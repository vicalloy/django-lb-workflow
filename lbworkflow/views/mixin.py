from django.core.exceptions import ImproperlyConfigured
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin
from django.views.generic.base import View

try:
    from crispy_forms.helper import FormHelper
except ImportError:
    pass


__all__ = ('FormsMixin', 'ModelFormsMixin', 'FormSetMixin', 'FormsView', 'BSFormSetMixin')


class FormsMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle any number of form in a request.
    """

    initial = {}
    form_classes = None  # the main form should named as form
    success_url = None

    def get_initial(self, form_class_key):
        return self.initial.get(form_class_key, {}).copy()

    def get_form_classes(self):
        """
        Returns the form classes to use in this view
        """
        if not self.form_classes:
            raise ImproperlyConfigured("Provide form_classes.")
        return self.form_classes

    def after_create_form(self, form_class_key, form):
        return form

    def create_form(self, form_class_key, form_class):
        form = form_class(**self.get_form_kwargs(form_class_key, form_class))
        self.after_create_form(form_class_key, form)
        return form

    def create_forms(self, **form_classes):
        """
        Returns an instance of the forms to be used in this view.
        forms can be access by self.forms
        """
        forms = {}
        self.forms = forms
        for form_class_key, form_class in form_classes.items():
            forms[form_class_key] = self.create_form(form_class_key, form_class)
        return forms

    def get_form_kwargs(self, form_class_key, form_class):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial(form_class_key)}
        if form_class_key != 'form':
            kwargs['prefix'] = form_class_key
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = self.success_url
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url.")
        return url

    def forms_valid(self, **forms):
        """
        If the forms are valid, redirect to the supplied URL.
        """
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, **forms):
        """
        If the forms are invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(**forms))


class ModelFormsMixin:

    def get_form_kwargs(self, form_class_key, form_class):
        kwargs = super().get_form_kwargs(form_class_key, form_class)
        # not (ModelForm or ModelFormSet)
        formset_form_class = getattr(form_class, 'form', str)
        if not issubclass(form_class, ModelForm) \
                and not issubclass(formset_form_class, ModelForm):
            return kwargs
        instance = getattr(self, 'object', None)
        # if have main form, try to get instance from main form
        # other form may have ForeignKey to main object
        form = self.forms.get('form')
        if form and getattr(form, 'instance', None):
            instance = getattr(form, 'instance', None)
        kwargs['instance'] = instance
        return kwargs


def is_formset(form):
    # form class
    if getattr(form, '__name__', '').endswith('FormSet'):
        return True
    # form instance
    return type(form).__name__.endswith('FormSet')


class FormSetMixin:

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        formset_list = []
        for form in self.forms.values():
            if is_formset(form):
                formset_list.append(form)
        kwargs['formset_list'] = formset_list
        return kwargs

    def after_create_formset(self, form_class_key, formset):
        formset.title = "Items"

    def after_create_form(self, form_class_key, form):
        super().after_create_form(form_class_key, form)
        if is_formset(form):
            self.after_create_formset(form_class_key, form)
        return form

    def get_formset_kwargs(self, form_class_key, form_class):
        return {}

    def get_form_kwargs(self, form_class_key, form_class):
        kwargs = super().get_form_kwargs(form_class_key, form_class)
        if is_formset(form_class):
            return kwargs
        ext_kwargs = self.get_formset_kwargs(form_class_key, form_class)
        kwargs.update(ext_kwargs)
        return kwargs


class FormsView(FormSetMixin, ModelFormsMixin, FormsMixin, View):
    """
    A mixin that renders any number of forms on GET and processes it on POST.
    """
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates a blank version of the forms.
        """
        form_classes = self.get_form_classes()
        forms = self.create_forms(**form_classes)
        return self.render_to_response(self.get_context_data(**forms))

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form_classes = self.get_form_classes()
        forms = self.create_forms(**form_classes)
        if all([forms[form].is_valid() for form in forms]):
            return self.forms_valid(**forms)
        else:
            return self.forms_invalid(**forms)

    # PUT is a valid HTTP verb for creating (with a known URL) or editing an
    # object, note that browsers only support POST for now.
    def put(self, *args, **kwargs):
        return self.post(*args, **kwargs)


class BSFormSetMixin:
    """
    Crispy & Bootstrap for formset
    """
    def after_create_formset(self, form_class_key, formset):
        super().after_create_formset(form_class_key, formset)
        helper = FormHelper()
        helper.template = 'lbadminlte/bootstrap3/table_inline_formset.html'
        formset.helper = helper
        return formset
