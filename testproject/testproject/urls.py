from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^', include('lbworkflow.tests.urls')),
    url(r'^impersonate/', include('impersonate.urls')),
]
