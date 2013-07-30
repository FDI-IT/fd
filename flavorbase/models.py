from datetime import date

from django.db import models
#from django.contrib.contenttypes.models import ContentType
#from django.contrib.contenttypes import generic
NATART_CHOICES = (
    ('N/A','N/A'),
    ('Nat','Nat'),
    ('Art','Art'),
    ('NFI','NFI'),
    ('NI','NI'),
)
class Product(models.Model):
    """
    Info scrubbed from Norma's spreadsheet
    """
    natart = models.CharField(max_length=3,blank=True,choices=NATART_CHOICES)
    name = models.CharField(max_length=60,)
    experimental_number = models.PositiveSmallIntegerField(blank=True,null=True)
    experimental_initials = models.CharField(max_length=2, blank=True)
    production_number = models.PositiveIntegerField(blank=True,null=True)
    approved_promote = models.CharField(max_length=20,blank=True)
    location_code = models.CharField(max_length=20, blank=True)
    oc = models.BooleanField(default=False)
    gmo_free = models.BooleanField(default=True)
    kosher = models.BooleanField(default=False)
    prop_sixtyfive = models.BooleanField(default=False)
    no_msg = models.BooleanField(default=True)
    no_pg = models.BooleanField(default=False)
    no_diacetyl = models.BooleanField(default=True)
    heat_stable = models.BooleanField(default=False)
    dup = models.BooleanField(default=False)
    export_only = models.BooleanField(default=False)
    liquid = models.BooleanField(default=True)
    conc = models.BooleanField(default=False)
    emulsion = models.BooleanField(default=False)
    dry = models.BooleanField(default=False)
    oil_soluble = models.BooleanField(default=False)
    spg = models.DecimalField(decimal_places=3,max_digits=4,)
    flash = models.SmallPositiveIntegerField(default=0)
    customer = models.CharField(max_length=60,blank=True)
    memo = models.TextField(blank=True)
    misc_sul = models.DecimalField(decimal_places=2, max_digits=4)
    misc_app = models.
    
    
    flavor = models.OneToOneField(Flavor)
    appearance = models.CharField(max_length=100, blank=True)
    organoleptic_properties = models.CharField(max_length=100, blank=True)
    testing_procedure = models.TextField(blank=True)
    flash_point = models.FloatField(blank=True, null=True)
    specific_gravity = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True)
    retain_on_file = models.BooleanField(default=False)
    original_card = models.FileField(upload_to='qc_original_cards')
    objects = ProductInfoManager()
    
