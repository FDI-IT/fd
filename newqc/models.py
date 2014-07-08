from datetime import date

from django.db.models import Q, F
from django.db import models
from django.db.models import Count

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


from access.models import Flavor, Ingredient, ExperimentalLog, FlavorSpecification, Customer

UNITS_CHOICES = (
    ('lbs','lbs'),
    ('kg','kg'),
    ('gal','gal'),
    ('oz','oz'),
    ('g','g'),                 
)

STATUS_CHOICES = (
    ('Created','Created'),
    ('In Production','In Production'),
    ('Pending QC','Pending QC'),
    ('Passed','Passed'),
    ('Hold','Hold'),
    ('Resample','Resample'),
    ('Rework','Rework'),
    ('Rejected','Rejected'),
    ('Expired','Expired'),
    ('RM','RM'),
    ('Duplicate','Duplicate'),
)

RM_STATUS_CHOICES = (
    ('Ordered','Ordered'),
    ('Received','Received'),
    ('Pending QC','Pending QC'),
    ('Passed','Passed'),
    ('Hold','Hold'),
    ('Resample','Resample'),
    ('Rejected','Rejected'),
    ('Expired','Expired'),
)

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

class ProductInfoManager(models.Manager):
    def update_or_create(self, flavor, *args, **kwargs):
        flavor_info, created = ProductInfo.objects.get_or_create(flavor=flavor)
        if created:
            for flavor_info_k, flavor_info_v in kwargs.iteritems():
                setattr(flavor_info, flavor_info_k, flavor_info_v)
            flavor_info.save()
            return (flavor_info, created)
        else:
            return (flavor_info, created)

class ProductInfo(models.Model):
    """
    Info scrubbed from QC cards about products
    """
    flavor = models.OneToOneField(Flavor)
    appearance = models.CharField(max_length=100, blank=True)
    organoleptic_properties = models.CharField(max_length=100, blank=True)
    testing_procedure = models.TextField(blank=True)
    flash_point = models.FloatField(blank=True, null=True)
    specific_gravity = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    retain_on_file = models.BooleanField(default=False)
    original_card = models.FileField(upload_to='qc_original_cards',blank=True,null=True)
    objects = ProductInfoManager()
    
    def __unicode__(self):
        return self.flavor.__unicode__()

    def get_admin_url(self):
        return "/admin/newqc/productinfo/%s" % self.pk
    
class ScannedSymbol(models.Model):
    scanned_doc = models.ForeignKey('ScannedDoc')
    symbol_data = models.TextField()
    symbol_type = models.CharField(max_length=100)
    symbol_quality = models.DecimalField(max_digits=3, decimal_places=2)
    symbol_location = models.CharField(max_length=100)
    symbol_count = models.PositiveSmallIntegerField()
    
    def __init__(self, *args, **kwargs):
        zbar_symbol = kwargs.pop('zbar_symbol', None)
        super(ScannedSymbol, self).__init__(*args, **kwargs)
        if zbar_symbol is not None:
            self.parse_zbar_symbol(zbar_symbol)

    def parse_zbar_symbol(self, zbar_symbol):
        self.symbol_data = zbar_symbol.data
        self.symbol_type = unicode(zbar_symbol.type) # zbar.EnumItem type
        self.symbol_quality = zbar_symbol.quality
        self.symbol_location = unicode(zbar_symbol.location) # 4x 2-tuples, represent coords of symbol
        self.symbol_count = zbar_symbol.count
        
    def __unicode__(self):
        return """DATA: %s | TYPE: %s | QUALITY: %s | LOCATION: %s | COUNT %s""" % (
                self.symbol_data, 
                self.symbol_type,
                self.symbol_quality,
                self.symbol_location,
                self.symbol_count)
                
    
class ScannedDoc(models.Model):
    related_object_name = None
    
    image_hash = models.CharField(max_length=64, blank=True)
    large = models.ImageField(upload_to='scanned_doc_large')
    thumbnail = models.ImageField(upload_to='scanned_doc_thumbnail')
    notes = models.TextField(blank=True, default="")
    scan_time = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    import_log = models.TextField(blank=True,default="")
    
    class Meta:
        ordering = ['-id']
        
    @property
    def subclass_object(self):
        if hasattr(self, "_related_object"):
            return self._related_object
         
        try:
            self._related_object = self.batchsheet
            return self._related_object
        except BatchSheet.DoesNotExist:
            pass
          
        try:
            self._related_object = self.testcard
            return self._related_object
        except TestCard.DoesNotExist:
            pass
          
        try:
            self._related_object = self.rmtestcard
            return self._related_object
        except RMTestCard.DoesNotExist:
            pass

        return self
    
    @property
    def related_object(self):
        return self.subclass_object.related_object
        
    @property
    def subclass_object_repr(self):
        return repr(self.related_object)
        
    @property
    def doc_link(self):
        return self.subclass_object.get_absolute_url()
    
    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        """In this case bc_key is going to be None, that's why we would
        save a generic ScannedDoc and not a more specific type of object.
        This method exists so this type can be handled the same as the more
        specific types."""
        return ScannedDoc(**document_create_kwargs)

        
class TestCard(ScannedDoc):
    related_object_name = 'retain'
    
    retain = models.ForeignKey('Retain', null=True)
    status = models.CharField(max_length=25,choices=STATUS_CHOICES,default='Pending QC')
    
    @property
    def related_object(self):
        return self.retain
    
    def __unicode__(self):
        return "%s" % (self.retain)
    
    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            r = Retain.objects.get(pk=bc_key)
        except Retain.DoesNotExist:
            r = None
        return TestCard(
                    retain=r,
                    **document_create_kwargs)
    
    #@property
    def get_absolute_url(self):
        return self.retain.get_absolute_url()


class RMTestCard(ScannedDoc):
    related_object_name = 'retain'
    
    retain = models.ForeignKey('RMRetain', null=True)
    status = models.CharField(max_length=25,choices=RM_STATUS_CHOICES,default='Pending QC')
    
    @property
    def related_object(self):
        return self.retain
    
    def __unicode__(self):
        return "%s" % (self.retain)
    
    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            r = RMRetain.objects.get(pk=bc_key)
        except RMRetain.DoesNotExist:
            r = None
        return RMTestCard(
                    retain=r,
                    **document_create_kwargs)
        
    @staticmethod
    def get_absolute_url(self):
        return "/access/ingredient/pin_review/%s/" % self.retain.pin

class BatchSheet(ScannedDoc):
    related_object_name = 'lot'
    
    lot = models.ForeignKey('Lot', null=True)
    status = models.CharField(max_length=25, default='')
    
    @property
    def related_object(self):
        return self.lot
    
    class Meta:
        ordering = ['-id']
        
    def __unicode__(self):
        if self.lot is None:
            return "Invalid"
        return "%s" % (self.lot.number)

    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            l = Lot.objects.get(number=bc_key)
        except Lot.DoesNotExist:
            l = None
        return BatchSheet(
                    lot=l,
                    **document_create_kwargs)


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
        try:
            next_number = Lot.objects.filter(number__gte=overflow_number).filter(number__lte=overflow_ceil).order_by('-number')[0].number + 1
        except IndexError:
            next_number = overflow_number
    return next_number

class LotManager(models.Manager):
    def get_query_set(self):
        objs = super(LotManager, self).get_query_set().all().extra(select={'lotyear':'extract(year from date)','lotmonth':'extract(month from date)'})
        return objs.order_by('-lotyear','-lotmonth','-number')

class Lot(models.Model):
    objects = LotManager()
    date = models.DateField("Issue date", default=date.today)
    number = models.PositiveIntegerField(default=get_next_lot_number)
    sub_lot = models.PositiveSmallIntegerField(blank=True,null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default="Created")
    amount = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True) 
    flavor = models.ForeignKey(Flavor)
    
    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            softkey=int(softkey)
            lots = Lot.objects.filter(number=softkey)
            if len(lots) == 1:
                return lots[0]
        except:
            return None
        return None
    
    @staticmethod
    def text_search(search_string):
        try:
            search_int = int(search_string)
            
            return Lot.objects.filter(
                    Q(number=search_string) |
                    Q(flavor__number=search_int)
                )
        except:
            return Lot.objects.filter(flavor__name__icontains=search_string)
    
    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
            if key == 'status':
                keyword = 'status__in'
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            
        return string_kwargs
    
    def __unicode__(self):
        return unicode(self.number)

    @staticmethod
    def fix_header(header):
        return header

    @staticmethod
    def get_absolute_url(self):
        return "/qc/lots/%s/" % self.pk

    class Meta:
        ordering = ['-date']
        
    def get_admin_url(self):
        return "/admin/newqc/lot/%s" % self.pk
    
    def retains_present(self):
        return self.retain_set.all().count() > 0
    
    @property
    def testcards_present(self): 
        for r in self.retain_set.all():
            if r.testcards_present():
                return True
        return False
    
    @property
    def batchsheets_present(self): 
        return self.batchsheet_set.all().count() > 0
    
    def coa_tests_image(self):
        all_completed = True
        if self.testresult_set.count() == 0:
            return None 
        
        for testresult in self.testresult_set.all():
            if testresult.result == '' or testresult.result == None:
                return '/djangomedia/images/Icons/16x16/pause.png'
                
        return '/djangomedia/images/Icons/16x16/accept.png'
            
    
    headers = (
            ('number','Lot Number', 'class="{sorter: \'link-digit\'}"'),
            ('sub_lot','Sub Lot',''),
            ('flavor','Flavor', ''),
            ('date','Date', ''),
            ('amount','Amount', ''),
            ('status','Status',''),
            
            ('testcards_present','QC Tests',''),
            ('batchsheets_present','Batchsheet',''),
        )
    
class LotWeightAdjustment(Lot):
    class Meta:
        proxy=True

    
class LotSOLIStamp(models.Model):
    lot = models.ForeignKey('Lot')
    salesordernumber = models.PositiveIntegerField()
    quantity = models.DecimalField(max_digits=9,decimal_places=2)
    

class COA(models.Model):
    lss = models.ForeignKey('LotSOLIStamp')
    
class TestResult(models.Model):
    lot = models.ForeignKey('Lot')
    #spec = models.ForeignKey('access.FlavorSpecification')
    name = models.CharField(max_length=48)
    specification = models.CharField(max_length=48)
    result = models.CharField(max_length=48, blank=True, null=True)
    replaces = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(Customer, blank=True, null=True)
     
class Retain(models.Model):
    """
    Data related to the retained sample of a production lot.
    """
    retain = models.PositiveSmallIntegerField()
    date = models.DateField("Date on which product was QCed")
    lot = models.ForeignKey(Lot)
    status = models.CharField(max_length=25,
                              choices=STATUS_CHOICES)
    notes = models.CharField(max_length=500,
                             blank=True,
                             default='')
    ir = models.ForeignKey('ImportRetain', blank=True, null=True, default=None, editable=False)
    browse_url = '/qc/retains/'
    class Meta:
        ordering = ['-date', '-retain']

    def __unicode__(self):
        return str(self.date.year)[2:5] + "-" + str(self.retain).zfill(4)

    def testcards_present(self):
        return self.testcard_set.all().count() > 0

    def get_admin_url(self):
        return "/admin/newqc/retain/%s" % self.pk
    
    def similar_to(self, other):
        if self.date == other.date:
            if self.lot == other.lot:
                return True
        return False
    
    @staticmethod
    def get_next_object_number():
        current_retains = Retain.objects.filter(date__year=date.today().year)
        try:
            last_retain = current_retains[0]
        except:
            return 1 #start at 1, you get an error if you add a retain with number 0
        return last_retain.retain + 1
    
    @staticmethod
    def get_absolute_url(self):
        return "/qc/lots/%s/" % self.lot.pk

class ImportRetain(models.Model):
    number = models.PositiveSmallIntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    flavor_number = models.PositiveIntegerField(blank=True, null=True)
    lot_number = models.PositiveIntegerField(blank=True, null=True)
    sub_lot_number = models.PositiveSmallIntegerField(blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=6, decimal_places=1, blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
    path = models.CharField(max_length=200, blank=True, null=True)
    
class RMImportRetain(models.Model):
    date = models.DateField(blank=True,null=True)
    pin = models.PositiveSmallIntegerField(blank=True,null=True)
    supplier = models.CharField(max_length=40,blank=True,null=True)
    name = models.CharField(max_length=100,blank=True,null=True)
    lot = models.CharField(max_length=40,blank=True,null=True)
    r_number = models.PositiveSmallIntegerField(blank=True,null=True)
    status = models.CharField(max_length=20,blank=True,null=True)
    notes = models.CharField(max_length=200,blank=True,null=True)
    
    def __unicode__(self):
        return u" - ".join((
                    unicode(self.date),
                    unicode(self.pin),
                    unicode(self.supplier),
                    unicode(self.name),
                    unicode(self.lot),
                    unicode(self.r_number),
                    unicode(self.status),
                    unicode(self.notes)
                ))

class RMInfo(models.Model):
    """
    Info scrubbed from QC cards about products
    """
    pin = models.PositiveSmallIntegerField()
    testing_procedure = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    retain_on_file = models.BooleanField(default=False)
    original_card = models.FileField(upload_to='rm_original_cards',blank=True,null=True)
    #objects = ProductInfoManager()
    
    def __unicode__(self):
        return unicode(self.pin)

    def get_admin_url(self):
        return "/admin/newqc/rm_info/%s" % self.pk

class RMRetain(models.Model):
    """
    Data related to the retained sample of a raw material.
    """
    date = models.DateField("Date on which product was QCed")
    pin = models.PositiveSmallIntegerField()
    supplier = models.CharField(max_length=40)
    lot = models.CharField(max_length=40,blank=True,default="")
    r_number = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=25,
                              choices=RM_STATUS_CHOICES)
    notes = notes = models.CharField(max_length=200,blank=True,default="")
    ir = models.ForeignKey('RMImportRetain', blank=True, null=True, default=None, editable=False)

    @property
    def related_ingredient(self):
        return Ingredient.objects.filter(discontinued=False).get(id=self.pin)
    
    class Meta:
        ordering = ['-date', '-r_number']

    def __unicode__(self):
        return u"PIN: " + str(self.pin) + " " + str(self.date.year)[2:5] + "-R" + str(self.r_number).zfill(3)

        
    @staticmethod
    def get_absolute_url(self):
        return "/access/ingredient/pin_review/%s/" % self.pin

    def get_admin_url(self):
        return "/admin/newqc/rmretain/%s/" % self.pk
    
    browse_url = "/qc/rm_retains/"

class ReceivingLogManager(models.Manager):
    def get_query_set(self):
        objs = super(ReceivingLogManager, self).get_query_set().extra(select={'receiving_year':'extract(year from date)','receiving_month':'extract(month from date)'})
        objs = objs.order_by('-receiving_year','-receiving_month','-r_number')
#        d =  objs[0].date
#        print d
        return objs

def get_next_r_number():
    today = date.today()
    try:
        rl = ReceivingLog.objects.filter(date__year=today.year)[0]
        return rl.r_number + 1
    except:
        return 1
    
class ReceivingLog(models.Model):
    objects = ReceivingLogManager()
    r_number = models.PositiveSmallIntegerField(default=get_next_r_number)
    date = models.DateField(auto_now_add=True)
    pin = models.PositiveSmallIntegerField()
    supplier = models.CharField(max_length=40)
    description = models.CharField(max_length=120)
    quantity_of_packages = models.DecimalField(max_digits=4, decimal_places=1)
    package_size = models.DecimalField(max_digits=6, decimal_places=3)
    units = models.CharField(max_length=20,choices=UNITS_CHOICES)
    lot = models.CharField(max_length=40)
    po_number = models.PositiveIntegerField("PO Number")
    trucking_co = models.CharField(max_length=40)
    kosher_group = models.CharField(max_length=40)
    
    class Meta:
        ordering = ['-id',]
    
    @staticmethod
    def create_from_cleaned_data(cd):
        x = ReceivingLog(**cd)
        return x
    
    def get_admin_url(self):
        return "/admin/newqc/receivinglog/%s/" % self.pk

    browse_url = '/qc/receiving_log/'

    @staticmethod
    def get_next_r_number():
        today = date.today()
        try:
            rl = ReceivingLog.objects.filter(date__year=today.year)[0]
            return rl.r_number + 1
        except:
            return 1

#    def similar_to(self, other):
#        if self.date == other.date:
#            if self.lot == other.lot:
#                return True
#        return False

def next_experimental_retain_number():
    try:
        return ExperimentalRetain.objects.all().order_by('-retain')[0].retain + 1
    except IndexError:
        return 1
        
class ExperimentalRetain(models.Model):
    """
    Data related to the retained sample of an experimental product.
    """
    retain = models.PositiveSmallIntegerField(default=next_experimental_retain_number)
    date = models.DateField()
    experimental_log = models.ForeignKey(ExperimentalLog)
    comments = models.TextField()
    
    class Meta:
        ordering = ['-date', '-retain']

    def __unicode__(self):
        return str(self.date.year)[2:5] + "-" + str(self.retain).zfill(4)

    def get_admin_url(self):
        return "/admin/newqc/experimentalretain/%s/" % self.pk

### OLD CODE

    
class OldScannedDoc(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')
    
    image_hash = models.CharField(max_length=64, blank=True)
    large = models.ImageField(upload_to='scanned_doc_large')
    thumbnail = models.ImageField(upload_to='scanned_doc_thumbnail')
    notes = models.TextField(blank=True, default="")
    scan_time = models.DateTimeField(blank=True,null=True)
    
    class Meta:
        ordering = ['-id']

class AbstractScannedDoc(models.Model):
    class Meta:
        abstract = True
    
    related_object_name = None
        
    def get_my_large_upload_path(self):
        pass
    
    def get_my_thumbnail_upload_path(self):
        pass

    @property
    def related_object(self):
        if self.related_object_name is None:
            return None
        else:
            return getattr(self, self.related_object_name)

    image_hash = models.CharField(max_length=64)
    large = models.ImageField(upload_to=get_my_large_upload_path)
    thumbnail = models.ImageField(upload_to=get_my_thumbnail_upload_path)
    notes = models.TextField(blank=True, default="")
    create_time = models.DateTimeField()
    modified_time = models.DateTimeField(auto_now=True)
    
class OldTestCard(AbstractScannedDoc):
    """
    Old format model that represents a scanned test card.
    
    In order to accommodate the new format, the name of the model has been
    changed as well as db_table.
    """
    related_object_name = 'retain'
    
    def get_my_large_upload_path(self):
        return 'testcards'
    
    def get_my_thumbnail_upload_path(self):
        return 'testcards_thumbnail'

    retain = models.ForeignKey('Retain', null=True)
    status = models.CharField(max_length=25,choices=STATUS_CHOICES,default='Pending QC')
    
    def __unicode__(self):
        return "%s" % (self.retain)
    
    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            r = Retain.objects.get(pk=bc_key)
        except Retain.DoesNotExist:
            r = None
        return OldTestCard(
                    retain=r,
                    **document_create_kwargs)


class OldRMTestCard(AbstractScannedDoc):

    related_object_name = 'retain'
    
    def get_my_large_upload_path(self):
        return 'rmtestcards'
    
    def get_my_thumbnail_upload_path(self):
        return 'rmtestcards_thumbnail'
    
    retain = models.ForeignKey('RMRetain', null=True)
    status = models.CharField(max_length=25,choices=RM_STATUS_CHOICES,default='Pending QC')
    
    def __unicode__(self):
        return "%s" % (self.retain)
    
    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            r = RMRetain.objects.get(pk=bc_key)
        except RMRetain.DoesNotExist:
            r = None
        return RMTestCard(
                    retain=r,
                    **document_create_kwargs)
        
    @staticmethod
    def get_absolute_url(self):
        return "/django/access/ingredient/pin_review/%s/" % self.retain.pin

class OldBatchSheet(AbstractScannedDoc):

    related_object_name = 'lot'
    
    def get_my_large_upload_path(self):
        return 'batchsheets'
    
    def get_my_thumbnail_upload_path(self):
        return 'batchsheets_thumbnail'
    
    lot = models.ForeignKey('Lot', null=True)
    status = models.CharField(max_length=25, default='')

    class Meta:
        ordering = ['-id']
        
    def __unicode__(self):
        if self.lot is None:
            return "Invalid"
        return "%s" % (self.lot.number)

    @staticmethod
    def create_from_referred_object_from_bc_key(bc_key, document_create_kwargs):
        try:
            l = Lot.objects.get(number=bc_key)
        except Lot.DoesNotExist:
            l = None
        return OldBatchSheet(
                    lot=l,
                    **document_create_kwargs)

class OldGenericTestCard(AbstractScannedDoc):

    def get_related_object(self):
        return None
    
    def get_my_large_upload_path(self):
        return 'generctestcards'
    
    def get_my_thumbnail_upload_path(self):
        return 'generictestcards_thumbnail'
    
    def get_my_status_choices(self):
        return STATUS_CHOICES
    
    def get_my_status_default(self):
        return 'Pending QC'
