from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateResponseMixin

from lbworkflow.core.exceptions import HttpResponseException
from lbworkflow.core.transition import TransitionExecutor
from lbworkflow.forms import BackToActivityForm
from lbworkflow.forms import WorkFlowForm
from lbworkflow.models import Activity
from lbworkflow.models import Transition
from lbworkflow.models import WorkItem

from .mixin import FormsMixin
from .mixin import ProcessFormsView


class ExecuteTransitionView(TemplateResponseMixin, FormsMixin, ProcessFormsView):
    """
    request.GET:
        ts_id: transition pk
        wi_id: work item pk
        pid: process instance pk (not used)
    """
    form_classes = {
        'main_form': WorkFlowForm
    }

    def get_template_names(self):
        try:
            return super(ExecuteTransitionView, self).get_template_names()
        except ImproperlyConfigured:
            base_tmpl = 'workflows/do_transition_form.html'
            _meta = self.wf_obj._meta
            app_label = _meta.app_label
            object_name = _meta.object_name.lower()
            return ["%s/%s/%s" % (app_label, object_name, base_tmpl,),
                    "%s/%s" % (app_label, base_tmpl,),
                    base_tmpl]

    def get_init_transition(self, process_instance, request):
        ts_id = request.GET.get('ts_id')
        return Transition.objects.get(pk=ts_id)

    def get_workitem(self, request):
        # TODO admin may don't have workitem, need auto create a work item for admin
        wi_id = request.GET.get('wi_id')
        return get_object_or_404(WorkItem, id=wi_id)

    def init_process_data(self, request):
        workitem = self.get_workitem(request)
        instance = workitem.instance

        self.transition = self.get_init_transition(instance, request)
        self.workitem = workitem
        self.process_instance = instance
        self.wf_obj = instance.content_object

    def check_permission(self, request, instance, workitem, transition):
        """ If no permission raise HttpResponseException """
        activity_is_ok = (
            transition.input == instance.cur_activity
            and workitem.activity == instance.cur_activity
            and workitem.status == 'in progress')
        user_is_ok = (
            request.user in [workitem.assign, workitem.agent_user]
            or instance.is_wf_admin(request.user))
        is_ok = activity_is_ok and user_is_ok

        if not is_ok:
            from django.template import Context, Template
            t = Template("""
            <!DOCTYPE HTML>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title></title>
            </head>
            <body>
                No permission to perform this action
                <br/>
                <a href="{% url 'wf_detail' instance.pk %}"> View this process </a>
            </body>
            </html>
            """)
            http_response = HttpResponse(
                t.render(Context({"instance": instance})), content_type='text/html', status=403)
            raise HttpResponseException(http_response)

    def get_transition_before_execute(self, cleaned_data):
        return self.transition

    def do_transition(self, cleaned_data):
        comment = cleaned_data.get('comment')
        attachments = cleaned_data.get('attachments')

        user = self.request.user
        instance = self.process_instance
        transition = self.get_transition_before_execute(cleaned_data)

        TransitionExecutor(user, instance, self.workitem, transition, comment, attachments).execute()

    def save_main_form(self, form):
        return form.save()

    def forms_valid(self, **forms):
        form = forms.pop('main_form')
        if isinstance(form, forms.ModelForm):
            wf_obj = self.save_main_form(form)
            # update cache for wf_obj
            self.wf_obj = wf_obj
            self.process_instance = wf_obj
            self.do_transition(form.cleaned_data)
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        try:
            self.init_process_data(request=request)
            super(ExecuteTransitionView, self).dispatch(request, *args, **kwargs)
        except HttpResponseException as error:
            return error.http_response


class ExecuteBackToTransitionView(ExecuteTransitionView):
    form_classes = {
        'main_form': BackToActivityForm
    }

    def get_init_transition(self, process_instance, request):
        return process_instance.get_reject_transition()

    def get_transition_before_execute(self, cleaned_data):
        back_to_activity = cleaned_data.get('back_to_activity')
        transition = self.transition
        transition.output_activity = Activity.objects.get(pk=back_to_activity)
        return transition


class ExecuteAgreeTransitionView(ExecuteTransitionView):
    def get_init_transition(self, process_instance, request):
        return process_instance.get_agree_transition(False)

    def get_transition_before_execute(self, cleaned_data):
        return self.process_instance.get_agree_transition(False)


class ExecuteRejectTransitionView(ExecuteTransitionView):
    form_classes = {
        'main_form': BackToActivityForm  # reason for reject.
    }

    def get_init_transition(self, process_instance, request):
        return process_instance.get_reject_transition()
