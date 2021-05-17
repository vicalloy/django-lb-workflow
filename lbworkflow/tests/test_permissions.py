from django.contrib.auth import get_user_model
from django.urls import reverse

from .leave.models import Leave
from .test_base import BaseTests

User = get_user_model()


class PermissionTests(BaseTests):
    def setUp(self):
        super().setUp()
        self.client.login(username="owner", password="password")

    def test_submit(self):
        self.client.login(username="hr", password="password")
        url = reverse("wf_new", args=("leave",))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username="tom", password="password")
        url = reverse("wf_new", args=("leave",))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_edit(self):
        self.client.login(username="owner", password="password")

        data = {
            "start_on": "2017-04-19 09:01",
            "end_on": "2017-04-20 09:01",
            "leave_days": "1",
            "reason": "test save",
        }
        url = reverse("wf_new", args=("leave",))
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason="test save")
        self.assertRedirects(resp, "/wf/%s/" % leave.pinstance.pk)
        self.assertEqual("Draft", leave.pinstance.cur_node.name)

        # only poster can edit draft
        url = reverse("wf_edit", args=(leave.pinstance.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # other user can't edit draft
        self.client.login(username="hr", password="password")
        url = reverse("wf_edit", args=(leave.pinstance.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

        self.client.login(username="owner", password="password")
        data["act_submit"] = "Submit"
        data["reason"] = "test submit"
        resp = self.client.post(url, data)
        leave = Leave.objects.get(reason="test submit")
        self.assertRedirects(resp, "/wf/%s/" % leave.pinstance.pk)
        self.assertEqual("A2", leave.pinstance.cur_node.name)

        url = reverse("wf_edit", args=(leave.pinstance.pk,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

    def test_detail(self):
        self.client.login(username="hr", password="password")
        resp = self.client.get(reverse("wf_detail", args=("1",)))
        self.assertEqual(resp.status_code, 403)
