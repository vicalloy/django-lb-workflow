import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from lbattachment.models import LBAttachment
from lbutils import get_or_none

from lbworkflow.settings import AUTH_USER_MODEL
from lbworkflow.settings import GET_USER_DISPLAY_NAME_FUNC

from .config import Node
from .config import Process
from .config import Transition


class ProcessInstance(models.Model):
    """
    A process instance is created when someone decides to do something,
    and doing this thing means start using a process defined in ``django-lb-workflow``.
    """
    no = models.CharField('NO.', max_length=100, blank=True)
    process = models.ForeignKey(
        'lbworkflow.Process',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
        related_name='instances')

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_on = models.DateTimeField(auto_now_add=True)
    submit_on = models.DateTimeField(null=True, blank=True)
    end_on = models.DateTimeField(null=True, blank=True)

    cur_node = models.ForeignKey(
        Node,
        null=True, on_delete=models.SET_NULL
    )

    attachments = models.ManyToManyField(LBAttachment, blank=True)
    can_view_users = models.ManyToManyField(
        AUTH_USER_MODEL, blank=True,
        verbose_name='Can view users',
        related_name="can_view_pinstances")

    summary = models.TextField('Summary', blank=True)

    def __str__(self):
        return self.no

    def last_event(self):
        return self.event_set.order_by('-created_on', '-pk').first()

    def can_rollback(self, user):
        """ if can roll back, return last event """
        last_event = self.last_event()
        if not last_event:
            return None
        if last_event.new_node == self.cur_node \
                and self.cur_node.status == 'in progress' \
                and last_event.old_node.status == 'in progress' \
                and last_event.user == user \
                and last_event.act_type in ['reject', 'back to', 'transition', 'give up']:
            return last_event
        return None

    def is_wf_admin(self, user):
        # TODO permission
        return user.is_superuser

    def can_view(self, user, ext_param_process=None):
        # TODO permission
        return True

    def can_give_up(self, user):
        if self.cur_node.status != 'in progress':
            return False
        if not self.cur_node.can_give_up:
            return False
        if self.is_wf_admin(user):
            return True
        if self.created_by == user:
            return True
        return False

    def get_operators(self):
        # TODO select_related
        qs = self.task_set.filter(status='in progress')
        users = []
        for e in qs:
            users.extend([e.user, e.agent_user])
        return [e for e in users if e]

    def get_operators_display(self):
        return ', '.join([GET_USER_DISPLAY_NAME_FUNC(e) for e in self.get_operators()])

    def get_reject_transition(self):
        return self.process.get_reject_transition(self.cur_node)

    def get_back_to_transition(self, out_node=None):
        return self.process.get_back_to_transition(self.cur_node, out_node)

    def get_rollback_transition(self, out_node):
        return self.process.get_rollback_transition(self.cur_node, out_node)

    def get_give_up_transition(self):
        return self.process.get_give_up_transition(self.cur_node)

    def get_add_assignee_transition(self):
        return self.process.get_add_assignee_transition(self.cur_node)

    def create_task(self, operator, **kwargs):
        """ create task for submit/give up/rollback """
        return Task.objects.create(
            instance=self,
            node=self.cur_node,
            user=operator,
            **kwargs
        )

    def get_transitions(self, only_agree=False, only_can_auto_agree=False):
        qs = Transition.objects.filter(
            process=self.process, input_node=self.cur_node
        ).order_by('is_agree', 'oid', 'id')
        if only_agree:
            qs = qs.filter(is_agree=True)
        if only_can_auto_agree:
            qs = qs.filter(can_auto_agree=True)
        return [e for e in qs if e.is_match_condition(self.content_object)]

    def get_agree_transitions(self, only_can_auto_agree=True):
        return self.get_transitions(only_agree=True, only_can_auto_agree=only_can_auto_agree)

    def get_agree_transition(self, only_can_auto_agree=True):
        agree_transitions = self.get_agree_transitions(only_can_auto_agree)
        return agree_transitions[0] if agree_transitions else None

    def get_merged_agree_transitions(self):
        transitions = self.get_transitions(self)

        transition_names = [e.name for e in transitions]
        merged_transitions = []
        simple_agree_added = False

        for transition in transitions:
            if not transition.is_agree:
                merged_transitions.append(transition)
            elif len(transition_names) == 1:
                merged_transitions.append(transition)
            elif not simple_agree_added:  # use which transition depend on condition
                simple_agree_added = True
                merged_transitions.append(transition.as_simple_agree_transition())

        return merged_transitions

    def get_todo_task(self, user=None):
        return self.get_todo_tasks(user).first()

    def get_todo_tasks(self, user=None):
        qs = Task.objects.filter(
            instance=self, node=self.cur_node,
            status='in progress').filter(Q(agent_user=user) | Q(user=user))
        if user:
            qs = qs.filter(Q(agent_user=user) | Q(user=user))
        return qs

    def is_user_agreed(self, user):
        events = Event.objects.filter(instance=self).order_by('-created_on', '-id')
        users = []
        for event in events:
            if event.act_type in ['give up', 'reject', 'back to']:
                break
            if event.act_type != 'agree':
                continue
            users.append(event.user)
        return user in users

    def get_can_back_to_activities(self):
        events = Event.objects.filter(instance=self).order_by('-created_on', '-id')
        activities = []
        for event in events:
            if event.old_node == self.cur_node:
                activities = []
                continue
            if event.old_node.status not in ['in progress']:
                break
            if event.old_node not in activities:
                activities.append(event.old_node)
        return activities

    def has_received(self):
        if self.cur_node.status != 'in progress':
            return True
        return self.task_set.filter(status='in progress', receive_on__isnull=False).exists()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        wf_obj = self.content_object
        if not self.no and wf_obj:  # self.no depend on pk(you should save to get pk)
            self.no = wf_obj.get_process_no()
            self.created_by = wf_obj.created_by
            self.summary = wf_obj.get_process_summary()
            super().save(force_update=True)


class Authorization(models.Model):
    user = models.ForeignKey(
        AUTH_USER_MODEL, verbose_name='User',
        null=True, on_delete=models.SET_NULL,
        related_name='authorized_user_authorizations')
    agent_user = models.ForeignKey(
        AUTH_USER_MODEL, verbose_name='Agent user',
        null=True, on_delete=models.SET_NULL,
        related_name='agent_user_authorizations')
    processes = models.ManyToManyField(Process, verbose_name='Processes')
    start_on = models.DateField('Start on')
    end_on = models.DateField('End on')

    def __str__(self):
        return '%s %s %s %s' % (self.user, self.agent_user, self.start_on, self.end_on)

    def update_agent_for_task(self):
        Task.objects.filter(
            authorization=self, status='in progress'
        ).update(agent_user=None)
        Task.objects.filter(
            user=self.authorized_user, status='in progress',
            instance__process__in=self.processes.all(),
        ).update(agent_user=self.agent_user, authorization=self)

    def is_active(self):
        today = datetime.date.today()
        if self.start_on > today:
            return False
        if self.end_on < today:
            return False
        return True

    def save(self, *args, **kwargs):
        # TODO on delete
        super().save(*args, **kwargs)
        self.update_agent_for_task()


class Task(models.Model):
    """
    A task object represents a task you are performing.
    """
    STATUS_CHOICES = (
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    instance = models.ForeignKey(
        ProcessInstance,
        on_delete=models.CASCADE
    )
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL, verbose_name='User', null=True, blank=True,
        on_delete=models.SET_NULL
    )
    agent_user = models.ForeignKey(
        AUTH_USER_MODEL, verbose_name='Agent user',
        related_name='agent_user_tasks',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    authorization = models.ForeignKey(
        Authorization, verbose_name='Authorization',
        blank=True, null=True, on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='in progress')
    receive_on = models.DateTimeField('Receive on', null=True, blank=True)
    is_hold = models.BooleanField('Is hold', default=False)
    is_joint = models.BooleanField('Is joint', default=False)

    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s - %s - %s' % (self.instance.summary, self.node.name, self.pk)

    def update_authorization(self, commit=True):
        today = datetime.date.today()
        authorization = Authorization.objects.filter(
            processes=self.instance.process, user=self.user,
            start_on__lte=today, end_on__gte=today,
        ).first()

        self.agent_user = None
        if authorization:
            self.agent_user = authorization.agent_user

        if commit:
            self.save()


class Event(models.Model):
    """
    A task perform log.
    """
    EVENT_ACT_CHOICES = (
        ('transition', 'Transition'),
        ('agree', 'Agree'),
        ('edit', 'Edit'),
        ('give up', 'Give up'),
        ('reject', 'Reject'),
        ('back to', 'Back to'),
        ('rollback', 'Rollback'),
        ('comment', 'Comment'),
        ('assign', 'Assign'),  # assign another user to audit
        ('hold', 'Hold'),
        ('unhold', 'Unhold')
    )
    instance = models.ForeignKey(
        ProcessInstance,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    act_type = models.CharField(
        max_length=255, choices=EVENT_ACT_CHOICES,
        default='transition')
    act_name = models.CharField(
        max_length=255, blank=True)
    old_node = models.ForeignKey(
        Node, related_name='out_events',
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    new_node = models.ForeignKey(
        Node, related_name='in_events',
        null=True, blank=True,
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task, related_name='events',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    next_operators = models.ManyToManyField(
        AUTH_USER_MODEL, related_name='audit_events',
        blank=True)
    notice_users = models.ManyToManyField(
        AUTH_USER_MODEL, related_name='notice_events',
        blank=True)

    comment = models.TextField(blank=True, default='')
    attachments = models.ManyToManyField(
        LBAttachment, verbose_name='Attachment', blank=True)
    ext_data = JSONField(null=True, blank=True)

    created_on = models.DateTimeField(auto_now_add=True)

    def get_act_name(self):
        if self.act_type == 'transition':
            return self.act_name
        # TODO assign should show assign to who
        return self.get_act_type_display()

    def get_next_notice_users_display(self):
        if self.old_node == self.new_node:
            return ''
        return ', '.join([GET_USER_DISPLAY_NAME_FUNC(e) for e in self.notice_users.all()])

    def __str__(self):
        old_node = self.old_node.name if self.old_node else ''
        new_node = self.new_node.name if self.new_node else ''
        return '%s: %s - %s - %s' % (self.instance.summary, old_node,
                                     self.get_act_name(), new_node)


class BaseWFObj(models.Model):
    """
    A abstract class for flow model. Every flow model should inherit from it.
    """
    pinstance = models.ForeignKey(
        ProcessInstance, blank=True, null=True,
        related_name="%(class)s",
        verbose_name='Process instance',
        on_delete=models.CASCADE
    )
    created_on = models.DateTimeField('Created on', auto_now_add=True)
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
        verbose_name='Created by')

    class Meta:
        abstract = True

    def get_process_no(self):
        instance = self.pinstance
        if instance and instance.pk:
            return '%s%s' % (instance.process.prefix, instance.pk)
        return ''

    def get_status(self):
        return self.pinstance.cur_node.status

    def get_process_summary(self):
        return "%s" % self

    def update_process_summary(self, commit=True):
        pinstance = self.pinstance
        if not pinstance:
            return
        pinstance.summary = self.get_process_summary()
        if commit:
            pinstance.save()

    def on_complete(self):
        """ Will call when process complete """
        pass

    def on_submit(self):
        """ Will call when process submit """
        pass

    def on_fail(self):
        """ Will call when process fail(cancel/give up/reject)"""
        pass

    def on_do_transition(self, cur_node, to_node):
        """
        Will call when process node transfer
        """
        pass

    def get_absolute_url(self):
        return ''

    def save(self, *args, **kwargs):
        """
        update self.pinstance.summary on save.
        """
        super().save(*args, **kwargs)
        instance = self.pinstance
        if instance:
            instance.summary = self.get_process_summary()
            instance.save()

    def create_pinstance(self, process, submit=False):
        """
        Create and set self.pinstance for this model

        :param process: Which process to use
        :param submit: Whether auto submit it after create
        :return: The created process instance
        """
        created_by = self.created_by
        if not isinstance(process, Process):
            process = get_or_none(Process, code=process)
        if not self.pk:
            self.save()
        instance = ProcessInstance.objects.create(
            process=process, created_by=created_by, content_object=self,
            cur_node=process.get_draft_active())
        self.pinstance = instance
        self.save()  # instance will save after self.save
        if submit:
            self.submit_process()
        return instance

    def submit_process(self, user=None):
        """
        Submit this process.

        :param user: Which user submit the process. The user is self.created_by if user is None.
        """
        from lbworkflow.core.transition import TransitionExecutor

        instance = self.pinstance
        if instance.cur_node.is_submitted():
            return
        user = user or self.created_by
        task = instance.create_task(user)
        transition = instance.get_transitions()[0]
        TransitionExecutor(user, instance, task, transition).execute()
