from django.db import models
from datetime import datetime
from time import strftime

from django.db.models import Q, F

class Invoice(models.Model):
    number = models.PositiveIntegerField(unique=True)
    create_date = models.DateField(auto_now_add=True)
    qb_date = models.DateField()
    customer = models.ForeignKey('access.Customer',blank=True,null=True,on_delete=models.CASCADE)
    open = models.BooleanField(default=True)

    headers = (
                    ('number','Number', 'width="80px"'),
                    ('qb_date','Date', 'width="120px"'),
                    ('customer','Customer', ''),
                    ('open','Open', 'width=40x'),
                )
    class Meta:
        ordering = ["-number"]

    def get_url(self):
        return "/invoice/%s/" % self.id

    def __str__(self):
        return "%s - %s %s" % (self.number,
                               self.create_date,
                               self.customer)

    @staticmethod
    def text_search(search_string):
        return Invoice.objects.filter(
            Q(customer__companyname__icontains=search_string) |
            Q(number=search_string)
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
    invoice = models.ForeignKey('Invoice',on_delete=models.CASCADE)
    flavor = models.ForeignKey('access.Flavor', related_name="invoice_lineitem",on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=9, decimal_places=2) # 12,345.12
    rawmaterialcost = models.DecimalField(max_digits=9, decimal_places=3) # $1,234.123 called Sales Price
    quantity_cost = models.DecimalField(max_digits=9, decimal_places=3) # $1,234.123 called Amount

    def __str__(self):
        return "%s - %s %s lbs $%s" % (self.invoice,
                                         self.flavor,
                                         self.quantity,
                                         self.rawmaterialcost)
