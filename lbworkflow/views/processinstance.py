from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from lbworkflow.models import ProcessCategory, ProcessInstance

from .generics import DetailView
from .helper import import_wf_views


def new(request, wf_code):
    views = import_wf_views(wf_code)
    return views.new(request, wf_code=wf_code)


def show_list(request, wf_code):
    views = import_wf_views(wf_code)
    return views.show_list(request, wf_code=wf_code)


def edit(request, pk):
    instance = get_object_or_404(ProcessInstance, pk=pk)
    wf_code = instance.process.code
    views = import_wf_views(wf_code)
    return views.edit(request, instance.content_object)


def detail(request, pk, ext_ctx={}):
    instance = ProcessInstance.objects.get(pk=pk)
    views = import_wf_views(instance.process.code)
    is_print = ext_ctx.get("is_print")
    func_detail = getattr(views, "detail", DetailView.as_view())
    return func_detail(request, instance.content_object, is_print)


def delete(request):
    pks = request.POST.getlist("pk") or request.GET.getlist("pk")
    instances = ProcessInstance.objects.filter(pk__in=pks)
    for instance in instances:
        # only workflow admin can delete
        if instance.is_wf_admin(request.user):
            instance.delete()
    messages.info(request, "Deleted")
    return redirect(reverse("wf_list_wf"))


def start_wf(request):
    template_name = "lbworkflow/start_wf.html"
    categories = ProcessCategory.objects.filter(is_active=True).order_by("oid")
    # only have perm's categories
    categories = [
        e for e in categories if e.get_can_apply_processes(request.user)
    ]
    ctx = {
        "categories": categories,
    }
    return render(request, template_name, ctx)


def report_list(request):
    template_name = "lbworkflow/report_list.html"
    categories = ProcessCategory.objects.filter(is_active=True).order_by("oid")
    categories = [e for e in categories]
    ctx = {
        "categories": categories,
    }
    return render(request, template_name, ctx)
