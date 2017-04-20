from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView

from lbworkflow.core.exceptions import HttpResponseException
from lbworkflow.core.transition import TransitionExecutor
from lbworkflow.forms import BackToActivityForm
from lbworkflow.forms import BatchWorkFlowForm
from lbworkflow.forms import WorkFlowForm
from lbworkflow.models import Activity
from lbworkflow.models import ProcessInstance
from lbworkflow.models import Transition
from lbworkflow.models import WorkItem

from .helper import import_wf_views
from .helper import add_processed_message
from .mixin import FormsView


class ExecuteTransitionView(TemplateResponseMixin, FormsView):
    """
    request.GET:
        ts_id: transition pk
        wi_id: work item pk
        pid: process instance pk (not used)
    """
    form_classes = {
        'form': WorkFlowForm
    }

    def get_success_url(self):
        return reverse("wf_todo")

    def get_template_names(self):
        try:
            return super(ExecuteTransitionView, self).get_template_names()
        except ImproperlyConfigured:
            base_tmpl = 'lbworkflow/do_transition_form.html'
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

    def raise_no_permission_exception(self, instance):
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

    def has_permission(self, request, instance, workitem, transition):
        activity_is_ok = (
            transition.input_activity == instance.cur_activity
            and workitem.activity == instance.cur_activity
            and workitem.status == 'in progress')
        user_is_ok = (
            request.user in [workitem.user, workitem.agent_user]
            or instance.is_wf_admin(request.user))
        is_ok = activity_is_ok and user_is_ok
        return is_ok

    def check_permission(self, request):
        """ If no permission raise HttpResponseException """
        if not self.has_permission(request, self.process_instance, self.workitem, self.transition):
            self.raise_no_permission_exception(self.process_instance)

    def get_transition_before_execute(self, cleaned_data):
        return self.transition

    def do_transition(self, cleaned_data):
        comment = cleaned_data.get('comment')
        attachments = cleaned_data.get('attachments')

        user = self.request.user
        instance = self.process_instance
        transition = self.get_transition_before_execute(cleaned_data)

        TransitionExecutor(user, instance, self.workitem, transition, comment, attachments).execute()

    def add_processed_message(self, process_instance, act_descn='Processed'):
        add_processed_message(self.request, process_instance, act_descn)

    def save_form(self, form):
        return form.save()

    def forms_valid(self, **forms):
        form = forms.pop('form')
        if isinstance(form, ModelForm):
            wf_obj = self.save_form(form)
            # update cache for wf_obj
            self.wf_obj = wf_obj
            self.process_instance = wf_obj.pinstance
        self.do_transition(form.cleaned_data)
        self.add_processed_message(self.process_instance)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs = super(ExecuteTransitionView, self).get_context_data(**kwargs)
        kwargs['workitem'] = self.workitem
        kwargs['transition'] = self.transition
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        try:
            self.init_process_data(request)
            self.check_permission(request)
            return super(ExecuteTransitionView, self).dispatch(request, *args, **kwargs)
        except HttpResponseException as error:
            return error.http_response


class BatchExecuteTransitionView(FormView):
    template_name = 'lbworkflow/batch_transition_form.html'
    form_class = BatchWorkFlowForm

    def get_success_url(self):
        return reverse("wf_todo")

    def get_context_data(self, **kwargs):
        kwargs['workitem_list'] = self.workitem_list
        return super(BatchExecuteTransitionView, self).get_context_data(**kwargs)

    def get_transition(self, process_instance):
        pass

    def add_processed_message(self, process_instance, act_descn='Processed'):
        add_processed_message(self.request, process_instance, act_descn)

    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        for workitem in self.workitem_list:
            if workitem.user != user:
                # TODO message for ignore
                continue
            instance = workitem.instance
            transition = self.get_transition(workitem.instance)
            comment = cleaned_data.get('comment')
            attachments = cleaned_data.get('attachments')
            TransitionExecutor(
                user, instance, workitem, transition, comment, attachments
            ).execute()
            self.add_processed_message(instance)
        return HttpResponseRedirect(self.get_success_url())

    def get_workitem_list(self, request):
        workitem_pk_list = request.POST.getlist('wi')
        workitem_pk_list = [e for e in workitem_pk_list if e]
        workitem_list = WorkItem.objects.filter(status='in progress', pk__in=workitem_pk_list)
        return workitem_list

    def dispatch(self, request, *args, **kwargs):
        self.workitem_list = self.get_workitem_list(request)
        return super(BatchExecuteTransitionView, self).dispatch(request, *args, **kwargs)


class ExecuteBackToTransitionView(ExecuteTransitionView):
    form_classes = {
        'form': BackToActivityForm
    }

    def has_permission(self, request, instance, workitem, transition):
        # TODO ...
        return True

    def get_form_kwargs(self, form_class_key):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ExecuteBackToTransitionView, self).get_form_kwargs(form_class_key)
        kwargs['process_instance'] = self.process_instance
        return kwargs

    def get_init_transition(self, process_instance, request):
        return process_instance.get_back_to_transition()

    def get_transition_before_execute(self, cleaned_data):
        back_to_activity = cleaned_data.get('back_to_activity')
        transition = self.transition
        transition.output_activity = Activity.objects.get(pk=back_to_activity)
        return transition


class ExecuteGiveUpTransitionView(ExecuteTransitionView):

    def get_success_url(self):
        return reverse("wf_my_wf")

    def has_permission(self, request, instance, workitem, transition):
        return instance.can_give_up(request.user)

    def get_init_transition(self, process_instance, request):
        return process_instance.get_give_up_transition()


class BatchExecuteGiveUpTransitionView(BatchExecuteTransitionView):

    def get_success_url(self):
        return reverse("wf_my_wf")

    def get_workitem_list(self, request):
        instance_pk_list = request.POST.getlist('pi')
        instance_list = ProcessInstance.objects.filter(
            cur_activity__status='in progress',
            pk__in=instance_pk_list)
        workitem_list = []
        for instance in instance_list:
            workitem = WorkItem(
                instance=instance,
                activity=instance.cur_activity,
                user=instance.created_by,
            )
            workitem_list.append(workitem)
        return workitem_list

    def get_transition(self, process_instance):
        return process_instance.get_give_up_transition()


class ExecuteAgreeTransitionView(ExecuteTransitionView):
    def get_init_transition(self, process_instance, request):
        return process_instance.get_agree_transition(False)

    def get_transition_before_execute(self, cleaned_data):
        return self.process_instance.get_agree_transition(False)


class BatchExecuteAgreeTransitionView(BatchExecuteTransitionView):
    def get_transition(self, process_instance):
        return process_instance.get_agree_transition(False)


class ExecuteRejectTransitionView(ExecuteTransitionView):

    def get_init_transition(self, process_instance, request):
        return process_instance.get_reject_transition()


class BatchExecuteRejectTransitionView(BatchExecuteTransitionView):
    def get_transition(self, process_instance):
        return process_instance.get_reject_transition()


# TODO Rollback


def execute_transitions(request, wf_code, trans_func):
    views = import_wf_views(wf_code, 'wf_views')
    # TODO check permission
    # TODO get transition and check if this transition can call this function
    func = getattr(views, trans_func)
    return func(request)
