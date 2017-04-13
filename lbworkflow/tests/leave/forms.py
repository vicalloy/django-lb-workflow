# -*- coding: utf-8 -*-
from django import forms

from lbworkflow.forms import WorkflowFormMixin
from lbutils import BootstrapFormHelperMixin

from .models import Leave


class LeaveForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super(LeaveForm, self).__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            ['start_on', 'end_on'],
            ['leave_days', ''],
            ['reason', ],
        ])

    class Meta:
        model = Leave
        fields = ['start_on', 'end_on', 'leave_days', 'reason', ]
