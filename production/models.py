from django.db import models
from flavorbase.models import Flavor
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Lot(models.Model):
    """
    A lot requested as part of a customer purchase order.
    """
    lot = models.PositiveIntegerField()
    sub_lot = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField("Date on which lot was ordered. Auto-set.", auto_now_add=True)
    status = models.CharField(max_length=25)
    amount = models.DecimalField(max_digits=6,
                                 decimal_places=2,
                                 blank=True, null=True)
    flavor = models.ForeignKey(Flavor)

    class Meta:
        ordering = ['-date', '-lot']

    def __unicode__(self):
        return str(self.lot)

