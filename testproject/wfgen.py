#!/usr/bin/env python
import inspect
import os
import sys

import django


def gen():
    from lbworkflow.flowgen import FlowAppGenerator
    from lbworkflow.tests.issue.models import Issue as wf_class
    FlowAppGenerator().gen(wf_class)


def clean():
    from lbworkflow.tests.issue.models import Issue as wf_class
    folder_path = os.path.dirname(inspect.getfile(wf_class))
    for path, dirs, files in os.walk(folder_path):
        print(path, dirs, files)
        pass


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
    load_data()
