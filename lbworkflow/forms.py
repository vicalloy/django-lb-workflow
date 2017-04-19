from django import forms
from django.contrib import messages
from lbattachment.models import LBAttachment
from lbutils import BootstrapFormHelperMixin
from lbutils import JustSelectedSelectMultiple

from lbworkflow.models import Event
from lbworkflow.models import WorkItem

try:
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout
    from crispy_forms.bootstrap import StrictButton
except ImportError:
    pass


class BSSearchFormMixin(object):
    def init_form_helper(self):
        self.add_class2fields('input-sm')
        self.helper = helper = FormHelper()
        helper.form_class = 'form-inline'
        helper.form_method = 'get'
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
        )


class QuickSearchFormMixin(object):
    q_quick_search_kw = forms.CharField(label="关键字", required=False)


class BSQuickSearchForm(BootstrapFormHelperMixin, BSSearchFormMixin, QuickSearchFormMixin, forms.Form):
    def __init__(self, *args, **kw):
        super(BSQuickSearchForm, self).__init__(*args, **kw)
        self.init_crispy_helper()


class WorkflowFormMixin(object):
    def save_new_process(self, request, wf_code):
        submit = request.POST.get('act_submit')
        act_name = request.POST.get('act_submit') or 'Save'
        obj = self.save(commit=False)
        obj.created_by = request.user
        obj.create_pinstance(wf_code, submit)
        self.save_m2m()
        # Other action
        messages.info(request, '成功%s: %s' % (act_name, obj, ))
        return obj

    def update_process(self, request):
        submit = request.POST.get('act_submit')
        act_name = request.POST.get('act_submit') or 'Save'
        obj = self.save()
        # add a edit event, change resolution to draft
        instance = obj.pinstance
        if instance.cur_activity.status in ['rejected', 'draft']:
            WorkItem.objects.filter(instance=instance, status='running').delete()
            Event.objects.create(
                instance=instance, old_activity=instance.cur_activity,
                new_activity=instance.process.get_draft_active(),
                act_type='edit', user=request.user,
            )
            instance.cur_activity = instance.process.get_draft_active()
            instance.save()
        can_resubmit = instance.cur_activity.status in ['draft']
        # Other action
        if submit and can_resubmit:
            obj.submit_process(request.user)
        messages.info(request, 'Submitted %s: %s' % (act_name, obj, ))
        return obj


class WorkFlowForm(forms.Form):
    attachments = forms.ModelMultipleChoiceField(
        label='Attachment',
        queryset=LBAttachment.objects.all(),
        help_text='',
        widget=JustSelectedSelectMultiple(attrs={'class': 'nochosen'}),
        required=False,
    )
    comment = forms.CharField(
        label='Comment', required=False,
        widget=forms.Textarea())

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(WorkFlowForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self.instance

    def save_m2m(self, *args, **kwargs):
        return self.instance


class BatchWorkFlowForm(WorkFlowForm):
    pass


class BackToActivityForm(WorkFlowForm):
    back_to_activity = forms.ChoiceField(label='Back to', required=True)

    def __init__(self, process_instance, *args, **kwargs):
        super(BackToActivityForm, self).__init__(*args, **kwargs)
        choices = [(e.pk, e.name) for e in process_instance.get_can_back_to_activities()]
        self.fields['back_to_activity'].choices = choices
