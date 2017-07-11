from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.base import View
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from lbutils import do_filter
from lbutils import simple_export2xlsx

from lbworkflow.forms import BSQuickSearchForm
from lbworkflow.forms import BSQuickSearchWithExportForm
from lbworkflow.models import Process

from .helper import get_base_wf_permit_query_param
from .helper import user_wf_info_as_dict
from .mixin import FormsView


class WorkflowTemplateResponseMixin(TemplateResponseMixin):
    def get_template_names(self):
        try:
            return super(WorkflowTemplateResponseMixin, self).get_template_names()
        except ImproperlyConfigured:
            base_tmpl = self.base_template_name
            templates = ["%s/%s" % (self.wf_code, base_tmpl,), ]
            _meta = None
            object = getattr(self, 'object', None)
            if object:
                _meta = self.object._meta
            elif self.model:
                _meta = self.model._meta
            if _meta:
                app_label = _meta.app_label
                object_name = _meta.object_name.lower()
                templates.extend([
                    "%s/%s/%s" % (app_label, object_name, base_tmpl,),
                    "%s/%s" % (app_label, base_tmpl,), ])
            return templates


class ExcelResponseMixin(object):
    excel_titles = []
    excel_file_name = 'flow'

    def get_excel_data(self, o):
        return []

    def get_formated_excel_data(self, o):
        data = []
        for d in self.get_excel_data(o):
            # TODO date
            d = "%s" % d
            data.append(d)
        return data

    def render_to_excel(self, object_list, **kwargs):
        return simple_export2xlsx(
            self.excel_file_name, self.excel_titles,
            object_list, lambda o: self.get_formated_excel_data(o))


class CreateView(WorkflowTemplateResponseMixin, FormsView):
    form_classes = {
        # 'form': None,  # the form for BaseWFObj should named as form
    }
    wf_code = None
    model = None
    base_template_name = 'form.html'

    def get_success_url(self):
        return reverse('wf_detail', args=(self.object.pinstance.pk, ))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['wf_code'] = self.wf_code
        kwargs['process'] = get_object_or_404(Process, code=self.wf_code)
        return kwargs

    def forms_valid(self, **forms):
        form = forms.pop('form')
        self.object = form.save_new_process(self.request, self.wf_code)
        # TODO refactor, you may update total amount base items
        for form in forms.values():
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, wf_code, *args, **kwargs):
        self.request = request
        self.wf_code = wf_code
        return super(CreateView, self).dispatch(request, *args, **kwargs)


class UpdateView(WorkflowTemplateResponseMixin, FormsView):
    form_classes = {
        # 'form': None,  # the form for BaseWFObj should named as form
    }
    wf_code = None
    model = None
    base_template_name = 'form.html'

    def get_success_url(self):
        return reverse('wf_detail', args=(self.object.pinstance.pk, ))

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update(user_wf_info_as_dict(self.object, self.request.user))
        return kwargs

    def forms_valid(self, **forms):
        form = forms.pop('form')
        self.object = form.update_process(self.request)
        # TODO refactor
        for form in forms.values():
            form.save()
        return HttpResponseRedirect(self.get_success_url())

    def dispatch(self, request, wf_object, *args, **kwargs):
        self.request = request
        self.object = wf_object
        return super(UpdateView, self).dispatch(request, *args, **kwargs)


class BaseListView(ExcelResponseMixin, MultipleObjectMixin, View):
    search_form_class = BSQuickSearchForm
    quick_query_fields = []
    int_quick_query_fields = []
    ordering = '-pk'
    base_template_name = 'list.html'

    def dispatch(self, request, *args, wf_code=None, **kwargs):
        self.request = request
        self.wf_code = wf_code
        return super(BaseListView, self).dispatch(request, *args, **kwargs)

    def get_quick_query_fields(self):
        return self.quick_query_fields

    def get_base_queryset(self):
        return self.queryset

    def do_filter(self, queryset, query_data):
        quick_query_fields = self.get_quick_query_fields()
        return do_filter(queryset, query_data, quick_query_fields, self.int_quick_query_fields)

    def get_search_form(self, request):
        if not self.search_form_class:
            return None
        search_form = self.search_form_class(request.GET)
        if not search_form.is_valid():
            pass
        return search_form

    def get(self, request, *args, **kwargs):
        search_form = self.get_search_form(request)
        self.queryset = self.get_base_queryset()
        queryset = self.get_queryset()
        self.object_list = self.do_filter(
            queryset,
            search_form.cleaned_data if search_form else {})

        if 'export' in request.GET:
            return self.render_to_excel(self.object_list)

        process = None
        if self.wf_code:
            process = get_object_or_404(Process, code=self.wf_code)
        context = self.get_context_data(
            search_form=search_form, process=process)
        return self.render_to_response(context)


class ListView(MultipleObjectTemplateResponseMixin, BaseListView):
    pass


class WFListView(WorkflowTemplateResponseMixin, BaseListView):
    search_form_class = BSQuickSearchWithExportForm
    model = None
    wf_code = None

    def get_quick_query_fields(self):
        fields = [
            'pinstance__no',
            'pinstance__summary',
            'pinstance__created_by__username',
            'pinstance__cur_node__name',
        ]
        fields.extend(self.quick_query_fields)
        return fields

    def get_permit_query_param(self, user, q_param):
        # override this function to add addition permit
        return q_param

    def get_base_queryset(self):
        # only show have permission
        user = self.request.user
        qs = self.model.objects.all()
        if self.wf_code:
            qs = qs.filter(pinstance__process__code=self.wf_code)
        if not user.is_superuser:
            return qs
        q_param = get_base_wf_permit_query_param(user)
        q_param = self.get_permit_query_param(user, q_param)
        qs = qs.filter(q_param).distinct()
        return qs
