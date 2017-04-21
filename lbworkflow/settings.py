from django.conf import settings as django_settings

AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

USER_PARSER = getattr(
    django_settings, 'LBWF_USER_PARSER',
    'lbworkflow.core.userparser.SimpleUserParser')

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
