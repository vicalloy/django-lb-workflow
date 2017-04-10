from django.conf.urls import include
from django.conf.urls import url

urlpatterns = [
    url(r'^wf/', include('lbworkflow.urls')),
]
