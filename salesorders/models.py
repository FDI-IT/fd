from django.db import models

from django.db.models import Q
from django.shortcuts import get_object_or_404

from newqc.models import *
#
#def filesave(instance, filename):
#    strftime_string = strftime("salesorders/reports/%Y/%m")
#    return "%s/%s.prn" % (strftime_string, instance.id)
#
#class SavedReport(models.Model):
#    hash = models.CharField(max_length=64,
#                            unique=True)
#    file = models.FileField(upload_to=filesave)
#    upload_date = models.DateField(auto_now_add=True)
#

class SalesOrderNumber(models.Model):
    """
    An abstract idea of a sales order. This holds all the key to all the data
    associated with a sales number that is collected over time.
    """
    number = models.PositiveIntegerField(unique=True)
    create_date = models.DateField(auto_now_add=True)
    #referred_from = models.Fosal    reignKey(null=True, blank=True)
    customer = models.ForeignKey('access.Customer',blank=True,null=True,on_delete=models.CASCADE)
    open = models.BooleanField(default=True)
    # TODO - remove the above field in production
    #purchase order number

    @staticmethod
    def get_next_internal_number():
        return SalesOrderNumber.objects.filter(number__gte=100000).order_by('-number').values_list('number', flat=True)[0] + 1

    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            get_object_or_404(SalesOrderNumber, number=softkey).get_absolute_url()
        except:
            pass

        return None

    def get_absolute_url(self):
        return '/salesorders/%s' % self.number

    headers = (
                    ('number','Number', 'width="80px"'),
                    ('create_date','Create Date', 'width="120px"'),
                    ('customer','Customer', ''),
                    ('open','Open', 'width=40x'),
                )
    class Meta:
        ordering = ["-number"]

    def get_url(self):
        return "/salesorder/%s/" % self.id

    def __str__(self):
        return "%s - %s %s" % (self.number,
                               self.create_date,
                               self.customer)

    @staticmethod
    def text_search(search_string):
        return SalesOrderNumber.objects.filter(
            Q(customer__companyname__icontains=search_string)
        )

    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
            if key == 'open':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    if my_arg == 'False':
                        arg_list.append(False)
                    elif my_arg == 'True':
                        arg_list.append(True)
                string_kwargs[keyword] = arg_list
        return string_kwargs


class LineItem(models.Model):
    """
    A line item of a sales order.
    """
    salesordernumber = models.ForeignKey('SalesOrderNumber',on_delete=models.CASCADE)
    flavor = models.ForeignKey('access.Flavor',on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=9, decimal_places=2) # 12,345.12
    unit_price = models.DecimalField(max_digits=9, decimal_places=3) # $1,234.123 called Sales Price
    quantity_price = models.DecimalField(max_digits=9, decimal_places=3) # $1,234.123 called Amount
    ship_date = models.DateField()
    due_date = models.DateField()
    covered = models.BooleanField(default=False)
    lot = models.ForeignKey('newqc.Lot',null=True,on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s %s lbs $%s" % (self.salesordernumber,
                                         self.flavor,
                                         self.quantity,
                                         self.unit_price)

    class Meta:
        ordering = ["-salesordernumber__number"]
