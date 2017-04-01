import importlib

from django.db.models import Q

from lbworkflow import settings


def as_func(func):
    if callable(func):
        return func
    idx = func.rindex(r'.')
    _module = importlib.import_module(func[:idx])
    return getattr(_module, func[idx + 1:])


def safe_eval(source, globals, *args, **kwargs):
    globals['Q'] = Q
    for s in settings.EVAL_FUNCS:
        globals[s[0]] = as_func(s[1])
    source = source.replace('import', '')
    return eval(source, globals, *args, **kwargs)
