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
    FlowAppGenerator().gen(wf_class, replace=True)
    from lbworkflow.tests.purchase.models import Purchase as wf_class
    from lbworkflow.tests.purchase.models import Item as wf_item_class
    FlowAppGenerator().gen(wf_class, [wf_item_class], replace=True)


def rm_folder(path):
    try:
        shutil.rmtree(path)
    except:
        pass


def clean():
    from lbworkflow.flowgen import clean_generated_files
    from lbworkflow.tests.issue.models import Issue
    clean_generated_files(Issue)
    # remove migrations for leave
    from lbworkflow.tests.leave.models import Leave
    folder_path = os.path.dirname(inspect.getfile(Leave))
    path = os.path.join(folder_path, 'migrations')
    rm_folder(path)
    # remove migrations for purchase
    from lbworkflow.tests.purchase.models import Purchase
    clean_generated_files(Purchase)
    folder_path = os.path.dirname(inspect.getfile(Purchase))
    path = os.path.join(folder_path, 'migrations')
    rm_folder(path)


def load_data():
    from lbworkflow.core.datahelper import load_wf_data
    load_wf_data('lbworkflow')
    load_wf_data('lbworkflow.tests.issue')
    load_wf_data('lbworkflow.tests.leave')
    load_wf_data('lbworkflow.tests.purchase')


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, BASE_DIR)
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
    call_command('makemigrations', 'purchase')
    call_command('migrate')
    load_data()
