from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from .leave.wfdata import load_data


from .leave.models import Leave

User = get_user_model()


class BaseTests(TestCase):

    def setUp(self):
        self.init_data()

    def init_users(self):
        def create_user(username):
            return User.objects.create_user(username, "%s@v.cn" % username, 'password')

        super(BaseTests, self).setUp()
        self.users = {
            'owner': create_user('owner'),
            'operator': create_user('operator'),
            'vicalloy': create_user('vicalloy'),
            'tom': create_user('tom'),
        }

    def init_leave(self):
        leave = Leave(
            start_on=timezone.now(), end_on=timezone.now(), leave_days=1,
            reason='reason', created_by=self.users['owner'])
        leave.init_actual_info()
        leave.save()
        leave.create_pinstance('leave', False)
        self.leave = leave

    def init_data(self):
        self.init_users()
        load_data('leave')
        self.init_leave()
