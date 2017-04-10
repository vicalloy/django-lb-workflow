from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import ListView
from lbworkflow.views.generics import UpdateView

from .forms import LeaveForm


class LeaveCreateView(CreateView):
    form_classes = {
        'main_form': LeaveForm,
    }

new = LeaveCreateView.as_view()


class LeaveUpdateView(UpdateView):
    form_classes = {
        'main_form': LeaveForm,
    }

edit = LeaveUpdateView.as_view()


class LeaveListView(ListView):
    pass

show_list = LeaveListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {'for_test': 'from leave.detail'}
