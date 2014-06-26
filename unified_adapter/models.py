from datetime import date
from decimal import Decimal

from xlrd import open_workbook

from django.db import models
from django.db.models import Q, F
from django.shortcuts import get_object_or_404

#from access.models import ProductSpecialInformation

#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic


NATART_CHOICES = (
    ('N/A','N/A'),
    ('Nat','Nat'),
    ('Art','Art'),
    ('NFI','NFI'),
    ('NI','NI'),
    ('UNK','UNK')
)


class ProductInfo(models.Model):
    allergens = models.CharField(max_length=50,blank=True,default="")
    approved_promote = models.CharField(max_length=20,blank=True,default="")
    concentrate = models.BooleanField(default=False)
    customer = models.CharField(max_length=60,blank=True,default="")    
    description = models.CharField(max_length=60,blank=True,default="")
    dry = models.BooleanField(default=False)
    duplication = models.BooleanField(default=False)
    emulsion = models.BooleanField(default=False)
    experimental_number = models.PositiveIntegerField(blank=True,null=True)
    export_only = models.CharField(max_length=200,blank=True,default="")
    flash = models.DecimalField(decimal_places=2,max_digits=5,default=0)
    gmo_free = models.BooleanField(default=True)
    heat_stable = models.BooleanField(default=False)
    initials = models.CharField(max_length=20,blank=True,default='')
    keyword_1 = models.CharField(max_length=40,blank=True,default="")
    keyword_2 = models.CharField(max_length=41,blank=True,default="")
    kosher = models.CharField(max_length=200,default="NonKosher")
    liquid = models.BooleanField(default=True) # is this redundant
    location_code = models.CharField(max_length=20,blank=True,default='')
    memo = models.TextField(blank=True)
    microsensitive = models.CharField(max_length=20,blank=True,default="NonSensitive")
    name = models.CharField(max_length=200,blank=False)
    nat_art = models.CharField(max_length=20,blank=True,choices=NATART_CHOICES)
    no_diacetyl = models.BooleanField(default=True)
    no_msg = models.BooleanField(default=True)
    no_pg = models.BooleanField(default=True)
    nutri_on_file = models.BooleanField(default=False)
    organic = models.BooleanField(default=False)
    organoleptic_properties = models.TextField(blank=True,default="")
    oil_soluble = models.BooleanField(default=False)
    percentage_yield = models.PositiveSmallIntegerField(default=100)
    production_number = models.PositiveIntegerField(blank=True,null=True)
    prop65 = models.BooleanField(default=False)
    same_as = models.CharField(max_length=200,blank=True,default="")
    sold = models.BooleanField(default=False)
    solubility = models.CharField(max_length=200,blank=True,default="")
    specific_gravity = models.DecimalField(decimal_places=3,max_digits=4,default=0)
    testing_procedure = models.TextField(blank=True,default="")
    transfat = models.BooleanField(default=False)
    unitprice =models.DecimalField(decimal_places=3,max_digits=7,blank=True,default=0)

    headers = (
                ('production_number','ProNum', 'width="50px" class="{sorter: \'link-digit\'}"'),
                ('nat_art','N/A', ''),
                ('name','Name', ''),
                ('experimental_number','ExNum', 'width="90px" class="{sorter: \'link-digit\'}"'),
                ('location_code','Location Code', 'width="90px" class="{sorter: \'link-digit\'}"')
            )
    
    @property
    def main_number(self):
        if self.production_number is not None:
            return self.production_number
        else:
            return "%s-%s" % (self.initials, self.experimental_number)

    @property
    def applications(self):
        appl_list = []
        for appl in self.application_set.all():
            if appl.memo is not "":
                appl_list.append( "%s %s %s" % (appl.application_type, appl.usage_level, appl.memo))
            else:
                appl_list.append( "%s %s" % (appl.application_type, appl.usage_level))
            
        return ", ".join(appl_list)

    @staticmethod
    def fix_header(header):
        return header

    class Meta:
        ordering = ("production_number","experimental_number","name")
        
    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        def parse_kwarg(key):
            arg_list = []
            for my_arg in qdict.getlist(key):
                arg_list.append(my_arg)
            string_kwargs[key] = arg_list
        
        def parse_bool_kwarg(key):
            arg_list = []
            for my_arg in qdict.getlist(key):
                arg_list.append(bool(my_arg))
            return arg_list
        
        def parse_other_kwarg(key):
            for my_arg in qdict.getlist(key):
                #if my_arg == 'retains__notes':
                #    string_kwargs['retains__notes'] = ''
                #if my_arg == 'no_pg':
                #    string_kwargs['no_pg__in'] = [True]
                string_kwargs['%s__in' % my_arg] = [True,]
        
        key_parse_func_map = {
            'allergens__in': parse_kwarg,
            'approved_promote__in': parse_kwarg,
            'nat_art__in': parse_kwarg,
            'other': parse_other_kwarg,
            'kosher__in': parse_kwarg,
            'application__application_type__id__in': parse_kwarg,
            'initials__in': parse_kwarg,      
        }
        
        for key in get_filter_kwargs(qdict):
            
            if key in key_parse_func_map:
                key_parse_func_map[key](key)
            else:
                parse_bool_kwarg(key)

        return string_kwargs
    
    @staticmethod
    def get_absolute_url(self):
        if self.production_number:
            return '/access/%s/' % self.production_number
        elif self.experimental_number:
            return '/access/experimental/%s/' % self.experimental_number
    
    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            softkey = int(softkey)
        except:
            return None
        finished_products = ProductInfo.objects.filter(production_number=softkey)
        experimentals = ProductInfo.objects.filter(experimental_number=softkey)
        if finished_products.count() == 1 and experimentals.count() == 0:
            return finished_products[0].get_absolute_url()
        elif finished_products.count() == 0 and experimentals.count() == 1:
            return experimentals[0].get_absolute_url()
        
        return None
    
    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            softkey = int(softkey)
        except:
            return None

        finished_products = ProductInfo.objects.filter(production_number=softkey)
        experimentals = ProductInfo.objects.filter(experimental_number=softkey)
        if finished_products.count() == 1 and experimentals.count() == 0:
            return finished_products[0]
        elif finished_products.count() == 0 and experimentals.count() == 1:
            return experimentals[0]
        elif finished_products.count() > 0:
            return finished_products[0]
        elif experimentals.count() > 0:
            return experimentals[0]
        
        
        
        return None
        
    @staticmethod
    def text_search(search_string):
        try:
            search_int = int(search_string)
            
            return ProductInfo.objects.filter( 
                Q(name__icontains=search_string) |
                Q(keyword_1__icontains=search_string) |
                Q(keyword_2__icontains=search_string) |
                Q(memo__icontains=search_string) |
                Q(production_number=search_int) |
                Q(experimental_number=search_int)
            )
        except:
            return ProductInfo.objects.filter( 
                Q(name__icontains=search_string) |
                Q(keyword_1__icontains=search_string) |
                Q(keyword_2__icontains=search_string) |
                Q(memo__icontains=search_string)
            )

class UABooleanField(models.Field):
    def __init__(self, *args, **kwargs):
        super(UABooleanField, self).__init__(*args, **kwargs)


# Create your models here.
class ApplicationType(models.Model):
    name = models.CharField(max_length=40)   
    def __unicode__(self):
        return self.name
    
class Application(models.Model):
    # add a foreign key to productinfo from unified adpater
    product_info = models.ForeignKey('ProductInfo')
    application_type = models.ForeignKey('ApplicationType')
    usage_level = models.DecimalField('Usage level (percentage)', decimal_places=3,
                                      max_digits=5)
    memo = models.TextField(blank=True)
    
    def get_admin_url(self):
        return "/admin/unified_adapter/application/%s/" % self.pk
    
    def __unicode__(self):
        if self.memo is not "":
            return "%s: %s %s %s" % (self.product_info, self.application_type, self.usage_level, self.memo)
        else:
            return "%s: %s %s" % (self.product_info, self.application_type, self.usage_level)

    
    
    
"""Static info from Norma's sheet
"""
APP_NAME = 0
APP_LEVEL = 1
APP_MEMO = 2
APP_OBJ = 3
app_types = [
             ["Misc.",30,31],
             ["Coffee",32,33],
             ["Tea Black",34,None],
             ["Tea White",35,None],
             ["Tea Green",36,None],
             ["Tea Rooibos",37,None],
             ["Flavorcoat",38,None],
             ["Tea Instant",39,None],
             ["Tea Herbal",40,None],
             ["Bakery",41,42],
             ["Beverage",43,44],
             ["Confectionary",45,46],
             ["Dairy",47,48],
             ["Meat & Savory",49,50],
             ["Prepared Foods",51,52],
             ["Snacks",53,54],
             ["Health & Nutraceuticals",55,56],
             ["Personal Hygiene",57,58],
             ["Pet",59,60],
             ["Tobacco",61,None],
             ["Non-food Fragrance",62,63],
             ]

def import_applications(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    re_init()
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    
    for x in range(1, sheet.nrows):
        parse_row(sheet.row(x))
        
#def import_allergens():
#    for psi in ProductSpecialInformation.objects.all():
#        for pi in ProductInfo.objects.filter(production_number=psi.flavornumber):
#            pi.allergens = psi.allergen
#            pi.save()

FLAVOR_NUMBER = 7
def parse_row(row):
    flavor_number = row[FLAVOR_NUMBER].value
    print flavor_number
    try:
        f = ProductInfo.objects.get(production_number=flavor_number)
        single = True
    except ProductInfo.DoesNotExist:
        print "Does not exist: %s" % row[FLAVOR_NUMBER]
        return
    except ProductInfo.MultipleObjectsReturned:
        f_multiple = ProductInfo.objects.filter(production_number=flavor_number)
        single = False
    except ValueError:
        print "Invalid production number: %s" % row[FLAVOR_NUMBER]
        return 
    
    for app in app_types:
        
        try:
            usage_level = row[app[APP_LEVEL]].value
            usage_level = Decimal(str(usage_level))
        except:
            usage_level = 0
        try:
            memo = row[app[APP_MEMO]].value
        except:
            memo = ""
        
        if usage_level != 0 or memo != '':
            print app[APP_NAME]
            print 'usage level: "%s" -- memo: "%s"' % (usage_level, memo)
            if single:
                application = Application(product_info=f,
                        application_type=app[APP_OBJ],
                        usage_level=usage_level,
                        memo=memo
                    )
                application.save()
            else:
                for f in f_multiple:
                    application = Application(product_info=f,
                        application_type=app[APP_OBJ],
                        usage_level=usage_level,
                        memo=memo
                    )
                    application.save()
    
    
def re_init():
    Application.objects.all().delete()
    ApplicationType.objects.all().delete()

    for app in app_types:
        app_type = ApplicationType(name=app[APP_NAME])
        app_type.save()
        app.append(app_type)
