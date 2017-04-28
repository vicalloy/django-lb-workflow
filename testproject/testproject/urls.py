from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static


urlpatterns = [
    url(r'^', include('lbworkflow.tests.urls')),
    url(r'^impersonate/', include('impersonate.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL_, document_root=settings.MEDIA_ROOT)
