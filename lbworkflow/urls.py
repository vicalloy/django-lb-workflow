from django.conf.urls import url

from .views.transition import ExecuteAgreeTransitionView
from .views.transition import ExecuteBackToTransitionView
from .views.transition import ExecuteRejectTransitionView
from .views.transition import ExecuteTransitionView

urlpatterns = [
    url(r'^t/$', ExecuteTransitionView.as_view(), name="wf_execute_transition"),
    url(r'^t/agree/$', ExecuteAgreeTransitionView.as_view(), name="wf_agree"),
    url(r'^t/back_to/$', ExecuteBackToTransitionView.as_view(), name="wf_back_to"),
    url(r'^t/reject/$', ExecuteRejectTransitionView.as_view(), name="wf_reject"),
]
