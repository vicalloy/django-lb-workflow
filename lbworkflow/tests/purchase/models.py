from django.db import models

from lbworkflow.models import BaseWFObj


class Purchase(BaseWFObj):
    title = models.CharField('Title', max_length=255)
    reason = models.CharField('Reason', max_length=255)

    def __str__(self):
        return self.reason


class Item(models.Model):
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
    )
    name = models.CharField('Name', max_length=255)
    qty = models.IntegerField('Qty')
    note = models.CharField('Note', max_length=255)

    class Meta:
        verbose_name = 'Purchase Item'

    def __str__(self):
        return self.name
