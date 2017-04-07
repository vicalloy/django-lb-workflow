import datetime

from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from jsonfield import JSONField
from lbattachment.models import LBAttachment
from lbutils import get_or_none

from lbworkflow.settings import AUTH_USER_MODEL
from lbworkflow.settings import GET_USER_DISPLAY_NAME_FUNC

from .config import Activity
from .config import Process
from .config import Transition


class ProcessInstance(models.Model):
    no = models.CharField('NO.', max_length=100, blank=True)
    process = models.ForeignKey('lbworkflow.Process')
    created_by = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True, on_delete=models.SET_NULL,
        related_name='instances')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_on = models.DateTimeField(auto_now_add=True)
    submit_on = models.DateTimeField(null=True, blank=True)
    end_on = models.DateTimeField(null=True, blank=True)

    cur_activity = models.ForeignKey(
        Activity,
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

    def can_rollback(self, user):
        """ if can roll back, return last event """
        last_event = self.event_set.order_by('-created_on', '-pk').first()
        if not last_event:
            return None
        if last_event.new_activity == self.cur_activity \
                and self.cur_activity.status == 'in progress' \
                and last_event.old_activity.status == 'in progress' \
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
        if self.cur_activity.status != 'in progress':
            return False
        if not self.cur_activity.can_give_up:
            return False
        if self.is_wf_admin(user):
            return True
        if self.created_by == user:
            return True
        return False

    def get_operators(self):
        # TODO select_related
        qs = self.workitem_set.filter(status='in progress')
        users = []
        for e in qs:
            users.extend([e.user, e.agent_user])
        return [e for e in users if e]

    def get_operators_display(self):
        return ', '.join([GET_USER_DISPLAY_NAME_FUNC(e) for e in self.get_operators()])

    def get_reject_transition(self):
        return self.process.get_reject_transition(self.cur_activity)

    def get_back_to_transition(self, out_activity=None):
        return self.process.get_back_to_transition(self.cur_activity, out_activity)

    def get_common_agree_transition(self, out_activity=None):
        return self.process.get_common_agree_transition(self.cur_activity, out_activity)

    def get_rollback_transition(self, out_activity):
        return self.process.get_rollback_transition(self.cur_activity, out_activity)

    def get_give_up_transition(self):
        return self.process.get_give_up_transition(self.cur_activity)

    def create_workitem(self, operator):
        """ create workitem for submit/give up/rollback """
        return WorkItem.objects.create(
            instance=self,
            activity=self.cur_activity,
            user=operator,
        )

    def get_transitions(self, only_agree=False, only_can_auto_agree=False):
        qs = Transition.objects.filter(
            process=self.process, input_activity=self.cur_activity
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

    def get_todo_workitem(self, user=None):
        return self.get_todo_workitems(user).first()

    def get_todo_workitems(self, user=None):
        qs = WorkItem.objects.filter(
            instance=self, activity=self.cur_activity,
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
            if not event.act_type == 'transition':
                continue
            if not event.transition or not event.transition.is_agree:
                continue
            users.append(event.user)
        return user in users

    def get_can_back_to_activities(self):
        events = Event.objects.filter(instance=self).order_by('-date', '-id')
        activities = []
        for event in events:
            if event.old_activity == self.cur_activity:
                activities = []
                continue
            if event.old_activity.status not in ['in progress']:
                break
            if event.old_activity not in activities:
                activities.append(event.old_activity)
        return activities

    def add_processed_message(self, request, act_descn='Processed'):
        messages.info(
            request,
            'Process "%s" has been %s. Current status："%s" Current user："%s"' %
            (self.no, act_descn, self.cur_activity.name, self.get_operators_display())
        )

    def has_received(self):
        if self.cur_activity.status != 'in progress':
            return True
        return self.workitem_set.filter(status='in progress', receive_on__isnull=False).exists()

    def save(self, *args, **kwargs):
        super(ProcessInstance, self).save(*args, **kwargs)
        wf_obj = self.content_object
        if not self.no and wf_obj:  # self.no depend on pk(you should save to get pk)
            self.no = wf_obj.get_process_no()
            self.created_by = wf_obj.created_by
            self.summary = wf_obj.get_process_summary()
            super(ProcessInstance, self).save(force_update=True)


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

    def update_agent_for_workitem(self):
        WorkItem.objects.filter(
            authorization=self, status='in progress'
        ).update(agent_user=None)
        WorkItem.objects.filter(
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
        super(Authorization, self).save(*args, **kwargs)
        self.update_agent_for_workitem()


class WorkItem(models.Model):
    STATUS_CHOICES = (
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    instance = models.ForeignKey(ProcessInstance)
    activity = models.ForeignKey(Activity)
    user = models.ForeignKey(AUTH_USER_MODEL, verbose_name='User', null=True, blank=True)
    agent_user = models.ForeignKey(
        AUTH_USER_MODEL, verbose_name='Agent user',
        related_name='agent_user_workitems',
        null=True, blank=True)
    authorization = models.ForeignKey(
        Authorization, verbose_name='Authorization',
        blank=True, null=True, on_delete=models.SET_NULL,
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='in progress')
    receive_on = models.DateTimeField('Receive on', null=True, blank=True)
    is_hold = models.BooleanField('Is hold', default=False)

    created_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - %s - %s' % (self.instance.summary, self.activity.name, self.pk)

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


class Comment(models.Model):
    instance = models.ForeignKey(ProcessInstance)
    content = models.TextField()
    ext_data = JSONField(null=True, blank=True)
    attachments = models.ManyToManyField(
        LBAttachment, verbose_name='Attachment', blank=True)

    def __str__(self):
        return '%s - %s' % (self.instance.summary, self.comment)


class Event(models.Model):
    EVENT_ACT_CHOICES = (
        ('transition', 'Transition'),
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
    instance = models.ForeignKey(ProcessInstance)
    user = models.ForeignKey(AUTH_USER_MODEL)
    act_type = models.CharField(
        max_length=255, choices=EVENT_ACT_CHOICES,
        default='transition')
    old_activity = models.ForeignKey(
        Activity, related_name='out_events',
        null=True, blank=True)
    new_activity = models.ForeignKey(
        Activity, related_name='in_events',
        null=True, blank=True)
    workitem = models.ForeignKey(
        WorkItem, related_name='events',
        null=True, blank=True)
    transition = models.ForeignKey(
        Transition, blank=True,
        null=True, on_delete=models.SET_NULL)

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

    created_on = models.DateTimeField(auto_now=True)

    def get_act_name(self):
        if self.act_type == 'transition':
            return self.transition.name if self.transition else ''
        # TODO assign should show assign to who
        return self.get_act_type_display()

    def get_next_notice_users_display(self):
        if self.old_activity == self.new_activity:
            return ''
        return ', '.join([GET_USER_DISPLAY_NAME_FUNC(e) for e in self.notice_users.all()])

    def __str__(self):
        old_activity = self.old_activity.name if self.old_activity else ''
        new_activity = self.new_activity.name if self.new_activity else ''
        return '%s: %s - %s - %s' % (self.instance.summary, old_activity,
                                     self.get_act_name(), new_activity)


class BaseWFObj(models.Model):
    pinstance = models.ForeignKey(
        ProcessInstance, blank=True, null=True,
        related_name="%(class)s",
        verbose_name='Process instance')
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
        return self.pinstance.cur_activity.status

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
        pass

    def on_submit(self):
        pass

    def on_fail(self):
        pass

    def on_do_transition(self, cur_activity, to_activity):
        pass

    def get_absolute_url(self):
        return ''

    def save(self, *args, **kwargs):
        super(BaseWFObj, self).save(*args, **kwargs)
        instance = self.pinstance
        if instance:
            instance.summary = self.get_process_summary()
            instance.save()

    def create_pinstance(self, process, submit=False):
        created_by = self.created_by
        if not isinstance(process, Process):
            process = get_or_none(Process, code=process)
        if not self.pk:
            self.save()
        instance = ProcessInstance.objects.create(
            process=process, created_by=created_by, content_object=self,
            cur_activity=process.get_draft_active())
        self.pinstance = instance
        self.save()  # instance will save after self.save
        if submit:
            self.submit_process()
        return instance

    def submit_process(self, user=None):
        from lbworkflow.core.transition import TransitionExecutor

        instance = self.pinstance
        if instance.cur_activity.is_submitted():
            return
        user = user or self.created_by
        workitem = instance.create_workitem(user)
        transition = instance.get_transitions()[0]
        TransitionExecutor(user, instance, workitem, transition).execute()
