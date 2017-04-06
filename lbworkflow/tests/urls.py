from django.conf.urls import url

import lbworkflow


urlpatterns = [
    url(r'^wf/', lbworkflow.urls),
]
