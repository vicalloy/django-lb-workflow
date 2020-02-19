from django.contrib.auth import get_user_model
from django.urls import reverse

from lbworkflow.views.helper import user_wf_info_as_dict

from .leave.models import Leave
from .test_base import BaseTests

User = get_user_model()


class HelperTests(BaseTests):

    def test_user_wf_info_as_dict(self):
        leave = self.leave
        leave.submit_process()

        info = user_wf_info_as_dict(leave, self.users['tom'])
        self.assertIsNotNone(info['task'])
        self.assertIsNotNone(info['object'])
        self.assertFalse(info['can_give_up'])
        self.assertEqual(info['wf_code'], 'leave')

        info = user_wf_info_as_dict(leave, self.users['owner'])
        self.assertIsNone(info['task'])
        self.assertTrue(info['can_give_up'])

        info = user_wf_info_as_dict(leave, self.users['vicalloy'])
        self.assertIsNone(info['task'])


class ViewTests(BaseTests):

    def setUp(self):
        super().setUp()
        self.client.login(username='owner', password='password')

    def test_start_wf(self):
        resp = self.client.get(reverse('wf_start_wf'))
        self.assertEqual(resp.status_code, 200)

    def test_wf_list(self):
        resp = self.client.get(reverse('wf_list', args=('leave', )))
        self.assertEqual(resp.status_code, 200)

    def test_wf_report_list(self):
        resp = self.client.get(reverse('wf_report_list'))
        self.assertEqual(resp.status_code, 200)

    def test_wf_list_export(self):
        resp = self.client.get(reverse('wf_list', args=('leave', )), {'export': 1})
        self.assertEqual(resp.status_code, 200)

    def test_detail(self):
        resp = self.client.get(reverse('wf_detail', args=('1', )))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'from leave.detail')

    def test_submit(self):
        self.client.login(username='owner', password='password')

        url = reverse('wf_new', args=('leave', ))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data = {
            'start_on': '2017-04-19 09:01',
            'end_on': '2017-04-20 09:01',
            'leave_days': '1',
            'reason': 'test save',
        }
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason='test save')
        self.assertRedirects(resp, '/wf/%s/' % leave.pinstance.pk)
        self.assertEqual('Draft', leave.pinstance.cur_node.name)

        data['act_submit'] = 'Submit'
        data['reason'] = 'test submit'
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason='test submit')
        self.assertRedirects(resp, '/wf/%s/' % leave.pinstance.pk)
        self.assertEqual('A2', leave.pinstance.cur_node.name)

    def test_edit(self):
        self.client.login(username='owner', password='password')

        data = {
            'start_on': '2017-04-19 09:01',
            'end_on': '2017-04-20 09:01',
            'leave_days': '1',
            'reason': 'test save',
        }
        url = reverse('wf_new', args=('leave', ))
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason='test save')
        self.assertRedirects(resp, '/wf/%s/' % leave.pinstance.pk)
        self.assertEqual('Draft', leave.pinstance.cur_node.name)

        url = reverse('wf_edit', args=(leave.pinstance.pk, ))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        data['act_submit'] = 'Submit'
        data['reason'] = 'test submit'
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason='test submit')
        self.assertRedirects(resp, '/wf/%s/' % leave.pinstance.pk)
        self.assertEqual('A2', leave.pinstance.cur_node.name)

    def test_delete(self):
        self.client.login(username='admin', password='password')
        # POST
        url = reverse('wf_delete')
        leave = self.create_leave('to delete')
        data = {'pk': leave.pinstance.pk}
        resp = self.client.post(url, data)
        self.assertRedirects(resp, '/wf/list/')
        self.assertIsNone(self.get_leave('to delete'))

        # GET
        leave = self.create_leave('to delete')
        data = {'pk': leave.pinstance.pk}
        resp = self.client.get(url, data)
        self.assertRedirects(resp, '/wf/list/')
        self.assertIsNone(self.get_leave('to delete'))
