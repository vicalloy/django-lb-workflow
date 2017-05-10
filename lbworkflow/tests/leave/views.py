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
    wf_code = 'leave'
    model = Leave
    excel_file_name = 'leave'
    excel_titles = [
        'Created on', 'Created by',
        'Start on', 'End on', 'Leave days',
        'Actual start on', 'Actual start on', 'Actual leave days',
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.start_on, o.end_on, o.leave_days,
            o.actual_start_on, o.actual_end_on, o.actual_leave_days,
            o.pinstance.cur_node.name,
        ]


show_list = LeaveListView.as_view()


def detail(request, instance, ext_ctx, *args, **kwargs):
    return {'for_test': 'from leave.detail'}
