from django.conf import settings as django_settings

AUTH_USER_MODEL = getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

USER_PARSER = getattr(
    django_settings, 'LBWF_USER_PARSER',
    'lbworkflow.core.userparser.SimpleUserParser')

EVAL_FUNCS = getattr(django_settings, 'LBWF_EVAL_FUNCS', {})

GET_USER_DISPLAY_NAME_FUNC = getattr(
    django_settings, 'LBWF_GET_USER_DISPLAY_NAME_FUNC',
    lambda user: "%s" % user)

DEBUG_WORKFLOW = getattr(django_settings, 'WF_DEBUG_WORKFLOW', False)