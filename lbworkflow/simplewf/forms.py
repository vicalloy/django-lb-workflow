from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import Layout
from django import forms
from lbutils import BootstrapFormHelperMixin

from lbworkflow.forms import BSQuickSearchForm
from lbworkflow.forms import WorkflowFormMixin

from .models import SimpleWorkFlow


class SearchForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class SimpleWorkFlowForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            ['summary', ],
            ['content', ],
        ])

    class Meta:
        model = SimpleWorkFlow
        fields = [
            'summary', 'content'
        ]
