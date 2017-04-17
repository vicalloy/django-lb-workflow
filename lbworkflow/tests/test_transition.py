from django.contrib.auth import get_user_model

from lbworkflow.core.transition import TransitionExecutor
from lbworkflow.views.helper import user_wf_info_as_dict

from .test_base import BaseTests

User = get_user_model()


class TransitionExecutorTests(BaseTests):

    def test_submit(self):
        leave = self.leave
        instance = self.leave.pinstance
        leave.submit_process()

        # A1 will auto agree
        self.assertEqual(leave.pinstance.cur_activity.name, 'A2')
        self.assertEqual(leave.pinstance.get_operators_display(), 'tom')

        # A3 not auto agree
        workitem = instance.get_todo_workitem()
        transition = instance.get_agree_transition()
        TransitionExecutor(self.users['tom'], instance, workitem, transition).execute()
        self.assertEqual(leave.pinstance.cur_activity.name, 'A3')


class ViewTests(BaseTests):

    def setUp(self):
        super(ViewTests, self).setUp()
        self.leave.submit_process()

    def test_execute_transition(self):
        self.client.login(username='tom', password='password')

        leave = self.leave
        ctx = user_wf_info_as_dict(leave, self.users['tom'])
        transitions = ctx['transitions']
        transition = transitions[0]
        url = transition.get_app_url(ctx['workitem'])

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

