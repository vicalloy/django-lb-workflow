from django.contrib.auth import get_user_model

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
