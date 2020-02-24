from django.utils import timezone

from lbworkflow.models import Event
from lbworkflow.models import Task

from .sendmsg import wf_send_msg


def create_event(instance, transition, **kwargs):
    act_type = 'transition' if transition.pk else transition.code
    if transition.is_agree:
        act_type = 'agree'
    event = Event.objects.create(
        instance=instance, act_name=transition.name, act_type=act_type,
        **kwargs)
    return event


class TransitionExecutor(object):
    def __init__(
            self, operator, instance, task, transition=None,
            comment='', attachments=[]):
        self.wf_obj = instance.content_object
        self.instance = instance
        self.operator = operator
        self.task = task
        self.transition = transition

        self.comment = comment
        self.attachments = attachments

        self.from_node = instance.cur_node
        # hold&assign wouldn't change node
        self.to_node = transition.output_node
        self.all_todo_tasks = instance.get_todo_tasks()

        self.last_event = None

    def execute(self):
        # TODO check permission

        all_todo_tasks = self.all_todo_tasks
        need_transfer = False
        if self.transition.code in ['reject', 'back to', 'give up']:
            need_transfer = True
        elif self.transition.routing_rule == 'joint':
            if all_todo_tasks.count() == 1:
                need_transfer = True
        else:
            if not all_todo_tasks.exclude(pk=self.task.pk).filter(is_joint=True).exists():
                need_transfer = True
        self._complete_task(need_transfer)
        if not need_transfer:
            return

        self._do_transfer()

        # if is agree should check if need auto agree for next node
        if self.transition.is_agree or self.to_node.node_type == 'router':
            self._auto_agree_next_node()

    def _auto_agree_next_node(self):
        instance = self.instance

        agree_transition = instance.get_agree_transition()
        all_todo_tasks = instance.get_todo_tasks()

        if not agree_transition:
            return

        # if from router, create a task
        if self.to_node.node_type == 'router':
            task = Task(
                instance=self.instance,
                node=self.instance.cur_node,
                user=self.operator,
            )
            all_todo_tasks = [task]

        for task in all_todo_tasks:
            users = [task.user, task.agent_user]
            users = [e for e in users if e]
            for user in set(users):
                if self.instance.cur_node != task.node:  # has processed
                    return
                if instance.is_user_agreed(user):
                    TransitionExecutor(self.operator, instance, task, agree_transition).execute()

    def _complete_task(self, need_transfer):
        """ close workite, create event and return it """
        instance = self.instance
        task = self.task
        transition = self.transition

        task.status = 'completed'
        task.save()

        to_node = self.to_node if need_transfer else instance.cur_node
        self.to_node = to_node

        event = None
        pre_last_event = instance.last_event()
        if pre_last_event and pre_last_event.new_node.node_type == 'router':
            event = pre_last_event
            event.new_node = to_node
            event.save()

        if not event:
            event = create_event(
                instance, transition,
                comment=self.comment, user=self.operator,
                old_node=task.node, new_node=to_node,
                task=task)

        if self.attachments:
            event.attachments.add(*self.attachments)

        self.last_event = event

        return event

    def _do_transfer_for_instance(self):
        instance = self.instance
        wf_obj = self.wf_obj

        from_node = self.from_node
        from_status = from_node.status

        to_node = self.to_node
        to_status = self.to_node.status

        # Submit
        if not from_node.is_submitted() and to_node.is_submitted():
            instance.submit_time = timezone.now()
            wf_obj.on_submit()

        # cancel & give up & reject
        if from_node.is_submitted() and not to_node.is_submitted():
            wf_obj.on_fail()

        # complete
        if from_status != 'completed' and to_status == 'completed':
            instance.end_on = timezone.now()
            self.wf_obj.on_complete()

        # cancel complete
        if from_status == 'completed' and to_status != 'completed':
            instance.end_on = None

        instance.cur_node = self.to_node
        self.wf_obj.on_do_transition(from_node, to_node)

        instance.save()

    def _send_notification(self):
        instance = self.instance
        last_event = self.last_event

        notice_users = last_event.notice_users.exclude(
            pk__in=[self.operator.pk, instance.created_by.pk]).distinct()
        wf_send_msg(notice_users, 'notify', last_event)

        # send notification to instance.created_by
        if instance.created_by != self.operator:
            wf_send_msg([instance.created_by], 'transfered', last_event)

    def _gen_new_task(self):
        last_event = self.last_event

        if not last_event:
            return

        next_operators = last_event.next_operators.distinct()

        need_notify_operators = []
        for operator in next_operators:
            new_task = Task(
                instance=self.instance, node=self.to_node,
                user=operator)
            new_task.update_authorization(commit=True)

            # notify next operator(not include current operator and instance.created_by)
            if operator not in [self.operator, self.instance.created_by]:
                need_notify_operators.append(operator)

            agent_user = new_task.agent_user
            if agent_user and agent_user not in [self.operator, self.instance.created_by]:
                need_notify_operators.append(agent_user)

        wf_send_msg(need_notify_operators, 'new_task', last_event)

    def update_users_on_transfer(self):
        instance = self.instance
        event = self.last_event
        to_node = event.new_node

        next_operators = to_node.get_operators(instance.created_by, self.operator, instance)
        event.next_operators.add(*next_operators)
        notice_users = to_node.get_notice_users(instance.created_by, self.operator, instance)
        event.notice_users.add(*notice_users)
        can_view_users = to_node.get_share_users(instance.created_by, self.operator, instance)
        instance.can_view_users.add(*can_view_users)

    def _do_transfer(self):
        self.update_users_on_transfer()
        # auto complete all current work item
        self.all_todo_tasks.update(status='completed')
        self._do_transfer_for_instance()
        self._gen_new_task()
        self._send_notification()
