from django.urls import path

from .views import flowchart
from .views import processinstance
from .views.list import ListWF
from .views.list import MyWF
from .views.list import Todo
from .views.transition import AddAssigneeView
from .views.transition import BatchExecuteAgreeTransitionView
from .views.transition import BatchExecuteGiveUpTransitionView
from .views.transition import BatchExecuteRejectTransitionView
from .views.transition import ExecuteAgreeTransitionView
from .views.transition import ExecuteBackToTransitionView
from .views.transition import ExecuteGiveUpTransitionView
from .views.transition import ExecuteRejectTransitionView
from .views.transition import ExecuteTransitionView
from .views.transition import execute_transitions

urlpatterns = [
    path('t/', ExecuteTransitionView.as_view(), name="wf_execute_transition"),
    path('t/agree/', ExecuteAgreeTransitionView.as_view(), name="wf_agree"),
    path('t/back_to/', ExecuteBackToTransitionView.as_view(), name="wf_back_to"),
    path('t/reject/', ExecuteRejectTransitionView.as_view(), name="wf_reject"),
    path('t/give_up/', ExecuteGiveUpTransitionView.as_view(), name="wf_give_up"),
    path('t/add_assignee/', AddAssigneeView.as_view(), name="wf_add_assignee"),
    path('t/batch/agree/', BatchExecuteAgreeTransitionView.as_view(), name="wf_batch_agree"),
    path('t/batch/reject/', BatchExecuteRejectTransitionView.as_view(), name="wf_batch_reject"),
    path('t/batch/give_up/', BatchExecuteGiveUpTransitionView.as_view(), name="wf_batch_give_up"),
    path(
        't/e/<str:wf_code>/<str:trans_func>/', execute_transitions,
        name='wf_execute_transition'),

    path('start_wf/', processinstance.start_wf, name='wf_start_wf'),
    path('report_list/', processinstance.report_list, name='wf_report_list'),

    path('new/<str:wf_code>/', processinstance.new, name='wf_new'),
    path('delete/', processinstance.delete, name='wf_delete'),
    path('list/<str:wf_code>/', processinstance.show_list, name='wf_list'),
    path('edit/<int:pk>/', processinstance.edit, name='wf_edit'),
    path('<int:pk>/', processinstance.detail, name='wf_detail'),
    path('<int:pk>/print/', processinstance.detail,
         {
             'ext_ctx': {'is_print': True}
         },
         name='wf_print_detail'),
    path('todo/', Todo.as_view(), name='wf_todo'),
    path('list/', ListWF.as_view(), name='wf_list_wf'),
    path('my/', MyWF.as_view(), name='wf_my_wf'),

    path('flowchart/process/<str:wf_code>/',
         flowchart.process_flowchart,
         name='wf_process_flowchart'),
]
