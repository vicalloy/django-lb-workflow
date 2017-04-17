from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from lbworkflow.core.datahelper import create_process
from lbworkflow.core.datahelper import create_activity
from lbworkflow.core.datahelper import create_transition
from lbworkflow.core.datahelper import create_app

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
        create_app('5f31d065-00aa-0010-beea-641f0a670010', 'Simple URL', action='wf_execute_transition')

    def init_leave_config(self):
        process = create_process('leave', 'Leave')
        create_activity('5f31d065-00a0-0010-beea-641f0a670010', process, 'Draft', status='draft')
        create_activity('5f31d065-00a0-0010-beea-641f0a670020', process, 'Given up', status='given up')
        create_activity('5f31d065-00a0-0010-beea-641f0a670030', process, 'Rejected', status='rejected')
        create_activity('5f31d065-00a0-0010-beea-641f0a670040', process, 'Completed', status='completed')
        create_activity('5f31d065-00a0-0010-beea-641f0a670050', process, 'A1', operators='[owner]')
        create_activity('5f31d065-00a0-0010-beea-641f0a670060', process, 'A2', operators='[tom]')
        create_activity('5f31d065-00a0-0010-beea-641f0a670070', process, 'A3', operators='[vicalloy]')
        create_transition('5f31d065-00e0-0010-beea-641f0a670010', process, 'Draft,', 'A1')
        create_transition('5f31d065-00e0-0010-beea-641f0a670020', process, 'A1,', 'A2')
        create_transition('5f31d065-00e0-0010-beea-641f0a670030', process, 'A2,', 'A3')
        create_transition('5f31d065-00e0-0010-beea-641f0a670040', process, 'A3,', 'Completed')

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
        self.init_leave_config()
        self.init_leave()
