from django.db import models

from lbworkflow.models import BaseWFObj


class SimpleWorkFlow(BaseWFObj):
    summary = models.CharField('Summary', max_length=255)
    # process.ext_data['template'] is the default content
    content = models.TextField('Content', blank=True)

    def __str__(self):
        return self.summary
