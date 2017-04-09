from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.base import TemplateResponseMixin

from lbworkflow.models import Process

from .mixin import ProcessFormsView
from .helper import user_wf_info_as_dict


class ProcessTemplateResponseMixin(TemplateResponseMixin):

    def get_template_names(self):
        try:
            return super(CreateView, self).get_template_names()
        except ImproperlyConfigured:
            base_tmpl = self.base_template_name
            templates = ["%s/%s" % (self.wf_code, base_tmpl,), ]
            _meta = None
            if self.object:
                _meta = self.object._meta
            elif self.model_class:
                _meta = self.model_class._meta
            if _meta:
                app_label = _meta.app_label
                object_name = _meta.object_name.lower()
                templates.extend([
                    "%s/%s/%s" % (app_label, object_name, base_tmpl,),
                    "%s/%s" % (app_label, base_tmpl,), ])
            return templates


class CreateView(ProcessTemplateResponseMixin, ProcessFormsView):
    wf_code = None
    model_class = None
    base_template_name = 'form.html'

    def get_success_url(self):
        return reverse('wf_detail', pk=self.object.pinstance.pk)

    def get_context_data(self, **kwargs):
        kwargs['wf_code'] = self.wf_code
        kwargs['process'] = get_object_or_404(Process, code=self.wf_code)
        return kwargs

    def forms_valid(self, **forms):
        form = forms.pop('main_form')
        self.object = form.save_new_process(self.request, self.wf_code)
        return HttpResponseRedirect(self.get_success_url())


class UpdateView(ProcessTemplateResponseMixin, ProcessFormsView):
    wf_code = None
    model_class = None
    base_template_name = 'form.html'

    def get_success_url(self):
        return reverse('wf_detail', pk=self.object.pinstance.pk)

    def get_context_data(self, **kwargs):
        kwargs.update(user_wf_info_as_dict(self.object, self.request.user))
        return kwargs

    def forms_valid(self, **forms):
        form = forms.pop('main_form')
        self.object = form.update_process(self.request, self.wf_code)
        return HttpResponseRedirect(self.get_success_url())
