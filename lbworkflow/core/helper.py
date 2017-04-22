import importlib

from django.db.models import Q

from lbworkflow import settings


def as_func(func_path):
    if callable(func_path):
        return func_path
    idx = func_path.rindex(r'.')
    _module = importlib.import_module(func_path[:idx])
    return getattr(_module, func_path[idx + 1:])


def as_class(cls_path):
    return as_func(cls_path)


def safe_eval(source, globals, *args, **kwargs):
    globals['Q'] = Q
    for s in settings.EVAL_FUNCS:
        globals[s[0]] = as_func(s[1])
    source = source.replace('import', '')
    return eval(source, globals, *args, **kwargs)
