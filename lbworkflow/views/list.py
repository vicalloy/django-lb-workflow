from django.db.models import Q
from django.utils import timezone

from lbworkflow.models import ProcessInstance
from lbworkflow.models import WorkItem
from lbworkflow.views.generics import ListView


class ListWF(ListView):
    ordering = '-created_on'
    template_name = 'lbworkflow/list_wf.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'no',
        'summary',
        'created_by__username',
        'cur_activity__name',
    ]

    def get_base_queryset(self):
        qs = ProcessInstance.objects.filter(cur_activity__status__in=['draft', 'given up'])
        qs = qs.select_related(
            'process',
            'created_by',
            'cur_activity'
        ).distinct()
        return qs


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


class Todo(ListView):
    template_name = 'lbworkflow/todo.html'
    search_form_class = None  # can config search_form_class
    quick_query_fields = [
        'instance__no',
        'instance__summary',
        'instance__cur_activity__name',
        'instance__created_by__username',
    ]

    def get_base_queryset(self):
        user = self.request.user
        qs = WorkItem.objects.filter(
            Q(user=user) | Q(agent_user=user),
            status='in process')
        qs = qs.select_related(
            'instance__no',
            'instance__summary',
            'instance__created_on',
            'instance__process__name',
            'instance__cur_activity__name'
        ).distinct()
        return qs

    def get_queryset(self):
        queryset = super(Todo, self).get_queryset()
        queryset.filter(receive_on=None).update(receive_on=timezone.now())
        return queryset
