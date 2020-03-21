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

from lbworkflow import settings
from lbworkflow.forms import BSQuickSearchForm
from lbworkflow.forms import BSQuickSearchWithExportForm
from lbworkflow.models import Process

from .forms import FormsView
from .helper import get_base_wf_permit_query_param
from .helper import get_wf_template_names
from .helper import user_wf_info_as_dict


class WorkflowTemplateResponseMixin(TemplateResponseMixin):
    def get_template_names(self):
        try:
            return super().get_template_names()
        except ImproperlyConfigured:
            return get_wf_template_names(
                self.wf_code,
                self.base_template_name,
                wf_object=getattr(self, 'object', None),
                model=getattr(self, 'model', None))


class ExcelResponseMixin:
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
        self.wf_code = wf_code
        return super().dispatch(request, *args, **kwargs)


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
        self.object = wf_object
        self.wf_code = wf_object.pinstance.process.code
        return super().dispatch(request, *args, **kwargs)


class BaseListView(ExcelResponseMixin, MultipleObjectMixin, View):
    paginate_by = settings.WF_PAGE_SIZE
    search_form_class = BSQuickSearchForm
    quick_query_fields = []
    int_quick_query_fields = []
    ordering = '-pk'
    base_template_name = 'list.html'

    def dispatch(self, request, *args, wf_code=None, **kwargs):
        self.wf_code = wf_code
        return super().dispatch(request, *args, **kwargs)

    def get_quick_query_fields(self):
        return self.quick_query_fields

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

    def get_queryset(self):
        qs = super().get_queryset()
        # only show have permission
        user = self.request.user
        if self.wf_code:
            qs = qs.filter(pinstance__process__code=self.wf_code)
        if not user.is_superuser:
            return qs
        q_param = get_base_wf_permit_query_param(user)
        q_param = self.get_permit_query_param(user, q_param)
        qs = qs.filter(q_param).distinct()
        return qs
