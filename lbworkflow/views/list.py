from django.db.models import Q
from django.utils import timezone

from lbworkflow.models import ProcessInstance, Task
from lbworkflow.views.generics import ListView

from .helper import get_base_wf_permit_query_param


class ListWF(ListView):
    model = ProcessInstance
    ordering = "-created_on"
    template_name = "lbworkflow/list_wf.html"
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        "no",
        "summary",
        "created_by__username",
        "cur_node__name",
    ]

    def permit_filter(self, qs):
        # only show have permission
        user = self.request.user
        if not user.is_superuser:
            q_param = get_base_wf_permit_query_param(user, "")
            qs = qs.filter(q_param)
        return qs

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.exclude(cur_node__status__in=["draft", "given up"])
        qs = self.permit_filter(qs)
        qs = qs.select_related("process", "created_by", "cur_node").distinct()
        return qs


class MyWF(ListView):
    model = ProcessInstance
    template_name = "lbworkflow/my_wf.html"
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        "no",
        "summary",
        "cur_node__name",
    ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)


class Todo(ListView):
    model = Task
    template_name = "lbworkflow/todo.html"
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        "instance__no",
        "instance__summary",
        "instance__cur_node__name",
        "instance__created_by__username",
    ]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        qs = qs.filter(Q(user=user) | Q(agent_user=user), status="in progress")
        qs.filter(receive_on=None).update(receive_on=timezone.now())
        qs = qs.select_related(
            "instance", "instance__process", "instance__cur_node"
        ).distinct()
        return qs
