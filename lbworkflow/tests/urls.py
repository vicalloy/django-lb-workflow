from django.conf.urls import url
from django.conf.urls import include


urlpatterns = [
    url(r'^wf/', include('lbworkflow.urls')),
]
