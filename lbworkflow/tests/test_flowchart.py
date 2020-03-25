from django.urls import reverse

from .test_base import BaseTests


class ViewTests(BaseTests):

    def test_flowchart(self):
        resp = self.client.get(reverse('wf_process_flowchart', args=('leave', )))
        self.assertEqual(resp.status_code, 200)

    def test_process_instance_flowchart(self):
        leave = self.create_leave('flowchart', True)
        resp = self.client.get(
            reverse('wf_process_instance_flowchart',
                    args=(leave.pinstance.pk, ))
        )
        self.assertEqual(resp.status_code, 200)
