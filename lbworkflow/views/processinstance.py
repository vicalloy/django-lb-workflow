# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

import importlib
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from lbworkflow import settings
from lbworkflow.core.helper import as_func
from lbworkflow.models import Process
from lbworkflow.models import ProcessInstance

from .helper import user_wf_info_as_dict

can_edit_wf = as_func(settings.CAN_EDIT_WF_FUNC)
can_submit_wf = as_func(settings.CAN_SUBMIT_WF_FUNC)
can_view_wf = as_func(settings.CAN_VIEW_WF_FUNC)


def import_wf_views(wf_code):
    wf_module = settings.WF_APPS.get(wf_code)
    return importlib.import_module('%s.views' % wf_module)


def new(request, wf_code):
    views = import_wf_views(wf_code)
    process = Process.objects.get(code=wf_code)
    if not can_submit_wf(process, request.user):
        raise PermissionDenied
    return views.new(request, wf_code=wf_code)


def show_list(request, wf_code):
    views = import_wf_views(wf_code)
    return views.show_list(request, wf_code=wf_code)


def edit(request, pk):
    instance = get_object_or_404(ProcessInstance, pk=pk)
    wf_code = instance.process.code
    views = import_wf_views(wf_code)
    if not can_edit_wf(instance, request.user):
        messages.info(request, 'No permission: %s' % instance)
        return redirect(reverse('wf_my_wf'))
    return views.edit(request, instance.content_object)


def _default_detail(request, instance, ext_ctx={}, template_name=None):
    if not template_name:
        template_name = '%s/detail.html' % instance.process.code
    ctx = {}
    ctx.update(ext_ctx)
    return render(request, template_name, ctx)


def detail(request, pk, template_name=None, ext_ctx={}):
    instance = ProcessInstance.objects.get(pk=pk)
    views = import_wf_views(instance.process.code)
    is_print = ext_ctx.get('is_print')
    __ext_param_process = getattr(views, '__ext_param_process', None)
    ctx = {}
    ctx.update(ext_ctx)

    if not can_view_wf(instance, request.user, ext_param_process=__ext_param_process):
        messages.info(request, 'No permission to view this process')
        return redirect(reverse('wf_my_wf'))

    user_wf_info = user_wf_info_as_dict(instance.content_object, request.user)
    ctx.update(user_wf_info)

    if not is_print and instance.cur_activity.can_edit \
            and instance.cur_activity.audit_view_type == 'edit' \
            and ext_ctx['workitem'] and instance.cur_activity.resolution == 'started':
        return redirect(reverse('wf_edit', args=[instance.pk]))
    detail_func = getattr(views, 'detail', _default_detail)
    ret = detail_func(request, instance, ext_ctx=ctx)
    if isinstance(ret, dict):
        ret.update(ctx)
        return _default_detail(request, instance, ret, template_name)
    return ret
