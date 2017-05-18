from django.urls import reverse

from .test_base import BaseTests


class ViewTests(BaseTests):

    def test_my_wf(self):
        self.client.login(username='owner', password='password')
        resp = self.client.get(reverse('wf_my_wf'))
        self.assertEqual(resp.status_code, 200)

    def test_list_wf(self):
        self.client.login(username='owner', password='password')
        resp = self.client.get(reverse('wf_list_wf'))
        self.assertEqual(resp.status_code, 200)

    def test_todo(self):
        self.client.login(username='owner', password='password')
        resp = self.client.get(reverse('wf_todo'))
        self.assertEqual(resp.status_code, 200)
