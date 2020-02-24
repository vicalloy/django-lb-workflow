import django
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/wf/list/'), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^wf/', include('lbworkflow.urls')),
    url(r'^attachment/', include('lbattachment.urls')),

]

django_major_version = django.VERSION[0]

if django_major_version >= 2:
    urlpatterns.append(url(r'^select2/', include('django_select2.urls')))
