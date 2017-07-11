from lbworkflow.flowgen import FlowAppGenerator
from lbworkflow.flowgen import clean_generated_files
from lbworkflow.tests.issue.models import Issue
from lbworkflow.tests.purchase.models import Item
from lbworkflow.tests.purchase.models import Purchase

from .test_base import BaseTests


class ViewTests(BaseTests):

    def test_gen_no_item_list(self):
        FlowAppGenerator().gen(Issue)
        clean_generated_files(Issue)

    def test_gen_with_item_list(self):
        FlowAppGenerator().gen(Purchase, [Item])
        clean_generated_files(Purchase)
