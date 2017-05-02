#!/usr/bin/env python
import inspect
import os
import shutil
import sys

import django
from django.core.management import call_command


def gen():
    from lbworkflow.flowgen import FlowAppGenerator
    from lbworkflow.tests.issue.models import Issue as wf_class
    FlowAppGenerator().gen(wf_class)


def clean():
    from lbworkflow.flowgen import clean_generated_files
    from lbworkflow.tests.issue.models import Issue
    clean_generated_files(Issue)
    # remove migrations for leave
    from lbworkflow.tests.leave.models import Leave
    folder_path = os.path.dirname(inspect.getfile(Leave))
    path = os.path.join(folder_path, 'migrations')
    shutil.rmtree(path)


def load_data():
    from lbworkflow.core.datahelper import load_wf_data
    load_wf_data('lbworkflow')
    load_wf_data('lbworkflow.tests.issue')
    load_wf_data('lbworkflow.tests.leave')

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = "testproject.settings"
    django.setup()
    if (len(sys.argv)) == 2:
        cmd = sys.argv[1]
        if cmd == 'load_data':
            load_data()
        elif cmd == 'clean':
            clean()
        sys.exit(0)
    gen()
    call_command('makemigrations', 'issue')
    call_command('makemigrations', 'leave')
    call_command('migrate')
    load_data()
