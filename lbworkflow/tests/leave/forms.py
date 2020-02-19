# -*- coding: utf-8 -*-
from django import forms
from lbutils import BootstrapFormHelperMixin

from lbworkflow.forms import WorkflowFormMixin

from .models import Leave


class LeaveForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper()
        self.layout_fields([
            ['start_on', 'end_on'],
            ['leave_days', None],
            ['reason', ],
        ])

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.init_actual_info()
        if commit:
            self.save_m2m()
            obj.save()
        return obj

    class Meta:
        model = Leave
        fields = ['start_on', 'end_on', 'leave_days', 'reason', ]


class HRForm(BootstrapFormHelperMixin, WorkflowFormMixin, forms.ModelForm):
    comment = forms.CharField(
        label='Comment', required=False,
        widget=forms.Textarea())

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper(label_class='col-md-2', field_class='col-md-8')
        self.layout_fields([
            ['actual_start_on', ],
            ['actual_end_on', ],
            ['actual_leave_days', ],
            ['comment', ],
        ])

    class Meta:
        model = Leave
        fields = ['actual_start_on', 'actual_end_on', 'actual_leave_days', ]
