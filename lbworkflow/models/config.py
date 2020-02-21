import uuid

from django.conf import settings as django_settings
from django.db import models
from django.template import Context
from django.template import Template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField
from lbutils import create_instance
from lbutils import get_or_none

from lbworkflow import settings
from lbworkflow.core.helper import safe_eval

AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')


class ProcessCategoryManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)


class ProcessCategory(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), max_length=255, db_index=True)

    oid = models.IntegerField(_('Order'), default=999)
    is_active = models.BooleanField(_('Is active'), default=True)

    objects = ProcessCategoryManager()

    class Meta:
        ordering = ["oid"]

    def __str__(self):
        return self.name

    def natural_key(self):
        return (
            self.uuid,
        )

    def get_can_apply_processes(self, user, force_fetch=False):
        processes = getattr(self, '__cache__can_apply_processes', None)
        if processes and not force_fetch:
            return processes
        return self.process_set.all()

    def get_report_links(self):
        return ProcessReportLink.objects.filter(category=self)

    def get_all_process(self):
        return self.process_set.order_by('oid')


class ProcessReportLinkManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)


class ProcessReportLink(models.Model):
    category = models.ForeignKey(
        ProcessCategory,
        blank=True, null=True,
        on_delete=models.SET_NULL, verbose_name='Category')
    name = models.CharField('Name', max_length=255)
    url = models.CharField('URL', max_length=255)
    open_in_new_window = models.BooleanField('Open in new window', default=False)
    perm = models.CharField(
        'Permission', max_length=255, blank=True,
        help_text="Permission to view this report")

    oid = models.IntegerField('Order', default=999)
    is_active = models.BooleanField('Is active', default=True)

    objects = ProcessReportLinkManager()

    class Meta:
        ordering = ["oid"]

    def __str__(self):
        return self.name

    def get_url(self):
        try:
            url_component_list = self.url.split(' ')
            return reverse(url_component_list[0], args=url_component_list[1:])
        except Exception:
            return self.url


class ProcessManager(models.Manager):
    def get_by_natural_key(self, code):
        return self.get(code=code)


class Process(models.Model):
    """
    A process holds the map that describes the flow of work.
    """
    code = models.CharField(
        'Code', max_length=100, unique=True,
        help_text='A unique code to identify process')
    prefix = models.CharField(
        'Prefix',
        max_length=8, default='', blank=True,
        help_text='prefix for process NO.')
    name = models.CharField(
        'Name', max_length=255,
        help_text='Name for this process')
    category = models.ForeignKey(
        ProcessCategory,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        verbose_name='Category')
    note = models.TextField('Note', blank=True)

    oid = models.IntegerField('Order', default=999)
    is_active = models.BooleanField('Is active', default=True)
    ext_data = JSONField(default="{}")

    objects = ProcessManager()

    class Meta:
        verbose_name = 'Process'
        ordering = ["oid"]
        permissions = (
            ("sft_mgr_process", "workflow - Config"),
        )

    def natural_key(self):
        return (
            self.code,
        )

    def __str__(self):
        return self.name

    def have_apply_perm(self, user):
        # TODO check permission
        return True

    def get_draft_active(self):
        return get_or_none(Node, process=self, status='draft')

    def get_rejected_active(self):
        return get_or_none(Node, process=self, status='rejected')

    def get_given_up_active(self):
        return get_or_none(Node, process=self, status='given up')

    def get_rollback_transition(self, in_node, out_node):
        transition = Transition(
            name='Rollback',
            code='rollback',
            process=self,
            is_agree=False,
            can_auto_agree=False,
            input_node=in_node,
            output_node=out_node,
        )
        return transition

    def get_give_up_transition(self, in_node):
        output = self.get_given_up_active()
        transition = Transition(
            name='Give up',
            code='give up',
            process=self,
            is_agree=False,
            can_auto_agree=False,
            input_node=in_node,
            output_node=output,
        )
        return transition

    def get_back_to_transition(self, in_node, out_node=None):
        transition = Transition(
            name='Back to',
            code='back to',
            process=self,
            is_agree=False,
            can_auto_agree=False,
            input_node=in_node,
            output_node=out_node,
        )
        return transition

    def get_reject_transition(self, in_node):
        transition = Transition(
            name='Reject',
            code='reject',
            process=self,
            is_agree=False,
            can_auto_agree=False,
            input_node=in_node,
            output_node=self.get_rejected_active(),
        )
        return transition

    def get_add_assignee_transition(self, in_node):
        transition = Transition(
            name='Add assignee',
            code='add assignee',
            process=self,
            is_agree=False,
            can_auto_agree=False,
            input_node=in_node,
            output_node=in_node,
        )
        return transition


class NodeManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)


class Node(models.Model):
    """
    Node is the states of an instance.
    """

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('given up', 'Given up'),
        ('rejected', 'Rejected'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    AUDIT_PAGE_TYPE_CHOICES = (
        ('view', 'view'),
        ('edit', 'Edit'),
    )
    TYPE_CHOICES = (
        ('node', 'Node'),
        ('router', 'Router'),
    )

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    process = models.ForeignKey(
        'Process',
        on_delete=models.CASCADE,
        verbose_name='Process')
    name = models.CharField('Name', max_length=255)
    code = models.CharField(
        'Code', max_length=255, blank=True)
    step = models.IntegerField(
        'Step', default=0,
        help_text="",
    )
    status = models.CharField(
        'Status', max_length=16,
        default='in progress', choices=STATUS_CHOICES)
    audit_page_type = models.CharField(
        'Audit page type', max_length=64,
        choices=AUDIT_PAGE_TYPE_CHOICES,
        help_text='If this node can edit, will auto goto edit mode when audit.',
        default='view')
    node_type = models.CharField(
        'Status', max_length=16,
        default='node', choices=TYPE_CHOICES)

    can_edit = models.BooleanField('Can edit', default=False)
    can_reject = models.BooleanField('Can reject', default=True)
    can_give_up = models.BooleanField('Can give up', default=True)

    operators = models.TextField('Audit users', blank=True)
    notice_users = models.TextField('Notice users', blank=True)
    share_users = models.TextField('Share users', blank=True)

    note = models.TextField('Note', blank=True)
    # if not audit after xx day send a remind

    is_active = models.BooleanField('Is active', default=True)
    ext_data = JSONField(default="{}")

    objects = NodeManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (
            self.uuid,
        )

    def is_submitted(self):
        return self.status in ['in progress', 'completed']

    def get_operators(self, owner, operator, instance=None):
        return create_instance(
            settings.USER_PARSER, self.operators, instance, operator, owner
        ).parse()

    def get_notice_users(self, owner, operator, instance=None):
        return create_instance(
            settings.USER_PARSER, self.notice_users, instance, operator, owner
        ).parse()

    def get_share_users(self, owner, operator, instance=None):
        return create_instance(
            settings.USER_PARSER, self.share_users, instance, operator, owner
        ).parse()

    def get_users(self, owner, operator, instance=None):
        operators = self.get_operators(owner, operator, instance)
        notice_users = self.get_notice_users(owner, operator, instance)
        share_users = self.get_share_users(owner, operator, instance)
        return operators, notice_users, share_users


class TransitionManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)


class Transition(models.Model):
    """
    A Transition connects two node: a From and a To activity.
    """
    ROUTING_RULE_CHOICES = (
        ('split', 'split'),
        ('joint', 'Joint'),
    )
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    process = models.ForeignKey(
        'Process',
        on_delete=models.CASCADE,
        verbose_name='Process'
    )
    name = models.CharField(
        'Name', max_length=100, default='Agree',
        help_text="It also the action's name, like: Agree/Submit")
    code = models.CharField(  # 'back to', 'rollback'
        'Code', max_length=100, blank=True,
    )
    is_agree = models.BooleanField(
        'Is agree',
        default=True,
        help_text='User only need agree one time in one workflow'
    )
    can_auto_agree = models.BooleanField(
        'If can auto agree',
        default=True,
        help_text='If user agreed in previous steps will auto agree',
    )
    routing_rule = models.CharField(
        'Routing rule', max_length=16,
        default='split',
        choices=ROUTING_RULE_CHOICES,
        help_text="joint: do transition after all work item finished. joint: do transition immediately")
    input_node = models.ForeignKey(
        Node, verbose_name='Input node',
        null=True, on_delete=models.SET_NULL,
        related_name='input_transitions',
        help_text='')
    output_node = models.ForeignKey(
        Node, verbose_name='Output node',
        null=True, on_delete=models.SET_NULL,
        related_name='output_transitions',
        help_text='')
    app = models.ForeignKey(
        'App', verbose_name='Application to perform',
        null=True, on_delete=models.SET_NULL,
        blank=True)
    app_param = models.CharField(
        max_length=100, verbose_name='Param for application',
        null=True, blank=True,
        help_text='Depend on App config')
    condition = models.TextField(
        'Condition', blank=True,
        help_text="Uses the Python syntax.ex: `o.leave_days>3`")  # eval(t.condition, {'o': obj})
    note = models.TextField('Note', blank=True)

    oid = models.IntegerField(
        'Order', default=999)
    is_active = models.BooleanField('Is active', default=True)
    ext_data = JSONField(default="{}")

    objects = TransitionManager()

    def __str__(self):
        return '%s - %s' % (self.process.name, self.name)

    def natural_key(self):
        return (
            self.uuid,
        )

    def is_match_condition(self, wf_obj):
        if not self.condition.strip():
            return True
        return safe_eval(self.condition, {'o': wf_obj})

    def get_condition_descn(self):
        return self.condition.split('#')[-1].strip()

    def as_simple_agree_transition(self):
        self.pk = None
        if not self.code:
            self.code = 'agree'

    def get_app_url(self, task):
        return self.app.get_url(task, self)


class AppManager(models.Manager):
    def get_by_natural_key(self, uuid):
        return self.get(uuid=uuid)


class App(models.Model):
    """
    An application is a python view that can be called by URL.
    """
    APP_TYPE_CHOICES = (
        ('url', 'URL'),
    )
    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text='Name')
    app_type = models.CharField('Type', max_length=255, choices=APP_TYPE_CHOICES, default='url')
    action = models.CharField(
        max_length=255, blank=True,
        help_text="URL: It can be url or django's url name. If it's blank will use transition's app param")
    note = models.TextField(blank=False)

    objects = AppManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (
            self.uuid,
        )

    def get_url(self, task, transition):
        def render(templ_str, ctx):
            return Template(templ_str).render(Context(ctx))
        ts_id = transition.pk or transition.code

        ctx = {
            "wi": task,
            "wf_code": transition.process.code,
            "ts": transition,
            "ts_id": ts_id,
            "in": task.instance,
            "o": task.instance.content_object,
        }

        url = 'wf_process'
        if self.action:
            url = self.action
        elif transition.app_param:
            url = transition.app_param
        try:
            url_component_list = url.split(' ')
            url_param = [render(e, ctx) for e in url_component_list[1:]]
            url = reverse(url_component_list[0], args=url_param)
        except Exception:
            pass
        if "?" not in url:
            url = "%s?a=" % url
        url = "%s&ts_id={{ts_id}}&wi_id={{wi.id}}" % url
        return render(url, ctx)
