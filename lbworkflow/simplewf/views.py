from lbworkflow.views.generics import CreateView
from lbworkflow.views.generics import UpdateView
from lbworkflow.views.generics import WFListView

from .forms import SimpleWorkFlowForm
from .models import SimpleWorkFlow


class SimpleWorkFlowCreateView(CreateView):
    form_classes = {
        'form': SimpleWorkFlowForm,
    }


new = SimpleWorkFlowCreateView.as_view()


class SimpleWorkFlowUpdateView(UpdateView):
    form_classes = {
        'form': SimpleWorkFlowForm,
    }


edit = SimpleWorkFlowUpdateView.as_view()


class SimpleWorkFlowListView(WFListView):
    wf_code = 'simplewf'
    model = SimpleWorkFlow
    excel_file_name = 'simplewf'
    excel_titles = [
        'Created on', 'Created by',
        'Summary', 'Content',
        'Status',
    ]

    def get_excel_data(self, o):
        return [
            o.created_by.username, o.created_on,
            o.summary, o.content,
            o.pinstance.cur_node.name,
        ]


show_list = SimpleWorkFlowListView.as_view()
