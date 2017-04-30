from django.db import models

from lbworkflow.models import BaseWFObj


class Issue(BaseWFObj):
    title = models.CharField('Title', max_length=255)
    summary = models.CharField('Summary', max_length=255)
    content = models.TextField('Content', blank=True)

    def __str__(self):
        return self.title
