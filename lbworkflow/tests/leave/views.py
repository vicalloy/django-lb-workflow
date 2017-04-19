from lbworkflow.forms import BSQuickSearchForm
from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import LeaveForm


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
    search_form_class = BSQuickSearchForm


show_list = LeaveListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {'for_test': 'from leave.detail'}
