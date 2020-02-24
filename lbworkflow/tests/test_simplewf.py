from django.contrib.auth import get_user_model
from django.urls import reverse

from lbworkflow.core.datahelper import load_wf_data
from lbworkflow.simplewf.models import SimpleWorkFlow

from .test_base import BaseTests

User = get_user_model()


class SimpleWFTests(BaseTests):

    def create_wf(self, wf_code, summary, submit=True):
        wf = SimpleWorkFlow.objects.create(
            summary=summary,
            created_by=self.users['owner'])
        wf.create_pinstance(wf_code, submit)
        return wf

    def init_data(self):
        super().init_data()
        load_wf_data('lbworkflow.simplewf')
        self.wf_a_1 = self.create_wf('simplewf__A', 'wf_a_1')
        self.wf_a_2 = self.create_wf('simplewf__A', 'wf_a_2')
        self.wf_b_1 = self.create_wf('simplewf__B', 'wf_b_1')

    def setUp(self):
        super().setUp()
        self.client.login(username='owner', password='password')

    def test_wf_list(self):
        resp = self.client.get(reverse('wf_list', args=('simplewf__A', )))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'wf_a_1')
        self.assertContains(resp, 'wf_a_2')
        self.assertNotContains(resp, 'wf_b_1')

        resp = self.client.get(reverse('wf_list', args=('simplewf__B', )))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'wf_a_1')
        self.assertNotContains(resp, 'wf_a_2')
        self.assertContains(resp, 'wf_b_1')

    def test_wf_list_export(self):
        resp = self.client.get(reverse('wf_list', args=('simplewf__A', )), {'export': 1})
        self.assertEqual(resp.status_code, 200)

    def test_detail(self):
        resp = self.client.get(reverse('wf_detail', args=(self.wf_a_1.pinstance.pk, )))
        self.assertEqual(resp.status_code, 200)

    def test_submit(self):
        self.client.login(username='owner', password='password')

        url = reverse('wf_new', args=('simplewf__A', ))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_edit(self):
        self.client.login(username='admin', password='password')

        url = reverse('wf_edit', args=(self.wf_a_1.pinstance.pk, ))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
