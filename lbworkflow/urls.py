from django.conf.urls import url

from .views import flowchart
from .views import processinstance
from .views.list import ListWF
from .views.list import MyWF
from .views.list import Todo
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
    url(r'^t/$', ExecuteTransitionView.as_view(), name="wf_execute_transition"),
    url(r'^t/agree/$', ExecuteAgreeTransitionView.as_view(), name="wf_agree"),
    url(r'^t/back_to/$', ExecuteBackToTransitionView.as_view(), name="wf_back_to"),
    url(r'^t/reject/$', ExecuteRejectTransitionView.as_view(), name="wf_reject"),
    url(r'^t/give_up/$', ExecuteGiveUpTransitionView.as_view(), name="wf_give_up"),
    url(r'^t/batch/agree/$', BatchExecuteAgreeTransitionView.as_view(), name="wf_batch_agree"),
    url(r'^t/batch/reject/$', BatchExecuteRejectTransitionView.as_view(), name="wf_batch_reject"),
    url(r'^t/batch/give_up/$', BatchExecuteGiveUpTransitionView.as_view(), name="wf_batch_give_up"),
    url(
        r'^t/e/(?P<wf_code>\w+)/(?P<trans_func>\w+)/$', execute_transitions,
        name='wf_execute_transition'),

    url(r'^start_wf/$', processinstance.start_wf, name='wf_start_wf'),
    url(r'^report_list/$', processinstance.report_list, name='wf_report_list'),

    url(r'^new/(?P<wf_code>\w+)/$', processinstance.new, name='wf_new'),
    url(r'^delete/$', processinstance.delete, name='wf_delete'),
    url(r'^list/(?P<wf_code>\w+)/$', processinstance.show_list, name='wf_list'),
    url(r'^edit/(?P<pk>\d+)/$', processinstance.edit, name='wf_edit'),
    url(r'^(?P<pk>\d+)/$', processinstance.detail, name='wf_detail'),
    url(r'^(?P<pk>\d+)/print/$', processinstance.detail,
        {
            'ext_ctx': {'is_print': True}
        },
        name='wf_print_detail'),

    url(r'^todo/$', Todo.as_view(), name='wf_todo'),
    url(r'^list/$', ListWF.as_view(), name='wf_list_wf'),
    url(r'^my/$', MyWF.as_view(), name='wf_my_wf'),

    url(r'^flowchart/process/(?P<wf_code>\w+)/$',
        flowchart.process_flowchart, name='wf_process_flowchart'),

]
