=======
Example
=======

.. _`example`:

Throughout this tutorial, we’ll walk you through the creation of a basic project and a leave process using default template.

Sample project
--------------

You can find sample code of using ``django-lb-workflow`` in ``testproject/`` and ``lbworkflow/tests/``.

Start a new project and config it
---------------------------------

Creating a project::

    django-admin.py startproject helloword

Add the following code in the file settings.py::

    INSTALLED_APPS = [
        ...
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

    CRISPY_TEMPLATE_PACK = 'bootstrap3'

    LBWF_APPS = {
    }

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

Add the following code in the file urls.py::

    urlpatterns = [
        url(r'^admin/', admin.site.urls),
        url(r'^$', RedirectView.as_view(url='/wf/todo/'), name='home'),
        url(r'^wf/', include('lbworkflow.urls')),
        url(r'^attachment/', include('lbattachment.urls')),
    ]

Install required static package::

    cd helloword
    python manager bower install

Start a new flow
----------------

Creating the issue app::

    python manage.py startapp issue

Creating models::

    from django.db import models

    from lbworkflow.models import BaseWFObj


    class Issue(BaseWFObj):
        title = models.CharField('Title', max_length=255)
        summary = models.CharField('Summary', max_length=255)
        content = models.TextField('Content', blank=True)

        def __str__(self):
            return self.title

Generate flow code::

    import os

    import django


    def gen():
        from lbworkflow.flowgen import FlowAppGenerator
        from issue.models import Issue as wf_class
        FlowAppGenerator().gen(wf_class)

    if __name__ == "__main__":
        os.environ['DJANGO_SETTINGS_MODULE'] = "helloword.settings"
        django.setup()
        gen()


You can config flow in django admin or create a python file and execute it.
Config the flow by code ``issue/wfdata.py``::

    from lbworkflow.core.datahelper import create_activity
    from lbworkflow.core.datahelper import create_category
    from lbworkflow.core.datahelper import create_process
    from lbworkflow.core.datahelper import create_transition


    def load_data():
        load_issue()


    def load_issue():
        """ load_[wf_code] """
        category = create_category('5f31d065-00cc-0020-beea-641f0a670010', 'HR')
        process = create_process('issue', 'Issue', category=category)
        create_activity('5f31d065-00a0-0020-beea-641f0a670010', process, 'Draft', status='draft')
        create_activity('5f31d065-00a0-0020-beea-641f0a670020', process, 'Given up', status='given up')
        create_activity('5f31d065-00a0-0020-beea-641f0a670030', process, 'Rejected', status='rejected')
        create_activity('5f31d065-00a0-0020-beea-641f0a670040', process, 'Completed', status='completed')
        create_activity('5f31d065-00a0-0020-beea-641f0a670050', process, 'A1', operators='[vicalloy]')
        create_transition('5f31d065-00e0-0020-beea-641f0a670010', process, 'Draft,', 'A1')
        create_transition('5f31d065-00e0-0020-beea-641f0a670020', process, 'A1,', 'Completed')

Add the following code in the file settings.py::

    INSTALLED_APPS = [
        ...
        'issue',
    ]

    LBWF_APPS = {
        'leave': 'lbworkflow.tests.leave',
    }


TODO import data,migrate

TODO Create test users

Run it
------

pass
