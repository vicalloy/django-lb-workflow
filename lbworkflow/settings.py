from django.conf import settings as django_settings
from django.utils.module_loading import import_string


def perform_import(val):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_string(val)
    elif isinstance(val, (list, tuple)):
        return [import_string(item) for item in val]
    return val


AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

USER_PARSER = getattr(
    django_settings, 'LBWF_USER_PARSER',
    'lbworkflow.core.userparser.SimpleUserParser')

WF_PAGE_SIZE = getattr(django_settings, 'LBWF_PAGE_SIZE', 20)

EVAL_FUNCS = getattr(django_settings, 'LBWF_EVAL_FUNCS', {})

WF_SEND_MSG_FUNCS = getattr(
    django_settings,
    'LBWF_WF_SEND_MSG_FUNCS',
    ['lbworkflow.core.sendmsg.wf_print', ],
)

DEFAULT_PERMISSION_CLASSES = getattr(
    django_settings, 'LBWF_DEFAULT_PERMISSION_CLASSES', []
)
DEFAULT_NEW_WF_PERMISSION_CLASSES = getattr(
    django_settings, 'LBWF_DEFAULT_NEW_PERMISSION_CLASSES', []
)
DEFAULT_EDIT_WF_PERMISSION_CLASSES = getattr(
    django_settings, 'LBWF_DEFAULT_EDIT_PERMISSION_CLASSES',
    ['lbworkflow.views.permissions.DefaultEditWorkFlowPermission']
)
DEFAULT_DETAIL_WF_PERMISSION_CLASSES = getattr(
    django_settings, 'LBWF_DEFAULT_DETAIL_PERMISSION_CLASSES',
    ['lbworkflow.views.permissions.DefaultDetailWorkFlowPermission']
)

GET_USER_DISPLAY_NAME_FUNC = getattr(
    django_settings, 'LBWF_GET_USER_DISPLAY_NAME_FUNC',
    lambda user: "%s" % user)

DEBUG_WORKFLOW = getattr(django_settings, 'LBWF_DEBUG_WORKFLOW', False)
WF_APPS = getattr(django_settings, 'LBWF_APPS', {})

QUICK_SEARCH_FORM = getattr(
    django_settings, 'LBWF_QUICK_SEARCH_FORM',
    'lbworkflow.forms.BSQuickSearchForm')

QUICK_SEARCH_WITH_EXPORT_FORM = getattr(
    django_settings, 'LBWF_QUICK_SEARCH_WITH_EXPORT_FORM',
    'lbworkflow.forms.BSQuickSearchWithExportForm')

WORK_FLOW_FORM = getattr(
    django_settings, 'LBWF_WORK_FLOW_FORM',
    'lbworkflow.forms.BSWorkFlowForm')

BATCH_WORK_FLOW_FORM = getattr(
    django_settings, 'LBWF_BATCH_WORK_FLOW_FORM',
    'lbworkflow.forms.BSBatchWorkFlowForm')

BACK_TO_ACTIVITY_FORM = getattr(
    django_settings, 'LBWF_BACK_TO_ACTIVITY_FORM',
    'lbworkflow.forms.BSBackToNodeForm')

ADD_ASSIGNEE_FORM = getattr(
    django_settings, 'LBWF_ADD_ASSIGNEE_FORM',
    'lbworkflow.forms.BSAddAssigneeForm')
