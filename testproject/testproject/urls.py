from django.conf import settings
from django.conf.urls.static import static
from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("lbworkflow.tests.urls")),
    path("impersonate/", include("impersonate.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL_, document_root=settings.MEDIA_ROOT
    )
