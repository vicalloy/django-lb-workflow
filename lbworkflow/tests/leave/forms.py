# -*- coding: utf-8 -*-
from django import forms

from lbworkflow.forms import WorkflowFormMixin

from .models import Leave


class LeaveForm(WorkflowFormMixin, forms.ModelForm):
    class Meta:
        model = Leave
        exclude = []
