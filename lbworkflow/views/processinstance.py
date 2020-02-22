from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from lbutils import as_callable

from lbworkflow import settings
from lbworkflow.models import Process
from lbworkflow.models import ProcessCategory
from lbworkflow.models import ProcessInstance

from .helper import get_wf_template_names
from .helper import import_wf_views
from .helper import user_wf_info_as_dict

can_edit_wf = as_callable(settings.CAN_EDIT_WF_FUNC)
can_submit_wf = as_callable(settings.CAN_SUBMIT_WF_FUNC)
can_view_wf = as_callable(settings.CAN_VIEW_WF_FUNC)


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
    is_print = ext_ctx.get('is_print')
    if not template_name:
        base_template_name = 'detail.html'
        if is_print:
            base_template_name = 'print.html'
        template_name = get_wf_template_names(
            instance.process.code,
            base_template_name,
            wf_object=instance.content_object)
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

    if not is_print and instance.cur_node.can_edit \
            and instance.cur_node.audit_view_type == 'edit' \
            and ext_ctx['task'] and instance.cur_node.resolution == 'started':
        return redirect(reverse('wf_edit', args=[instance.pk]))
    detail_func = getattr(views, 'detail', _default_detail)
    ret = detail_func(request, instance, ext_ctx=ctx)
    if isinstance(ret, dict):
        ret.update(ctx)
        return _default_detail(request, instance, ret, template_name)
    return ret


def delete(request):
    pks = request.POST.getlist('pk') or request.GET.getlist('pk')
    instances = ProcessInstance.objects.filter(pk__in=pks)
    for instance in instances:
        # only workflow admin can delete
        if instance.is_wf_admin(request.user):
            instance.delete()
    messages.info(request, 'Deleted')
    return redirect(reverse('wf_list_wf'))


def start_wf(request):
    template_name = 'lbworkflow/start_wf.html'
    categories = ProcessCategory.objects.filter(
        is_active=True).order_by('oid')
    # only have perm's categories
    categories = [e for e in categories if e.get_can_apply_processes(request.user)]
    ctx = {
        'categories': categories,
    }
    return render(request, template_name, ctx)


def report_list(request):
    template_name = 'lbworkflow/report_list.html'
    categories = ProcessCategory.objects.filter(
        is_active=True).order_by('oid')
    categories = [e for e in categories]
    ctx = {
        'categories': categories,
    }
    return render(request, template_name, ctx)
