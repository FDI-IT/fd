"""
Describes all of the data related to QC
"""

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from fd.flavorbase.models import Flavor
from fd.production.models import Lot

special_cells_new = (
    'name', (1,0),
    'prefix', (8,3),
    'product', (8,4),
    'testing_procedure', (6,0),
    'appearance', (1,7),
    'organoleptic_properties', (2,7),
    'flash_point', (3,7),
    'specific_gravity', (4,7) )
"Coordinates of indicated data in new-style QC cards"

special_cells_old = (
    'name', (0,0),
    'prefix', (3,3),
    'product', (3,4),
    'testing_procedure', (1,2) )
"Coordinates of indicated data in old-style QC cards"

class Retain(models.Model):
    """
    Data related to the retained sample of a production lot.
    """
    retain = models.PositiveSmallIntegerField()
    date = models.DateField("Date on which product was QCed")
    lot = models.ForeignKey(Lot, blank=True, null=True)
    status = models.CharField(max_length=25)
    notes = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    product = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-date', '-retain']

    def __unicode__(self):
        return str(self.date.year)[2:5] + "-" + str(self.retain).zfill(4)
"""
class FlavorChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.id
"""

