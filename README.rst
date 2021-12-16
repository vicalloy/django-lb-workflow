django-lb-workflow
==================

.. image:: https://secure.travis-ci.org/vicalloy/django-lb-workflow.svg?branch=master
   :target: http://travis-ci.org/vicalloy/django-lb-workflow

.. image:: https://coveralls.io/repos/github/vicalloy/django-lb-workflow/badge.svg?branch=master
   :target: https://coveralls.io/github/vicalloy/django-lb-workflow?branch=master

Reusable workflow library for Django.

``django-lb-workflow`` supports Django 2.20+ on Python 3.5+.

.. image:: https://github.com/vicalloy/django-lb-workflow/raw/master/docs/_static/demo-flow.png

Demo site
---------

Demo site: http://wf.haoluobo.com/

username: ``admin`` password: ``password``

Switch to another user: http://wf.haoluobo.com/impersonate/search

Stop switch: http://wf.haoluobo.com/impersonate/stop

The code of demo site
---------------------

Carrot Box: https://github.com/vicalloy/carrot-box/

It's a workflow platform, you can start a new project with it.


Documentation
-------------

Read the official docs here: http://django-lb-workflow.readthedocs.io/en/latest/


Installation
------------

Workflow is on PyPI so all you need is: ::

    pip install django-lb-workflow

Pipenv
------

Install pipenv and create a virtualenv:  ::

    pip3 install pipenv
    make pyenv

Spawns a shell within the virtualenv: ::

    pipenv shell

Testing
-------

Running the test suite is as simple as: ::

    make test

Run test project
----------------

Running the test project is as simple as: ::

    npm install
    python testproject/wfgen.py
    make run

Demo for create a new flow
--------------------------

You can find demo code in ``lbworkflow/tests/leave``.

``testproject/wfgen.py`` is a demo for how to generate base code for a flow. The model for this flow is in ``/lbworkflow/tests/issue``.
