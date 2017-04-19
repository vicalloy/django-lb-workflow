#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def run_test():
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["lbworkflow"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = "lbworkflow.tests.settings"
    django.setup()
    from django.core.management import call_command
    if (len(sys.argv)) == 2:
        call_command(sys.argv[1])
        sys.exit(0)
    run_test()
