============
Installation
============

.. _`install`:

Requirements
------------

* python>=3.4
* django>=1.10
* jsonfield>=1.0.1
* pygraphviz>=1.3
* xlsxwriter>=0.9.6
* jinja2>=2.9.6
* django-lbutils>=1.0.3
* django-lbattachment>=1.0.2
* django-stronghold

The following packages are optional:

* django-compressor>=2.1.1
* django-bower>=5.2.0
* django-crispy-forms>=1.6
* django-lb-adminlte>=0.9.4
* django-el-pagination>=3.0.1
* django-impersonate

Installing django-lb-workflow
------------------------------

Install latest stable version into your python path using pip or easy_install::

    pip install --upgrade django-lb-workflow

If you want to install ``django-lb-workflow`` with all option requires::

    pip install --upgrade django-lb-workflow[options]

If you want to install development version (unstable), you can do so doing::

    pip install git+git://github.com/vicalloy/django-lb-workflow.git#egg=django-lb-workflow

Or, if you'd like to install the development version as a git repository (so
you can ``git pull`` updates, use the ``-e`` flag with ``pip install``, like
so::

    pip install -e git+git://github.com/vicalloy/django-lb-workflow.git#egg=django-lb-workflow

Add ``lbworkflow`` to your ``INSTALLED_APPS`` in settings.py::

    INSTALLED_APPS = (
        ...
        'lbworkflow',
    )

Add ``lbworkflow.urls`` to you ``url``::

    urlpatterns = [
        ...
        url(r'^wf/', include('lbworkflow.urls')),  # url for lbworkflow
        url(r'^attachment/', include('lbattachment.urls')),  # url for lbattachment
    ]

**Others**: You should also config other required APPS, ex: ``django-el-pagination``.

Sample code of using django-lb-workflow
----------------------------------------

You can find sample code of using django-lb-workflow in ``testproject/`` and ``lbworkflow/tests/``.
