=======
Example
=======

.. _`example`:

Throughout this tutorial, we’ll walk you through the creation of a basic project and a issue process using default template.

Sample project
--------------

You can find sample code of using ``django-lb-workflow`` in ``testproject/`` and ``lbworkflow/tests/``.

Start a new project and config it
---------------------------------

Install ``django-lb-workflow`` with all option requires::

    pip install --upgrade django-lb-workflow[options]

Creating a project::

    $ django-admin.py startproject helloword

Creating ``helloword/middleware.py`` to compatible stronghold to django 1.10+::

    from django.utils.deprecation import MiddlewareMixin
    from stronghold.middleware import LoginRequiredMiddleware


    class LoginRequiredStrongholdMiddleware(MiddlewareMixin, LoginRequiredMiddleware):
        pass

Add the following code in the file ``settings.py``::

    INSTALLED_APPS = [
        ...
        'helloword',

        'crispy_forms',
        'lbattachment',
        'lbadminlte',
        'lbutils',
        'compressor',
        'djangobower',
        'el_pagination',

        'stronghold',

        'lbworkflow',
    ]

    MIDDLEWARE += [
        'testproject.middleware.LoginRequiredStrongholdMiddleware',
    ]

    CRISPY_TEMPLATE_PACK = 'bootstrap3'

    LBWF_APPS = {
    }

    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]

    # bower
    STATICFILES_FINDERS += (('djangobower.finders.BowerFinder'),)
    BOWER_COMPONENTS_ROOT = BASE_DIR

    BOWER_INSTALLED_APPS = (
        'admin-lte#2.3.11',
        'font-awesome#4.7.0',
        'ionicons#2.0.1',

        'modernizr',
        # POLYFILLS: javascript fallback solutions for older browsers.
        # CSS3 selectors for IE 6-8.
        'selectivizr',
        # min/max width media queries for IE 6-8.
        'respond',
        # CSS3 styles for IE 6-8.
        'pie',
        # HTML5 tag support for IE 6-8.
        'html5shiv',

        'masonry#4.1.1',
        'blueimp-file-upload#9.12.5',
        'flatpickr-calendar#2.5.6',
    )

    # django-compressor
    STATICFILES_FINDERS += (('compressor.finders.CompressorFinder'),)
    COMPRESS_PRECOMPILERS = (
        ('text/coffeescript', 'coffee --compile --stdio'),
        ('text/less', 'lessc {infile} {outfile}'),
        ('text/x-sass', 'sass {infile} {outfile}'),
        ('text/x-scss', 'sass --scss {infile} {outfile}'),
    )

    PROJECT_TITLE = 'LB-Workflow'

    LOGIN_URL = '/admin/login/'
    LOGOUT_URL = '/admin/logout/'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL_ = '/media/'
    MEDIA_URL = MEDIA_URL_

    STATIC_ROOT = os.path.join(BASE_DIR, 'collectedstatic')

    STRONGHOLD_PUBLIC_URLS = [
        r'^/admin/',
    ]

Edit the file urls.py::

    from django.conf.urls import include
    from django.conf.urls import url
    from django.contrib import admin
    from django.views.generic import RedirectView

    urlpatterns = [
        url(r'^$', RedirectView.as_view(url='/wf/list/'), name='home'),
        url(r'^admin/', admin.site.urls),
        url(r'^wf/', include('lbworkflow.urls')),
        url(r'^attachment/', include('lbattachment.urls')),
    ]

Create base templates for project.

``helloword/templates/base.html``::

    {% extends "lbadminlte/base.html" %}

    {% load staticfiles %}

    {% block head_ext %}
      <link href="{% static '/css/lbworkflow.css' %}" rel="stylesheet" type="text/css" />
    {% endblock %}

    {% block footer_ext %}
      <script src="{% static 'js/lbworkflow.js' %}" type="text/javascript"></script>
      <script type="text/javascript">
        URL_UPLOAD_ATTACH = "{% url 'lbattachment_upload__' %}";
      </script>
    {% endblock %}

``helloword/templates/base_ext.html``::

    {% extends "lbadminlte/base_ext.html" %}

    {% block left_side %}
      <section class="sidebar">
        <ul class="sidebar-menu">
          <li id="id-nav-todo">
            <a href="{% url 'wf_todo' %}">
              <i class="fa fa-th"></i> Todo
              <small class="badge pull-right bg-red todo-count hide"></small>
            </a>
          </li>
          <li id="id-nav-mywf">
            <a href="{% url 'wf_my_wf' %}">
              <i class="fa fa-th"></i> My
            </a>
          </li>
          <li id="id-nav-start-wf">
            <a href="{% url 'wf_start_wf' %}">
              <i class="fa fa-th"></i> Submit
            </a>
          </li>
          <li id="id-nav-list-wf">
            <a href="{% url 'wf_list_wf' %}">
              <i class="fa fa-th"></i> All
            </a>
          </li>
          <li id="id-nav-report-list">
            <a href="{% url 'wf_report_list' %}">
              <i class="fa fa-th"></i> Report list
            </a>
          </li>
        </ul>
      </section>
    {% endblock %}

``helloword/templates/base_form.html``::

    {% extends "lbadminlte/base_form.html" %}

Install required static package::

    $ cd helloword
    $ python manager bower install

run the following command to create database and create two superuser ``admin`` and ``vicalloy``::

    $ python manage.py migrate
    $ python manage.py createsuperuser
    $ python manage.py createsuperuser

Start the development server::

    $ python manage.py runserver

Now, open a Web browser and go to "/" on your local domain – e.g., http://127.0.0.1:8000/ .
You should see the admin’s login screen. After login you can see the home page of this project.

Start a new flow
----------------

Create app and generate base code
#################################

Creating the issue app::

    $ python manage.py startapp issue

Add ``issue`` to ``INSTALLED_APPS`` in ``settings.py``::

    INSTALLED_APPS = [
        ...
        'issue',
    ]

Creating models::

    from django.db import models

    from lbworkflow.models import BaseWFObj


    class Issue(BaseWFObj):
        title = models.CharField('Title', max_length=255)
        summary = models.CharField('Summary', max_length=255)
        content = models.TextField('Content', blank=True)

        def __str__(self):
            return self.title

``python manager.py shell`` to open django shell, and run the following code to generate flow code::

    >>> from lbworkflow.flowgen import FlowAppGenerator
    >>> from issue.models import Issue as wf_class
    >>> FlowAppGenerator().gen(wf_class)

run the following command to update database::

    $ python manage.py makemigrations issue
    $ python manage.py migrate

Config flow
###########

You can config flow in django admin or create a python file and execute it.
Config the flow by code ``issue/wfdata.py``::

    from lbworkflow.core.datahelper import create_node
    from lbworkflow.core.datahelper import create_category
    from lbworkflow.core.datahelper import create_process
    from lbworkflow.core.datahelper import create_transition


    def load_data():
        load_issue()


    def load_issue():
        """ load_[wf_code] """
        category = create_category('5f31d065-00cc-0020-beea-641f0a670010', 'HR')
        process = create_process('issue', 'Issue', category=category)
        create_node('5f31d065-00a0-0020-beea-641f0a670010', process, 'Draft', status='draft')
        create_node('5f31d065-00a0-0020-beea-641f0a670020', process, 'Given up', status='given up')
        create_node('5f31d065-00a0-0020-beea-641f0a670030', process, 'Rejected', status='rejected')
        create_node('5f31d065-00a0-0020-beea-641f0a670040', process, 'Completed', status='completed')
        create_node('5f31d065-00a0-0020-beea-641f0a670050', process, 'A1', operators='[vicalloy]')
        create_transition('5f31d065-00e0-0020-beea-641f0a670010', process, 'Draft,', 'A1')
        create_transition('5f31d065-00e0-0020-beea-641f0a670020', process, 'A1,', 'Completed')

Add the following code in the file settings.py::

    LBWF_APPS = {
        'issue': 'issue',
    }

run the following command to load flow config to database::

    $ python manage.py callfunc lbworkflow.wfdata.load_data
    $ python manage.py callfunc issue.wfdata.load_data

Submit and audit
----------------

Now we can start the server and submit a issue. We also can audit the issue.

Start the development server::

    $ python manage.py runserver

- Left menu
    - ``Todo`` All task need you todo
    - ``My`` All process you submitted
    - ``Submit`` Submit a new process
    - ``All`` You process that you can see
    - ``Report list`` Report list
