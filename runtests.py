#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    sys.path.append('./testproject')
    os.environ['DJANGO_SETTINGS_MODULE'] = "testproject.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["lbworkflow"])
    sys.exit(bool(failures))
