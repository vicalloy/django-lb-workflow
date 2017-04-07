from django.http import HttpResponse


def new(request, *args, **kwargs):
    return HttpResponse('todo')


def edit(request, pk, *args, **kwargs):
    return HttpResponse('todo')


def show_list(request, *args, **kwargs):
    return HttpResponse('todo')


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {'for_test': 'from leave.detail'}
