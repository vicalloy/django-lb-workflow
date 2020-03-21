from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django_select2.forms import ModelSelect2MultipleWidget
from lbattachment.models import LBAttachment
from lbutils import BootstrapFormHelperMixin
from lbutils import JustSelectedSelectMultiple

from lbworkflow.models import Event
from lbworkflow.models import Task

User = get_user_model()

try:
    from crispy_forms.helper import FormHelper
    from crispy_forms.layout import Layout
    from crispy_forms.bootstrap import StrictButton
except ImportError:
    pass


class BSSearchFormMixin(BootstrapFormHelperMixin):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
        )

    def init_form_helper(self):
        self.add_class2fields('input-sm')
        self.helper = helper = FormHelper()
        helper.form_class = 'form-inline'
        helper.form_method = 'get'
        helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout()


class QuickSearchFormMixin(forms.Form):
    q_quick_search_kw = forms.CharField(label="Key word", required=False)


class BSQuickSearchForm(BSSearchFormMixin, QuickSearchFormMixin, forms.Form):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_form_helper()


class BSQuickSearchWithExportForm(BSQuickSearchForm):
    def layout(self):
        self.helper.layout = Layout(
            'q_quick_search_kw',
            StrictButton('Search', type="submit", css_class='btn-sm btn-default'),
            StrictButton('Export', type="submit", name="export", css_class='btn-sm btn-default'),
        )


class WorkflowFormMixin:
    def save_new_process(self, request, wf_code):
        submit = request.POST.get('act_submit')
        act_name = request.POST.get('act_submit') or 'Save'
        obj = self.save(commit=False)
        obj.created_by = request.user
        obj.create_pinstance(wf_code, submit)
        self.save_m2m()
        # Other action
        messages.info(request, 'Success %s: %s' % (act_name, obj, ))
        return obj

    def update_process(self, request):
        submit = request.POST.get('act_submit')
        act_name = request.POST.get('act_submit') or 'Save'
        obj = self.save()
        # add a edit event, change resolution to draft
        instance = obj.pinstance
        if instance.cur_node.status in ['rejected', 'draft']:
            Task.objects.filter(instance=instance, status='running').delete()
            Event.objects.create(
                instance=instance, old_node=instance.cur_node,
                new_node=instance.process.get_draft_active(),
                act_type='edit', user=request.user,
            )
            instance.cur_node = instance.process.get_draft_active()
            instance.save()
        can_resubmit = instance.cur_node.status in ['draft']
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
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self.instance

    def save_m2m(self, *args, **kwargs):
        return self.instance


class BSWorkFlowForm(BootstrapFormHelperMixin, WorkFlowForm):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper(label_class='col-md-2', field_class='col-md-8')
        self.layout_fields([
            ['attachments', ],
            ['comment', ],
        ])


class BatchWorkFlowForm(WorkFlowForm):
    pass


class BSBatchWorkFlowForm(BootstrapFormHelperMixin, BatchWorkFlowForm):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper(label_class='col-md-2', field_class='col-md-8')


class BackToNodeForm(WorkFlowForm):
    back_to_node = forms.ChoiceField(label='Back to', required=True)

    def __init__(self, process_instance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [(e.pk, e.name) for e in process_instance.get_can_back_to_activities()]
        self.fields['back_to_node'].choices = choices


class BSBackToNodeForm(BootstrapFormHelperMixin, BackToNodeForm):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper(label_class='col-md-2', field_class='col-md-8')
        self.layout_fields([
            ['back_to_node', ],
            ['attachments', ],
            ['comment', ],
        ])


class UserSelect2MultipleWidget(ModelSelect2MultipleWidget):
    search_fields = [
        'username__icontains',
    ]


class AddAssigneeForm(WorkFlowForm):
    assignees = forms.ModelMultipleChoiceField(
        label='Assignees', required=True,
        queryset=User.objects,
        widget=UserSelect2MultipleWidget
    )

    def __init__(self, *args, **kwargs):
        super(AddAssigneeForm, self).__init__(*args, **kwargs)
        self.init_crispy_helper()


class BSAddAssigneeForm(BootstrapFormHelperMixin, AddAssigneeForm):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.init_crispy_helper(label_class='col-md-2', field_class='col-md-8')
        self.layout_fields([
            ['assignees', ],
            ['attachments', ],
            ['comment', ],
        ])
