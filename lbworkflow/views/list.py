from lbworkflow.views.generics import ListView
from lbworkflow.models import ProcessInstance


class MyWF(ListView):
    template_name = 'lbworkflow/my_wf.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'no',
        'summary',
        'cur_activity__name',
    ]

    def get_base_queryset(self):
        return ProcessInstance.objects.filter(created_by=self.request.user)
