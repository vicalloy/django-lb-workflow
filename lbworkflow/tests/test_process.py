from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from lbworkflow.views.helper import user_wf_info_as_dict

from .test_base import BaseTests

User = get_user_model()


class HelperTests(BaseTests):

    def test_user_wf_info_as_dict(self):
        leave = self.leave
        leave.submit_process()

        info = user_wf_info_as_dict(leave, self.users['tom'])
        self.assertIsNotNone(info['workitem'])
        self.assertIsNotNone(info['wf_obj'])
        self.assertFalse(info['can_give_up'])
        self.assertEqual(info['wf_code'], 'leave')

        info = user_wf_info_as_dict(leave, self.users['owner'])
        self.assertIsNone(info['workitem'])
        self.assertTrue(info['can_give_up'])

        info = user_wf_info_as_dict(leave, self.users['vicalloy'])
        self.assertIsNone(info['workitem'])


class ViewTests(BaseTests):

    def test_base_get(self):
        resp = self.client.get(reverse('wf_new', args=('leave', )))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('wf_list', args=('leave', )))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('wf_edit', args=('1', )))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse('wf_detail', args=('1', )))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'from leave.detail')
