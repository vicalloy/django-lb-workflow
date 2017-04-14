from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from lbworkflow.models import Activity
from lbworkflow.models import Process
from lbworkflow.models import Transition

from .leave.models import Leave

User = get_user_model()


def create_transition(process, from_activity, to_activity, **kwargs):
    from_activity = Activity.objects.get(process=process, name=from_activity)
    to_activity = Activity.objects.get(process=process, name=to_activity)

    return Transition.objects.create(
        process=process, input_activity=from_activity, output_activity=to_activity,
        **kwargs)


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

    def init_leave_config(self):
        process = Process.objects.create(code='leave', name='Leave')
        Activity.objects.create(process=process, name='Draft', status='draft')
        Activity.objects.create(process=process, name='Given up', status='given up')
        Activity.objects.create(process=process, name='Rejected', status='rejected')
        Activity.objects.create(process=process, name='Completed', status='completed')
        Activity.objects.create(process=process, name='A1', operators='[owner]')
        Activity.objects.create(process=process, name='A2', operators='[tom]')
        Activity.objects.create(process=process, name='A3', operators='[vicalloy]')
        create_transition(process, 'Draft', 'A1')
        create_transition(process, 'A1', 'A2')
        create_transition(process, 'A2', 'A3')
        create_transition(process, 'A3', 'Completed')

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
