from django.contrib.auth import get_user_model
from django.urls import reverse

from lbworkflow.core.transition import TransitionExecutor
from lbworkflow.views.helper import user_wf_info_as_dict

from .leave.models import Leave
from .test_base import BaseTests

User = get_user_model()


class TransitionExecutorTests(BaseTests):

    def test_submit(self):
        leave = self.leave
        instance = self.leave.pinstance
        leave.submit_process()

        # A1 will auto agree
        self.assertEqual(leave.pinstance.cur_node.name, 'A2')
        self.assertEqual(leave.pinstance.get_operators_display(), 'tom')

        # A3 not auto agree
        task = instance.get_todo_task()
        transition = instance.get_agree_transition()
        TransitionExecutor(self.users['tom'], instance, task, transition).execute()
        self.assertEqual(leave.pinstance.cur_node.name, 'A3')


class ViewTests(BaseTests):

    def get_transition_url(self, leave, user):
        ctx = user_wf_info_as_dict(leave, user)

        transitions = ctx['transitions']
        transition = transitions[0]
        transition_url = transition.get_app_url(ctx['task'])
        return transition_url

    def setUp(self):
        super(ViewTests, self).setUp()
        self.leave.submit_process()

        leave = self.leave
        ctx = user_wf_info_as_dict(leave, self.users['tom'])

        transitions = ctx['transitions']
        transition = transitions[0]
        self.transition_url = transition.get_app_url(ctx['task'])

        self.task = ctx['task']

        self.client.login(username='tom', password='password')

    def do_agree(self, username, node_name, leave=None, data={}):
        if not leave:
            leave = self.leave
        leave = Leave.objects.get(pk=leave.pk)

        self.client.login(username=username, password='password')

        transition_url = self.get_transition_url(leave, self.users[username])
        resp = self.client.post(transition_url, data=data)
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=leave.pk)
        self.assertEqual(node_name, leave.pinstance.cur_node.name)

    def test_execute_transition(self):
        self.do_agree('tom', 'A3')
        self.do_agree('vicalloy', 'A4')

    def test_execute_transition_customized_url(self):
        self.do_agree('tom', 'A3')
        self.do_agree('vicalloy', 'A4')
        data = {
            'actual_start_on': '2017-04-25 08:00',
            'actual_end_on': '2017-04-26 08:00',
            'actual_leave_days': '2',
        }
        self.do_agree('hr', 'Completed', data=data)

    def goto_A2B1(self):
        leave = self.leave
        leave.leave_days = 10
        leave.save()

        self.do_agree('tom', 'A2B1')

    def test_execute_transition_with_condition(self):
        self.goto_A2B1()

    def test_execute_transition_joint(self):
        self.goto_A2B1()
        self.do_agree('tom', 'A2B1')
        self.do_agree('owner', 'A3')

    def test_execute_transition_no_permission(self):
        self.client.login(username='vicalloy', password='password')
        resp = self.client.post(self.transition_url)
        self.assertEqual(resp.status_code, 403)

    def test_simple_agree(self):
        url = reverse('wf_agree')
        resp = self.client.get('%s?wi_id=%s' % (url, self.task.pk))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('%s?wi_id=%s' % (url, self.task.pk))
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('A3', leave.pinstance.cur_node.name)

    def test_reject(self):
        url = reverse('wf_reject')
        resp = self.client.get('%s?wi_id=%s' % (url, self.task.pk))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('%s?wi_id=%s' % (url, self.task.pk))
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('Rejected', leave.pinstance.cur_node.name)

    def test_give_up(self):
        self.client.login(username='owner', password='password')
        url = reverse('wf_give_up')
        resp = self.client.get('%s?pk=%s' % (url, self.leave.pinstance.pk))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post('%s?pk=%s' % (url, self.leave.pinstance.pk))
        self.assertRedirects(resp, '/wf/my/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('Given up', leave.pinstance.cur_node.name)

    def test_back_to(self):
        self.client.post(self.transition_url)  # A2 TO A3
        leave = Leave.objects.get(pk=self.leave.pk)

        url = reverse('wf_back_to')
        resp = self.client.get('%s?wi_id=%s' % (url, self.task.pk))
        self.assertEqual(resp.status_code, 200)
        back_to_node = leave.pinstance.get_can_back_to_activities()[0]

        resp = self.client.post(
            '%s?wi_id=%s' % (url, self.task.pk),
            {'back_to_node': back_to_node.pk}
        )
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('A2', leave.pinstance.cur_node.name)

    def test_batch_agree(self):
        url = reverse('wf_batch_agree')
        ctx = user_wf_info_as_dict(self.leave, self.users['tom'])
        data = {
            'wi': [ctx['task'].pk, 1, 2, 3],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)

        data['do_submit'] = 'submit'
        resp = self.client.post(url, data)
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('A3', leave.pinstance.cur_node.name)

    def test_batch_reject(self):
        url = reverse('wf_batch_reject')
        ctx = user_wf_info_as_dict(self.leave, self.users['tom'])
        data = {
            'wi': [ctx['task'].pk, 1, 2, 3],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)

        data['do_submit'] = 'submit'
        resp = self.client.post(url, data)
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('Rejected', leave.pinstance.cur_node.name)

    def test_batch_give_up(self):
        self.client.login(username='owner', password='password')
        url = reverse('wf_batch_give_up')
        data = {
            'pi': [self.leave.pinstance.pk, 1, 2, 3],
        }
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 200)

        data['do_submit'] = 'submit'
        resp = self.client.post(url, data)
        self.assertRedirects(resp, '/wf/my/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('Given up', leave.pinstance.cur_node.name)

    def test_add_assignee(self):
        url = reverse('wf_add_assignee')
        url = '%s?wi_id=%s' % (url, self.task.pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = {
            'assignees': (self.users['hr'].pk, self.users['owner'].pk, ),
            'comment': 'comments',
        }
        resp = self.client.post(url, data)
        self.assertRedirects(resp, '/wf/todo/')
        leave = Leave.objects.get(pk=self.leave.pk)
        self.assertEqual('A2', leave.pinstance.cur_node.name)

        self.do_agree('tom', 'A2')
        self.do_agree('hr', 'A2')
        self.do_agree('owner', 'A3')
