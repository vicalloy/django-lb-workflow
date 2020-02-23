from django.conf import settings as django_settings

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

GET_USER_DISPLAY_NAME_FUNC = getattr(
    django_settings, 'LBWF_GET_USER_DISPLAY_NAME_FUNC',
    lambda user: "%s" % user)

CAN_EDIT_WF_FUNC = getattr(
    django_settings, 'LBWF_CAN_EDIT_WF_FUNC',
    lambda *args, **kwargs: True)

CAN_SUBMIT_WF_FUNC = getattr(
    django_settings, 'LBWF_CAN_SUBMIT_WF_FUNC',
    lambda *args, **kwargs: True)

CAN_VIEW_WF_FUNC = getattr(
    django_settings, 'LBWF_CAN_VIEW_WF_FUNC',
    lambda *args, **kwargs: True)

DEBUG_WORKFLOW = getattr(django_settings, 'LBWF_DEBUG_WORKFLOW', False)
WF_APPS = getattr(django_settings, 'LBWF_APPS', {})

PROCESS_INSTANCE_GET_PERMIT_QUERY_PARAM_FUNC = getattr(
    django_settings, 'LBWF_PROCESS_INSTANCE_GET_PERMIT_QUERY_PARAM_FUNC',
    lambda user, query_param: query_param)

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
