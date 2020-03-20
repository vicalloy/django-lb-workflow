from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.forms import ModelForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormView
from lbutils import as_callable
from lbutils import get_or_none

from lbworkflow import settings
from lbworkflow.core.exceptions import HttpResponseException
from lbworkflow.core.sendmsg import wf_send_msg
from lbworkflow.core.transition import TransitionExecutor
from lbworkflow.core.transition import create_event
from lbworkflow.models import Node
from lbworkflow.models import ProcessInstance
from lbworkflow.models import Task
from lbworkflow.models import Transition
from lbworkflow.settings import GET_USER_DISPLAY_NAME_FUNC

from .forms import FormsView
from .helper import add_processed_message
from .helper import import_wf_views
from .helper import user_wf_info_as_dict


class ExecuteTransitionView(TemplateResponseMixin, FormsView):
    """
    request.GET:
        ts_id: transition pk
        wi_id: work item pk
        pid: process instance pk (not used)
    """
    form_classes = {
        'form': as_callable(settings.WORK_FLOW_FORM)
    }

    def get_success_url(self):
        return reverse("wf_todo")

    def get_template_names(self):
        try:
            return super().get_template_names()
        except ImproperlyConfigured:
            base_tmpl = 'lbworkflow/do_transition_form.html'
            _meta = self.object._meta
            app_label = _meta.app_label
            object_name = _meta.object_name.lower()
            return ["%s/%s/%s" % (app_label, object_name, base_tmpl,),
                    "%s/%s" % (app_label, base_tmpl,),
                    base_tmpl]

    def get_init_transition(self, process_instance, request):
        ts_id = request.GET.get('ts_id')
        return Transition.objects.get(pk=ts_id)

    def get_task(self, request):
        # TODO admin may don't have task, need auto create a work item for admin
        wi_id = request.GET.get('wi_id')
        user = request.user
        return get_or_none(Task, Q(user=user) | Q(agent_user=user), id=wi_id)

    def init_process_data(self, request):
        task = self.get_task(request)
        if not task:
            self.raise_no_permission_exception()
        instance = task.instance

        self.transition = self.get_init_transition(instance, request)
        self.task = task
        self.process_instance = instance
        self.object = instance.content_object

    def raise_no_permission_exception(self, instance=None):
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
                {% if instance %}
                    <br/>
                    <a href="{% url 'wf_detail' instance.pk %}"> View this process </a>
                {% endif %}
            </body>
            </html>
            """)
        http_response = HttpResponse(
            t.render(Context({"instance": instance})), content_type='text/html', status=403)
        raise HttpResponseException(http_response)

    def has_permission(self, request, instance, task, transition):
        node_is_ok = (
            transition.input_node == instance.cur_node
            and task.node == instance.cur_node
            and task.status == 'in progress')
        user_is_ok = (
            request.user in [task.user, task.agent_user]
            or instance.is_wf_admin(request.user))
        is_ok = node_is_ok and user_is_ok
        return is_ok

    def check_permission(self, request):
        """ If no permission raise HttpResponseException """
        if not self.has_permission(request, self.process_instance, self.task, self.transition):
            self.raise_no_permission_exception(self.process_instance)

    def get_transition_before_execute(self, cleaned_data):
        return self.transition

    def do_transition(self, cleaned_data):
        comment = cleaned_data.get('comment')
        attachments = cleaned_data.get('attachments')

        user = self.request.user
        instance = self.process_instance
        transition = self.get_transition_before_execute(cleaned_data)

        TransitionExecutor(user, instance, self.task, transition, comment, attachments).execute()

    def add_processed_message(self, process_instance, act_descn='Processed'):
        add_processed_message(self.request, process_instance, act_descn)

    def save_form(self, form):
        return form.save()

    def forms_valid(self, **forms):
        form = forms.pop('form')
        if isinstance(form, ModelForm):
            wf_obj = self.save_form(form)
            # update cache for wf_obj
            self.object = wf_obj
            self.process_instance = wf_obj.pinstance
        for other_form in forms:
            self.save_form(other_form)
        self.do_transition(form.cleaned_data)
        self.add_processed_message(self.process_instance)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['task'] = self.task
        kwargs['transition'] = self.transition
        kwargs.update(user_wf_info_as_dict(self.object, self.request.user))
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        try:
            self.init_process_data(request)
            self.check_permission(request)
            return super().dispatch(request, *args, **kwargs)
        except HttpResponseException as error:
            return error.http_response


class BatchExecuteTransitionView(FormView):
    template_name = 'lbworkflow/batch_transition_form.html'
    form_class = as_callable(settings.BATCH_WORK_FLOW_FORM)

    def get_success_url(self):
        return reverse("wf_todo")

    def get_context_data(self, **kwargs):
        kwargs['task_list'] = self.task_list
        kwargs['transition_name'] = self.get_transition_name()
        return super().get_context_data(**kwargs)

    def get_transition_name(self):
        return 'Agree'

    def get_transition(self, process_instance):
        pass

    def add_processed_message(self, process_instance, act_descn='Processed'):
        add_processed_message(self.request, process_instance, act_descn)

    def post(self, request, *args, **kwargs):
        if not request.POST.get('do_submit'):
            return self.get(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        for task in self.task_list:
            if task.user != user:
                # TODO message for ignore
                continue
            instance = task.instance
            transition = self.get_transition(task.instance)
            comment = cleaned_data.get('comment')
            attachments = cleaned_data.get('attachments')
            TransitionExecutor(
                user, instance, task, transition, comment, attachments
            ).execute()
            self.add_processed_message(instance)
        return HttpResponseRedirect(self.get_success_url())

    def get_task_list(self, request):
        task_pk_list = request.POST.getlist('wi')
        task_pk_list = [e for e in task_pk_list if e]
        task_list = Task.objects.filter(status='in progress', pk__in=task_pk_list)
        return task_list

    def dispatch(self, request, *args, **kwargs):
        self.task_list = self.get_task_list(request)
        return super().dispatch(request, *args, **kwargs)


class ExecuteBackToTransitionView(ExecuteTransitionView):
    form_classes = {
        'form': as_callable(settings.BACK_TO_ACTIVITY_FORM)
    }

    def has_permission(self, request, instance, task, transition):
        # TODO ...
        return True

    def get_form_kwargs(self, form_class_key, form_class):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super().get_form_kwargs(form_class_key, form_class)
        kwargs['process_instance'] = self.process_instance
        return kwargs

    def get_init_transition(self, process_instance, request):
        return process_instance.get_back_to_transition()

    def get_transition_before_execute(self, cleaned_data):
        back_to_node = cleaned_data.get('back_to_node')
        transition = self.transition
        transition.output_node = Node.objects.get(pk=back_to_node)
        return transition


class ExecuteGiveUpTransitionView(ExecuteTransitionView):

    def get_success_url(self):
        return reverse("wf_my_wf")

    def get_task(self, request):
        pk = request.GET.get('pk')
        process_instance = get_or_none(ProcessInstance, pk=pk)
        if not process_instance:
            return None
        return process_instance.create_task(request.user)
        return Task(
            instance=process_instance,
            node=process_instance.cur_node,
            user=request.user)

    def has_permission(self, request, instance, task, transition):
        return instance.can_give_up(request.user)

    def get_init_transition(self, process_instance, request):
        return process_instance.get_give_up_transition()


class BatchExecuteGiveUpTransitionView(BatchExecuteTransitionView):

    def get_success_url(self):
        return reverse("wf_my_wf")

    def get_task_list(self, request):
        instance_pk_list = request.POST.getlist('pi')
        instance_list = ProcessInstance.objects.filter(
            cur_node__status='in progress',
            pk__in=instance_pk_list)
        task_list = []
        for instance in instance_list:
            task = Task(
                instance=instance,
                node=instance.cur_node,
                user=instance.created_by,
            )
            task_list.append(task)
        return task_list

    def get_transition_name(self):
        return 'Give up'

    def get_transition(self, process_instance):
        return process_instance.get_give_up_transition()


class ExecuteAgreeTransitionView(ExecuteTransitionView):
    def get_init_transition(self, process_instance, request):
        return process_instance.get_agree_transition(False)

    def get_transition_before_execute(self, cleaned_data):
        return self.process_instance.get_agree_transition(False)


class BatchExecuteAgreeTransitionView(BatchExecuteTransitionView):
    def get_transition_name(self):
        return 'Agree'

    def get_transition(self, process_instance):
        return process_instance.get_agree_transition(False)


class ExecuteRejectTransitionView(ExecuteTransitionView):
    def get_task(self, request):
        task = super().get_task(request)
        return task if task and task.node.can_reject else None

    def get_init_transition(self, process_instance, request):
        return process_instance.get_reject_transition()


class BatchExecuteRejectTransitionView(BatchExecuteTransitionView):
    def get_task_list(self, request):
        task_list = []
        for task in super().get_task_list(request):
            if task.node.can_reject:
                task_list.append(task)
            else:
                messages.info(
                    request,
                    """You can't reject process "%s" """ %
                    (
                        task.instance.no,
                    )
                )
        return task_list

    def get_transition_name(self):
        return 'Reject'

    def get_transition(self, process_instance):
        return process_instance.get_reject_transition()


# TODO Rollback


class AddAssigneeView(ExecuteTransitionView):
    form_classes = {
        'form': as_callable(settings.ADD_ASSIGNEE_FORM)
    }

    def get_form_kwargs(self, form_class_key, form_class):
        kwargs = super().get_form_kwargs(form_class_key, form_class)
        kwargs['instance'] = self.process_instance
        return kwargs

    def get_init_transition(self, process_instance, request):
        return process_instance.get_add_assignee_transition()

    def do_transition(self, cleaned_data):
        request = self.request
        transition = self.get_transition_before_execute(cleaned_data)
        comment = cleaned_data.get('comment')
        attachments = cleaned_data.get('attachments')
        user = request.user
        instance = self.process_instance
        assignees = cleaned_data.get('assignees', [])
        for assignee in assignees:
            instance.create_task(assignee, is_joint=True)
        msg = 'Add assignee %s.' % ', '.join([GET_USER_DISPLAY_NAME_FUNC(e) for e in assignees])
        messages.info(request, msg)
        comment = msg + '\n' + comment
        event = create_event(
            instance, transition,
            comment=comment, user=user,
            old_node=instance.cur_node, new_node=instance.cur_node)
        event.attachments.add(*attachments)
        wf_send_msg(assignees, 'new_workitem', event)


def execute_transitions(request, wf_code, trans_func):
    views = import_wf_views(wf_code, 'wf_views')
    # TODO check permission
    # TODO get transition and check if this transition can call this function
    func = getattr(views, trans_func)
    return func(request)
