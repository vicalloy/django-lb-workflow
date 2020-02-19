from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from lbutils import get_or_none

from lbworkflow.core.datahelper import load_wf_data

from .leave.models import Leave
from .wfdata import init_users

User = get_user_model()


class BaseTests(TestCase):

    def setUp(self):
        self.init_data()

    def init_users(self):
        super().setUp()
        self.users = init_users()

    # TODO add a function to submit new leave
    def create_leave(self, reason, submit=True):
        leave = Leave(
            start_on=timezone.now(), end_on=timezone.now(), leave_days=1,
            reason=reason, created_by=self.users['owner'])
        leave.init_actual_info()
        leave.save()
        leave.create_pinstance('leave', submit)
        return leave

    def get_leave(self, reason):
        return get_or_none(Leave, reason=reason)

    def init_leave(self):
        self.leave = self.create_leave('reason', False)

    def init_data(self):
        self.init_users()
        load_wf_data('lbworkflow')
        load_wf_data('lbworkflow.tests.leave')
        self.init_leave()
