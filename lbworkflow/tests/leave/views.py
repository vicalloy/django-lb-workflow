from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import LeaveForm
from .models import Leave


class LeaveCreateView(CreateView):
    form_classes = {
        'form': LeaveForm,
    }


new = LeaveCreateView.as_view()


class LeaveUpdateView(UpdateView):
    form_classes = {
        'form': LeaveForm,
    }


edit = LeaveUpdateView.as_view()


class LeaveListView(WFListView):
    model = Leave


show_list = LeaveListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {'for_test': 'from leave.detail'}
