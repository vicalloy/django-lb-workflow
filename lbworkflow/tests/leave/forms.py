# -*- coding: utf-8 -*-
from django import forms

from lbworkflow.forms import WorkflowFormMixin
from lbutils import FormHelperMixin
from lbutils import row_div
from crispy_forms.layout import Layout

from .models import Leave


class LeaveForm(FormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(LeaveForm, self).__init__(*args, **kw)
        self.one_row_fields = ['reason', ]
        self.init_crispy_helper()
        self.helper.label_class = 'col-xs-4'
        self.helper.layout = Layout(
            row_div(['start_on', 'end_on'], 6),
            row_div(['leave_days', ], 6),
            row_div(['reason'], 12),
        )

    class Meta:
        model = Leave
        fields = ['start_on', 'end_on', 'leave_days', 'reason', ]
