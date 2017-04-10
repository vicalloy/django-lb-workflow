from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponseRedirect
from django.views.generic.base import ContextMixin
from django.views.generic.base import View


class FormsMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle any number of form in a request.
    """

    initial = {}
    form_classes = None
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

    def create_forms(self, **form_classes):
        """
        Returns an instance of the forms to be used in this view.
        forms can be access by self.forms
        """
        forms = {}
        self.forms = forms
        for form_class_key, form_class in form_classes.items():
            forms[form_class_key] = form_class(**self.get_form_kwargs(form_class_key))
        return forms

    def get_form_kwargs(self, form_class_key):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {'initial': self.get_initial(form_class_key)}
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


class ModelFormsMixin(object):

    def get_form_kwargs(self, form_class_key):
        kwargs = super().get_form_kwargs(form_class_key)
        instance = getattr(self, 'object', None)
        main_form = self.forms.get('main_form')
        if main_form:
            kwargs['instance'] = main_form.instance
        kwargs['instance'] = instance
        return kwargs


class FormsView(FormsMixin, View):
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
