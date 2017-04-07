from django.conf.urls import url

from .views.transition import ExecuteAgreeTransitionView
from .views.transition import ExecuteBackToTransitionView
from .views.transition import ExecuteRejectTransitionView
from .views.transition import ExecuteTransitionView

from .views import processinstance

urlpatterns = [
    url(r'^t/$', ExecuteTransitionView.as_view(), name="wf_execute_transition"),
    url(r'^t/agree/$', ExecuteAgreeTransitionView.as_view(), name="wf_agree"),
    url(r'^t/back_to/$', ExecuteBackToTransitionView.as_view(), name="wf_back_to"),
    url(r'^t/reject/$', ExecuteRejectTransitionView.as_view(), name="wf_reject"),

    url(r'^new/(?P<wf_code>\w+)/$', processinstance.new, name='wf_new'),
    url(r'^list/(?P<wf_code>\w+)/$', processinstance.show_list, name='wf_list'),
    url(r'^edit/(?P<pk>\d+)/$', processinstance.edit, name='wf_edit'),
    url(r'^(?P<pk>\d+)/$', processinstance.detail, name='wf_detail'),
    url(r'^(?P<pk>\d+)/print/$', processinstance.detail,
        {
            'ext_ctx': {'is_print': True}
        },
        name='wf_print_detail'),


]
