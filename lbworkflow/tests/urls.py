from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/wf/list/'), name='home'),
    path('admin/', admin.site.urls),
    path('wf/', include('lbworkflow.urls')),
    path('attachment/', include('lbattachment.urls')),
    path('select2/', include('django_select2.urls')),
]
