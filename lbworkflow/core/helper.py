from django.db.models import Q
from lbutils import as_callable

from lbworkflow import settings


def safe_eval(source, globals, *args, **kwargs):
    globals['Q'] = Q
    for s in settings.EVAL_FUNCS:
        globals[s[0]] = as_callable(s[1])
    source = source.replace('import', '')
    return eval(source, globals, *args, **kwargs)
