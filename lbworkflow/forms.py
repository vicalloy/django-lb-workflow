from django import forms
from lbattachment.models import LBAttachment
from lbutils import JustSelectedSelectMultiple


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


class BackToActivityForm(WorkFlowForm):
    back_to_activity = forms.ChoiceField(label='Back to', required=True)

    def __init__(self, process_instance, *args, **kwargs):
        super(BackToActivityForm, self).__init__(*args, **kwargs)
        choices = [(e.pk, e.name) for e in process_instance.get_can_back_to_activities()]
        self.fields['back_to_activity'].choices = choices
