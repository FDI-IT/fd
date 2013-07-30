from datetime import date

from django.db import models
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic

from access.models import Flavor

def get_next_lot_number():
    today = date.today()
    base_lot_prefix = int(today.strftime('%y%m'))
    base_lot_number = base_lot_prefix*1000
    lot_number_ceil = base_lot_number+999
    #base_overflow_number = base_lot_number*10
    
    current_lots = Lot.objects.filter(number__gte=base_lot_number).filter(number__lte=lot_number_ceil).order_by('-number')
    if current_lots.count() == 0:
        return base_lot_number
    
    next_number = current_lots[0].number + 1
    if next_number > lot_number_ceil:
        overflow_number = base_lot_number*10
        overflow_ceil = overflow_number+9999
        next_number = Lot.objects.filter(number__gte=overflow_number).filter(number__lte=overflow_ceil).order_by('-number')[0].number + 1
    return next_number

class Lot(models.Model):

    date = models.DateField("Issue date", default=date.today)
    number = models.PositiveIntegerField(default=get_next_lot_number)
    sub_lot = models.PositiveSmallIntegerField(blank=True,default="")
    status = models.CharField(max_length=25, default="Pending")
    amount = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True) 
    flavor = models.ForeignKey(Flavor, related_name="plot")
    
    def __unicode__(self):
        return unicode(self.number)

    class Meta:
        ordering = ['number']
        
    def get_admin_url(self):
        return "/django/admin/lot/lot/%s" % self.pk
