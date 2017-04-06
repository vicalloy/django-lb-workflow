from django.contrib.auth import get_user_model

from lbworkflow.core.transition import TransitionExecutor

from .test_base import BaseTests

User = get_user_model()


class TransitionExecutorTests(BaseTests):

    def test_submit(self):
        leave = self.leave
        instance = self.leave.pinstance
        leave.submit_process()

        # A1 will auto agree
        self.assertEqual(leave.pinstance.cur_activity.name, 'A2')
        self.assertEqual(leave.pinstance.get_users_display(), 'tom')

        # A3 not auto agree
        workitem = instance.get_todo_workitem()
        transition = instance.get_agree_transition()
        TransitionExecutor(self.users['tom'], instance, workitem, transition).execute()
        self.assertEqual(leave.pinstance.cur_activity.name, 'A3')
