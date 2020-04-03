from django.contrib import admin

from .models import App
from .models import Authorization
from .models import Event
from .models import Node
from .models import Process
from .models import ProcessCategory
from .models import ProcessInstance
from .models import ProcessReportLink
from .models import Task
from .models import Transition


@admin.register(ProcessCategory)
class ProcessCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'oid', 'is_active')


@admin.register(ProcessReportLink)
class ProcessReportLinkAdmin(admin.ModelAdmin):
    search_fields = ('category__name', 'name', 'url')
    list_display = ('name', 'url', 'category', 'perm', 'oid', 'is_active')
    list_filter = ('category',)
    autocomplete_fields = ('category',)


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    search_fields = ('code', 'prefix', 'name', 'category__name')
    list_display = ('code', 'prefix', 'name', 'category', 'oid', 'is_active')
    list_filter = ('category',)
    autocomplete_fields = ('category',)


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code', 'name', 'code',
        'operators', 'notice_users', 'share_users')
    list_display = (
        'process', 'name', 'code', 'step', 'status', 'audit_page_type',
        'can_edit', 'can_reject', 'can_give_up',
        'operators', 'notice_users', 'share_users',
        'is_active')
    list_filter = ('process',)
    autocomplete_fields = ('process',)


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code',
        'input_node__name', 'output_node__name',
        'name', 'condition')
    list_display = (
        'process', 'name', 'code', 'routing_rule',
        'input_node', 'output_node',
        'is_agree', 'can_auto_agree',
        'app', 'app_param', 'condition',
        'oid', 'is_active')
    list_filter = ('process',)
    raw_id_fields = ('input_node', 'output_node', )
    autocomplete_fields = ('process',)


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'app_type', 'action')


@admin.register(ProcessInstance)
class ProcessInstanceAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code',
        'created_by__username', 'cur_node__name')
    list_display = (
        'process', 'no', 'summary', 'created_by', 'created_on',
        'cur_node')
    list_filter = ('process', )
    raw_id_fields = (
        'content_type', 'created_by', 'attachments', 'can_view_users',
        'cur_node')
    autocomplete_fields = ('process',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = (
        'instance__no', 'node__name', 'user__username',
        'agent__username')
    list_display = (
        'instance', 'node', 'user', 'agent_user', 'is_hold', 'status',
        'created_on', 'receive_on')
    list_filter = ('instance__process', )
    raw_id_fields = ('instance', 'node', 'user', 'agent_user', 'authorization', )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = (
        'instance__no', 'user__username', 'old_node__name',
        'new_node__name', )
    list_display = (
        'instance', 'user', 'get_act_name', 'old_node',
        'new_node', 'created_on')
    raw_id_fields = (
        'instance', 'user', 'task', 'next_operators',
        'notice_users', 'attachments', 'old_node', 'new_node')


def get_processes(o):
    return ', '.join(e.name for e in o.processes.all())


@admin.register(Authorization)
class AuthorizationAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'agent_user__username')
    list_display = ('user', 'agent_user', get_processes, 'start_on', 'end_on')
    raw_id_fields = ('user', 'agent_user')
    autocomplete_fields = ('processes', )
