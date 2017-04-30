from lbworkflow.flowgen import FlowAppGenerator
from lbworkflow.flowgen import clean_generated_files
from lbworkflow.tests.issue.models import Issue

from .test_base import BaseTests


class ViewTests(BaseTests):

    def test_gen(self):
        FlowAppGenerator().gen(Issue)
        clean_generated_files(Issue)

