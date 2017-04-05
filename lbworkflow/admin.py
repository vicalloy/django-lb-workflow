from django.contrib import admin

from .models import (
    Activity, App, Authorization, Event, Process, ProcessCategory, ProcessInstance, ProcessReportLink, Transition,
    WorkItem,
)


class ProcessCategoryAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', 'oid', 'is_active')


class ProcessReportLinkAdmin(admin.ModelAdmin):
    search_fields = ('category__name', 'name', 'url')
    list_display = ('name', 'url', 'category', 'perm', 'oid', 'is_active')
    list_filter = ('category',)


class ProcessAdmin(admin.ModelAdmin):
    search_fields = ('code', 'prefix', 'name', 'category__name')
    list_display = ('code', 'prefix', 'name', 'category', 'oid', 'is_active')
    list_filter = ('category',)


class ActivityAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code', 'name', 'code',
        'operators', 'notice_users', 'share_users')
    list_display = (
        'process', 'name', 'code', 'step', 'status', 'audit_page_type',
        'can_edit', 'can_reject', 'can_give_up',
        'operators', 'notice_users', 'share_users',
        'is_active')
    list_filter = ('process',)


class TransitionAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code',
        'input_activity__name', 'output_activity__name',
        'name', 'condition')
    list_display = (
        'process', 'name', 'code', 'routing_rule',
        'input_activity', 'output_activity',
        'is_agree', 'can_auto_agree',
        'app', 'app_param', 'condition',
        'oid', 'is_active')
    list_filter = ('process',)


class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'app_type', 'action')


class ProcessInstanceAdmin(admin.ModelAdmin):
    search_fields = (
        'process__name', 'process__code',
        'created_by__username', 'cur_activity__name')
    list_display = (
        'process', 'no', 'summary', 'created_by', 'created_on',
        'cur_activity')
    list_filter = ('process', )
    raw_id_fields = (
        'content_type', 'created_by', 'attachments', 'can_view_users',
        'cur_activity')


class WorkItemAdmin(admin.ModelAdmin):
    search_fields = (
        'instance__no', 'activity__name', 'user__username',
        'agent__username')
    list_display = (
        'instance', 'activity', 'user', 'agent_user', 'is_hold', 'status',
        'created_on', 'receive_on')
    list_filter = ('instance__process', )
    raw_id_fields = ('instance', 'activity', 'user', 'agent_user', 'authorization', )


class EventAdmin(admin.ModelAdmin):
    search_fields = (
        'instance__no', 'user__username', 'old_activity__name',
        'new_activity__name', )
    list_display = (
        'instance', 'user', 'get_act_name', 'old_activity',
        'new_activity', 'created_on')
    raw_id_fields = (
        'instance', 'user', 'workitem', 'next_operators',
        'notice_users')


class AuthorizationAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'agent_user__username')
    list_display = ('user', 'agent_user', 'start_on', 'end_on')
    raw_id_fields = ('user', 'agent_user')


admin.site.register(ProcessCategory, ProcessCategoryAdmin)
admin.site.register(Process, ProcessAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Transition, TransitionAdmin)
admin.site.register(App, AppAdmin)
admin.site.register(ProcessInstance, ProcessInstanceAdmin)
admin.site.register(WorkItem, WorkItemAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Authorization, AuthorizationAdmin)
admin.site.register(ProcessReportLink, ProcessReportLinkAdmin)
