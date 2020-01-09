# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime, timedelta, date
import re
import queue
import os
from operator import itemgetter
import collections
import csv
import reversion

from django.db import models, connection
from django.db.models import Q, F
# from django.db.models.signal import pre_save
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes import fields
from django.db import transaction
from django.contrib.postgres.fields import ArrayField
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from hazards.models import HazardCategory, GHSIngredient, HazardAccumulator
from hazards.tasks import calculate_flavor_hazards, update_hazard_dict_with_flammable_hazards
from hazards.views import create_fli_url, create_sds_url
from hazards.initial_data import pcode_dict, HazardClassDict
#from access.controller import hazard_list, acute_toxicity_list
#from access.controller import make_hazard_class, skin_hazard_dict, eye_hazard_dict, respiratory_hazard_dict, germ_mutagenicity_dict

from pluggable.sets import AncestorSet

one_hundred = Decimal('100')
hundredths = Decimal('0.00')
zero = Decimal('0')
one_thousand = Decimal('1000')

flavor_api_fields = [
    'prefix',
    'natart',
    'number',
    'name',
    'phase',
    'product_category',
    'solubility',
    'wonf_type',
    'kosher',
    'country_of_origin',
    'valid',
    'sold',
    'approved',
    'flashpoint',
    #'spg',
    'vegan',
    'ovo_vegan',
    'no_pg',
    'discontinued',
    # 'new_gmo',
    'id',
    'unitprice',
    # 'tags',
    # 'applications',
    'label_type'
]

field_status_dict = {
    "N/A": "blue",
    "Expired": "red",
    "Verified": "green",
    "Unverified": "red",
    "Single Verification": "red",
    "Verification Mismatch": "red",
    "No Documents": "red",
}

flavor_field_to_doctype_dict = {
    'vegan': 'vegan',
    # 'halal': 'halal',
    # 'kosher': 'kosher',
    'microsensitive': 'specsheet',
    # 'natural_document_on_file': 'natural',
    'new_gmo': 'GMO',
    # 'nutri': 'nutri',
    'organic_compliant': 'organic',
    # 'rm_ingredient_statement': 'specsheet',
    # 'salmonella': 'COA',
    'allergen': 'allergen',
    'sulfites': 'allergen', }

rm_field_to_doctype_dict = {
    # 'Certificate of Insurance': 'COI',
    # 'Ingredient Breakdown': 'ingbreak',
    # 'Letter Of Guarantee': 'LOG',
    'vegan': 'vegan',
    'cas': 'sds',
    # 'celery': 'allergen',
    'country_of_origin': 'origin',
    # 'crustacean': 'allergen',
    # 'eggs': 'allergen',
    # 'fish': 'allergen',
    'halal': 'halal',
    #'kosher': 'kosher',
    # 'lupines': 'allergen',
    'microsensitive': 'specsheet',
    # 'milk': 'allergen',
    # 'mollusks': 'allergen',
    # 'mustard': 'allergen',
    'natural_document_on_file': 'natural',
    'new_gmo': 'GMO',
    'nutri': 'nutri',
    'organic_compliant': 'organic',
    # 'peanuts': 'allergen',
    'rm_ingredient_statement': 'specsheet',
    'salmonella': 'COA',
    # 'sesame': 'allergen',
    # 'soybeans': 'allergen',
    # 'sunflower': 'allergen',
    # 'treenuts': 'allergen',
    # 'wheat': 'allergen',
    # 'yellow_5': 'allergen',
    'allergen': 'allergen', }

NATART_CHOICES = (
    ('N/A','N/A'),
    ('Nat','Nat'),
    ('Art','Art'),
    ('NFI-N','NFI-N'),
    ('NFI-A','NFI-A'),
    #('NI','NI'),
    ('Nat w/ 0.1% Art Topnote', 'TTB'),
)

YES_NO_CHOICES = (
    ('Yes','Yes'),
    ('No','No'),
)

#New fields
PHASE_CHOICES = (
    ('Liquid','Liquid'),
    ('Powder','Powder'),
    ('Undetermined', 'Undetermined'),
)

LIQUID_CATEGORY_CHOICES = (
    ('Solution', 'Solution'),
    ('Reaction', 'Reaction'),
    ('Emulsion', 'Emulsion'),
    ('Concentrate', 'Concentrate'),
    ('Syrup', 'Syrup'),
    ('Syrup Base', 'Syrup Base'),
    ('Flavored Syrup', 'Flavored Syrup'),
)

DRY_CATEGORY_CHOICES = (
    ('Spray Dry', 'Spray Dry'),
    ('Rub', 'Rub'),
    ('Spice Blend', 'Spice Blend'),
    ('Base', 'Base'),
    ('Powdered Flavor', 'Powdered Flavor'),
    ('Flavorcoat', 'Flavorcoat'),
)
PRODUCT_CATEGORY_CHOICES = (
    LIQUID_CATEGORY_CHOICES + DRY_CATEGORY_CHOICES
)

WONF_TYPE_CHOICES = (
    ('WONF', 'WONF'),
    ('Type', 'Type'),
)

# Use NullBooleanField for these fields instead
# ORGANIC_COMPLIANT_CHOICES = (
#     ('Not OC', 'Not OC'),
#     ('OC', 'OC'),
# )
#
SOLUBILITY_CHOICES = (
    ('Water', 'Water'),
    ('Oil', 'Oil'),
    ('Water Dispersable', 'Water Dispersable'),
)

KOSHER_CHOICES = (
    ('Not Assigned', 'Not Assigned'),
    ('Not Kosher', 'Not Kosher'),
    ('All','All'),
    ('Meat','Meat'),
    ('Dairy','Dairy'),
    ('Pareve','Pareve'),
    ('Passover','Passover'),
)

HALAL_CHOICES = (
    # ('Not Assigned', 'Not Assigned'),
    ('Not Halal', 'Not Halal'),
    # ('All','All'),
    # ('Meat','Meat'),
    # ('Dairy','Dairy'),
    # ('Pareve','Pareve'),
    # ('Passover','Passover'),
    ('Halal Certified', 'Halal Certified'),
    ('Halal Compliant', 'Halal Compliant'),
)

GMO_CHOICES = (
    ('GMO Free','GMO Free'),
    ('Genetically Modified', 'Genetically Modified'),
    ('GMO Non-Detect', 'GMO Non-Detect')
)

SOLVENT_NAMES = {
    1983:'Neobee',
    829:'Triacetin',
    86:'Benzyl Alcohol',
    703:'PG',
    321:'ETOH',
    100:'Water',
    473:'Lactic Acid',
    25:'Iso Amyl Alcohol',
    758:'Soybean Oil',
    6403:'Safflower Oil',
    1478:'Dextrose',
    5928:'Radia',
}

RISK_ASSESSMENT_CHOICES = (  #NEW
    (0, "Antimicrobial"),
    (1, "Regularly Monitored"),
    (2, "Bacteriostatic/Non-Supportive"),
    (3, "Hot Packed/Heat Treated"),
    (4, "Low pH, <3.9"),
    (5, "COA Salmonella"),
    (6, "Spray Dried"),
    (7, "Pending"),
    (8, "Intermediate Only"),
)

DIACETYL_PKS = [262, 263, 1791]
PG_PKS = [670,6717]

def get_next_renumber():
    if 'access_integratedproduct' in connection.introspection.table_names():
        renumber_base = 23000
        while True:
            if not Flavor.objects.filter(number = renumber_base).exists():
                return renumber_base
                break
            else:
                renumber_base += 1
    else:
        return None

def get_next_flavorid():
    if 'access_integratedproduct' in connection.introspection.table_names():
        if Flavor.objects.count() > 0:
            return Flavor.objects.all().order_by('-id')[0].id+1
        else:
            return 1
    else:
        return None

def get_next_rawmaterialcode():
    if 'access_ingredient' in connection.introspection.table_names():
        if Ingredient.objects.count() > 0:
            return Ingredient.objects.all().order_by('-rawmaterialcode')[0].rawmaterialcode+1
        else:
            return 1
    else:
        return None

#this is used in forms
def get_next_experimentalnum():
    try:
        return ExperimentalLog.objects.all().order_by('-experimentalnum')[0].experimentalnum+1
    except:
        return 1

class FormulaTree(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="formula_rows", db_index=True, on_delete=models.CASCADE)
    lft = models.PositiveSmallIntegerField()
    rgt = models.PositiveSmallIntegerField()
    formula_row = models.ForeignKey('Formula', null=True, blank=True,on_delete=models.CASCADE)
    node_ingredient = models.ForeignKey('Ingredient', null=True, blank=True, db_index=True,on_delete=models.CASCADE)
    node_flavor = models.ForeignKey('Flavor', null=True, blank=True,on_delete=models.CASCADE)
    row_id = models.PositiveSmallIntegerField(null=True, blank=True)
    parent_id = models.PositiveSmallIntegerField(null=True, blank=True)
    weight = models.DecimalField(decimal_places=3,
            max_digits=7,)
    weight_factor = models.DecimalField(decimal_places=15, max_digits=16)
    leaf = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['root_flavor', 'lft']

    #returns the depth of a formula tree node (recursively)
    @property
    def depth(self):
        #base case: node is root node, depth = 0
        if(self.row_id == 0):
            return 0
        else:
            parent_node = FormulaTree.objects.get(root_flavor=self.root_flavor, row_id=self.parent_id)
            return 1 + parent_node.depth

    @property
    def indivisible_leaf(self):
        if self.rgt == self.lft + 1:
            return True
        elif self.node_flavor.spraydried == True:
            return True
        elif self.node_flavor.yield_field != 100:
            return True
        elif self.node_flavor.prefix == 'SN':
            return True
        else:
            return False

    @property
    def node_label(self):
        if self.lft == 0:
            return self.root_flavor.name
        else:
            return "%s -- %slbs<br>%s" % (self.node_ingredient.id, self.weight, self.node_ingredient.short_prefixed_name(trim_length=25), )

    @property
    def relative_cost(self):
        return self.get_exploded_cost()

    def __str__(self):
        return "%s: l%s r%s parent%s" % (self.root_flavor.__str__(), self.lft, self.rgt, self.parent_id)

class LeafWeight(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="leaf_weights", db_index=True,on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient', db_index=True,on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=3, max_digits=7)
    quant_weight = models.IntegerField(null=True)

class IndivisibleLeafWeight(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="indivisible_leaf_weights", db_index=True,on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient', db_index=True,on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=3, max_digits=7)
    quant_weight = models.IntegerField(null=True)

    def __str__(self):
        return "%s, %s" % (self.ingredient, self.weight)


class Formula(models.Model):
    """Constituent ingredients of a particular approved formula.
    Referenced by Flavor number.

    Depends on RawMaterial
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    # Flavor points here; one flavor points to many ingredients

    # The below fields are added to create true foreign keys to the
    # related tables, not just the pseudo keys used by the legacy joins
    # product = models.ForeignKey('Product', related_name='ingredients')
    acc_flavor = models.PositiveIntegerField()
    # Points to the Ingredient table, which actually may be a flavor or rawmat
    acc_ingredient = models.PositiveIntegerField()

    flavor = models.ForeignKey('Flavor',on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient',on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=3,
            max_digits=7,
            )
    totalweight = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            default=Decimal('0'))
    flavorextendedprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            default=Decimal('0'))
    price = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            default=Decimal('0'))
    discontinued = models.BooleanField(default=False)
    batchamount = models.PositiveIntegerField(default=0)
    machinebatch = models.PositiveIntegerField(default=0)
    rawmaterialcode = models.PositiveIntegerField(default=0)
    # ^not really used since formulas point to PINs not primary keys to the
    # Ingredient table.

    # this helps the import-data management command know which order to
    # import tables so that foreign-key dependencies are met

    class Meta:
        db_table = 'access_integratedformula'
        ordering = ['acc_flavor',]

    def __str__(self):
        return "%s-%s: %s %s lbs" % (self.flavor.prefix, self.flavor.number, self.ingredient.__str__(), self.amount)

    def get_exploded_weight(self, weight_factor):
        return Decimal(self.amount * weight_factor)

    def get_admin_url(self):
        return "BORKEN!"

    def get_exploded_cost(self, weight_factor=1):
        if self.ingredient.is_gazinta:
            g = self.gazinta()
            y = g.yield_field

            if y == 0 or y == 100:
                rmc = g.rawmaterialcost
            else:
                if g.rawmaterialcost is None or y is None:
                    print("Updating %s" % g)
                    g.update_cost()
                rmc = g.rawmaterialcost * y / Decimal('100')

        else:
            rmc = self.ingredient.unitprice
        try:
            return self.amount * weight_factor * rmc / Decimal('1000')
        except TypeError:
            return Decimal('0')

    @property
    def relative_cost(self, weight_factor=1):
        rmc = self.ingredient.unitprice
        try:
            return self.amount * weight_factor * rmc / Decimal('1000')
        except TypeError:
            return Decimal('0')

    def gazinta(self):
        try:
            return self.ingredient.sub_flavor
        except:
            raise FormulaException("%s contains an invalid formula row trying to point to flavor number: %s" %
                                  (self.flavor, self.ingredient.flavornum))



class IngredientSuperClass(models.Model):
    # rawmaterialcode = models.PositiveIntegerField(
    #         primary_key=True,
    #         db_column='RawMaterialCode',
    #         blank=True,
    #         default=get_next_rawmaterialcode)
    #
    # id = models.PositiveIntegerField("PIN",
    #                                   db_column='ProductID',
    #                                   default = get_next_rawmaterialcode)
    cas = models.CharField(
            max_length=20,
            blank=True,
            null=True,
            default="")

    cas2 = models.CharField(
            max_length=20,
            blank=True,
            default="",
            null=True

            )

    #calculate cas 1 percentage from cas 2 percentage - default 0%
    cas2_percentage = models.DecimalField("CAS 2 Percentage",
        max_digits=7,
        decimal_places=2,
        default=Decimal(0),
        )

    art_nati = models.CharField(
                max_length=50,
                db_column='ART_NATI',
                choices=NATART_CHOICES)
    kosher = models.CharField(
                max_length=20,
                db_column='KOSHER',
                blank=True,
                choices=KOSHER_CHOICES)
    kosher_code = models.CharField(
                max_length=50,
                db_column='Kosher Code',
                blank=True)
    # halal = models.NullBooleanField(default=False)
    halal = models.CharField(
            max_length=20,
            blank=True,
            null=True,
            choices=HALAL_CHOICES,
            default=None,
            )
    halal_code = models.CharField(
                max_length=50,
                blank=True)
    new_gmo = models.CharField(
                'New GMO',
                max_length=50,
                choices=GMO_CHOICES,
                db_column='NEW_GMO',
                null=True,
                blank=True)
    natural_document_on_file = models.BooleanField(
                db_column='Natural_Document_On_File',
                blank=True,
                default=False)
    allergen = models.CharField(
                max_length=100,
                db_column='Allergen',
                blank=True)
    microsensitive = models.CharField(
                max_length=20,
                db_column='Microsensitive',
                blank=True,
                null=True)

    rm_ingredient_statement = models.CharField("RM Ingredient Statement", max_length=200, blank=True, null=True)

    country_of_origin = models.CharField(max_length=200,blank=True,null=True)


    eggs = models.BooleanField('Eggs',blank=True, default=False)
    milk = models.BooleanField('Milk',blank=True, default=False)
    soybeans = models.BooleanField('Soybeans', blank=True, default=False)
    peanuts = models.BooleanField('Peanuts', blank=True, default=False)
    fish = models.CharField("Fish", blank=True, null=True, max_length=100)
    treenuts = models.CharField("Treenuts", blank=True, null=True, max_length=100)
    crustacean = models.CharField("Crustacean", blank=True, null=True, max_length=100)

    wheat = models.BooleanField('Wheat', blank=True, default=False)
    sunflower = models.BooleanField('Sunflower', blank=True, default=False)
    sesame = models.BooleanField('Sesame', blank=True, default=False)
    mollusks = models.BooleanField('Mollusks', blank=True, default=False)
    mustard = models.BooleanField('Mustard', blank=True, default=False)
    celery = models.BooleanField('Celery', blank=True, default=False)
    lupines = models.BooleanField('Lupines', blank=True, default=False)
    yellow_5 = models.BooleanField('Yellow 5', blank=True, default=False)

    salmonella = models.NullBooleanField(default=False)
    vegan = models.NullBooleanField(default=False)
    organic_compliant = models.NullBooleanField(default=False)
    organic_certified = models.NullBooleanField(default=False)

    barley_gluten = models.BooleanField("Barley Gluten", blank=True, default=False)
    sulfites_ppm = models.PositiveSmallIntegerField('Sulfites(PPM)', default=0, blank=True)
    class Meta:
        abstract=True

    @property
    def get_label(self, label):
        return self.__get_label(label)

class Ingredient(IngredientSuperClass):
    """Raw materials for use in production.

    The unique indentifier for this table is 'rawmaterialcode'.
    Multiple unique 'rawmaterialcode' fields can exist with the same
    productid; this represents equivalent raw materials from alternate
    suppliers.
    """


    rawmaterialcode = models.PositiveIntegerField(
            primary_key=True,
            db_column='RawMaterialCode',
            blank=True,
            default=get_next_rawmaterialcode)
    id = models.PositiveIntegerField("PIN",
                                      db_column='ProductID',
                                      default = get_next_rawmaterialcode)
    # cas = models.CharField(
    #         max_length=15,
    #         blank=True,)

    # art_nati = models.CharField(
    #         max_length=50,
    #         db_column='ART_NATI',
    #         choices=NATART_CHOICES)
    prefix = models.CharField(
            max_length=60,
            db_column='PREFIX',
            blank=True)
    product_name = models.CharField(
            max_length=70,
            db_column='ProductName')
    part_name2 = models.CharField(
            max_length=60,
            db_column='PART_NAME2',
            blank=True)
    alternate_name = models.CharField(
            max_length=100,
            blank=True,
            null=True)
    memo = models.TextField(
            blank=True)
    description = models.CharField(
            max_length=60,
            db_column='DESCRIPT',
            blank=True)
    comments = models.TextField(
            "Comments (Organoleptics)",
            db_column='COMMENTS',
            blank=True)
    # points back to Flavor if this is a complex Ingredient
    flavornum = models.IntegerField(
            db_column='PRODNUM',
            null=True,
            blank=True)
    # "real" foreign key
    sub_flavor = models.ForeignKey(
            'Flavor',
            null=True,
            blank=True,
            related_name="gazinta",on_delete=models.CASCADE)
    discontinued = models.BooleanField(
            db_column='Discontinued',
            blank=True,
            default=False)
    experimental = models.BooleanField(blank=True, default=False) #AKDJFLKJADLFDAFLADFAFKDADFDAfkj
    unitprice = models.DecimalField(
            decimal_places=3,
            max_digits=10,
            db_column='UnitPrice',)
    purchase_price_update = models.DateTimeField(
            "Date of last purchase price update",
            db_column='LSTPRICDAT',
            blank=True,
            default=datetime(1990,1,1))
    date_ordered = models.DateTimeField(
            db_column='Date_Ordered',
            blank=True,
            default=datetime(1990,1,1))
    suppliercode = models.CharField(
            max_length=50,
            db_column='SupplierCode',
            blank=True)
    supplier = models.ForeignKey('Supplier', blank=True, default=None, null=True,on_delete=models.CASCADE)

    fldr = models.CharField(
            max_length=50,
            db_column='FLDR',
            blank=True)
    # kosher = models.CharField(
    #         max_length=20,
    #         db_column='KOSHER',
    #         blank=True,
    #         choices=KOSHER_CHOICES)
    # kosher_code = models.CharField(
    #         max_length=50,
    #         db_column='Kosher Code',
    #         blank=True)
    lastkoshdt = models.DateTimeField(
            db_column='LASTKOSHDT',
            blank=True,
            default=datetime(1990,1,1))
    # halal = models.CharField(
    #         max_length=20,
    #         blank=True,
    #         choices=HALAL_CHOICES)
    # halal_code = models.CharField(
    #         max_length=50,
    #         blank=True)
    solution = models.DecimalField(
            decimal_places=3,
            max_digits=5,
            db_column='SOLUTION',
            blank=True,
            default=0)
    solvent = models.CharField(
            max_length=10,
            db_column='SOLVENT',
            blank=True)

    fema = models.CharField(
            max_length=20,
            db_column='FEMA',
            blank=True)
    # gmo = models.CharField(
    #         max_length=50,
    #         choices=YES_NO_CHOICES,
    #         db_column='GMO',
    #         blank=True)
    # new_gmo = models.CharField(
    #         'New GMO',
    #         max_length=50,
    #         choices=GMO_CHOICES,
    #         db_column='NEW_GMO',
    #         blank=True)
    # natural_document_on_file = models.BooleanField(
    #         db_column='Natural_Document_On_File',
    #         blank=True,
    #         default=False)
    # allergen = models.CharField(
    #         max_length=100,
    #         db_column='Allergen',
    #         blank=True)
    sprayed = models.BooleanField(
            db_column='Sprayed',
            blank=True,
            default=False)
    # microsensitive = models.CharField(
    #         max_length=20,
    #         db_column='Microsensitive',
    #         blank=True)
    prop65 = models.BooleanField(
            db_column='Prop65',
            blank=True,
            default=False)
    nutri = models.BooleanField(
            db_column='Nutri',
            blank=True,
            default=False)
    transfat = models.BooleanField(
            db_column='TransFat',
            blank=True,
            default=False)
    sulfites = models.BooleanField(blank=True, default=False)
    # sulfites_ppm = models.PositiveSmallIntegerField()

    gluten_ppm = models.PositiveIntegerField(default=0)

    # eggs = models.BooleanField(blank=True, default=False)
    # milk = models.BooleanField(blank=True, default=False)
    # soybeans = models.BooleanField(blank=True, default=False)
    # peanuts = models.BooleanField(blank=True, default=False)

    # fish_bass = models.BooleanField("Fish (bass)",blank=True, default=False)
    # fish_flounder = models.BooleanField("Fish (flounder)",blank=True, default=False)
    # fish_cod = models.BooleanField("Fish (cod)",blank=True, default=False)
    #
    # treenuts_almond = models.BooleanField("Tree nuts (almond)",blank=True, default=False)
    # treenuts_pecan = models.BooleanField("Tree nuts (pecan)",blank=True, default=False)
    # treenuts_walnut = models.BooleanField("Tree nuts (walnut)",blank=True, default=False)
    #
    # crustacean_crab = models.BooleanField("Crustacean (crab)",blank=True, default=False)
    # crustacean_lobster = models.BooleanField("Crustacean (lobster)",blank=True, default=False)
    # crustacean_shrimp = models.BooleanField("Crustacean (shrimp)",blank=True, default=False)

    # fish = models.CharField("Fish", blank=True, null=True, max_length=100)
    # treenuts = models.CharField("Treenuts", blank=True, null=True, max_length=100)
    # crustacean = models.CharField("Crustacean", blank=True, null=True, max_length=100)

    # wheat = models.BooleanField(blank=True, default=False)
    # sunflower = models.BooleanField(blank=True, default=False)
    # sesame = models.BooleanField(blank=True, default=False)
    # mollusks = models.BooleanField(blank=True, default=False)
    # mustard = models.BooleanField(blank=True, default=False)
    # celery = models.BooleanField(blank=True, default=False)
    # lupines = models.BooleanField(blank=True, default=False)
    # yellow_5 = models.BooleanField(blank=True, default=False)
    has_allergen_text = models.BooleanField(blank=True, default=False)

    hazardous = models.BooleanField(blank=True, default=False)

    #caramel_color = models.BooleanField(blank=True,default=False)
    # rm_ingredient_statement = models.CharField("RM Ingredient Statement", max_length=200, blank=True, null=True)

    package_size = models.DecimalField("Package size (lbs)", max_digits=7,decimal_places=2)
    minimum_quantity = models.DecimalField("Minimum quantity (lbs)", max_digits=7,decimal_places=2)
    quantity_discount = models.CharField(max_length=50, blank=True)
    fob_point = models.CharField("FOB point", max_length=50)
    lead_time = models.CharField(db_column='lead_time',max_length=50)
    solubility = models.CharField(max_length=50,
                                  choices=SOLUBILITY_CHOICES,
                                  blank=True,
                                  null=True),
    solubility_memo = models.CharField(max_length=50,blank=True)
    supplier_catalog_number = models.CharField(max_length=50,blank=True)



    # these values have something to do with inventory, or solutions, or gazintas?
    inventoryng = models.BooleanField(db_column='InventoryNG', blank=True, default=False)
    kencheck = models.BooleanField(db_column='Kencheck', blank=True, default=False)
    # these values were to be part of an inventory system that was never done
    unitsinstock = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsInStock', blank=True, default=0)
    committed = models.DecimalField(decimal_places=2, max_digits=6, db_column='COMMITTED', blank=True, default=0)
    reorderlevel = models.DecimalField(decimal_places=2, max_digits=6, db_column='ReorderLevel', blank=True, default=0)
    old_lead_time = models.DecimalField(decimal_places=2, max_digits=6, db_column='LEAD_TIME', blank=True, default=0, null=True)
    unitsonorder = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsOnOrder', blank=True, default=0)
    # simply not used
    supplierid = models.PositiveIntegerField(db_column='SupplierID',  blank=True, default=0)
    inventory = models.DecimalField(decimal_places=4, max_digits=10, default=0)


    boolean_allergens = [
        'eggs',
        'milk',
        'peanuts',
        'soybeans',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
        'barley_gluten',
    ]

    text_allergens = [
        'fish',
        'crustacean',
        'treenuts',

    ]


    location_code_n = fields.GenericRelation('LocationCode')
    #cas_status = models.CharField(max_length=50,blank=True)
    hazard_set = models.ManyToManyField(HazardCategory, through='FDIIngredientCategoryInfo')

    #this is used in labelview to easily get the latest rmretain when given a pin number
    latest_retain_pk = models.PositiveIntegerField(blank=True, null=True)

    total_sugars = models.DecimalField("Total Sugars", max_digits=7,decimal_places=3, blank=True, null=True)
    added_sugars = models.DecimalField("Added Sugars", max_digits=7,decimal_places=3, blank=True, null=True)

    # organic_compliant = models.NullBooleanField()

    hazards_approved = models.BooleanField(default=False)

    @staticmethod
    def anonymize():
        supplier_code_queue = queue.Queue()
        supplier_codes = ("abt", 'cna','kerry','vigon','FDI')
        for word in supplier_codes:
            supplier_code_queue.put(word)

        for rm in Ingredient.objects.all():
            lorem_one = q.get()
            lorem_two = q.get()
            lorem_three = q.get()
            if rm.sub_flavor == None:
                rm.product_name = "%s %s" % (lorem_one, lorem_two)
            else:
                rm.product_name = rm.sub_flavor.name

            rm.part_name2 = "%s" % (lorem_three)
            rm.description = "%s %s %s" % (lorem_one, lorem_two, lorem_three)

            rm.kosher_code = "kosh"

            suppliercode = supplier_code_queue.get()
            rm.suppliercode = suppliercode
            supplier_code_queue.put(suppliercode)

            rm.save()

            q.put(lorem_one)
            q.put(lorem_two)
            q.put(lorem_three)
            print(rm)

    @property
    def url(self):
        return "/access/ingredient/pin_review/%s/" % self.id

    @property
    def info_slice(self):
        return {
            'unit_price':str(self.unitprice).rstrip('0').rstrip('.'),
            'allergen':self.allergen,
            'sulfites_ppm':self.sulfites_ppm,
        }

    def get_absolute_url(self):
        #REMOVED 2/18 - We want the pin review page for every raw material now because by default, raw materials will be discontinued
#         if self.discontinued == False:
#             return "/access/ingredient/pin_review/%s/" % self.id
#         else:
#             return "/access/ingredient/%s/" % self.rawmaterialcode

        return "/access/ingredient/pin_review/%s/" % self.id

    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
            if key == 'art_nati':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'kosher':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'allergen':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'prop65':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    if my_arg == 'False':
                        arg_list.append(False)
                    else:
                        arg_list.append(True)
                string_kwargs[keyword] = arg_list

                '''else:
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(bool(int(my_arg)))
                string_kwargs[keyword] = arg_list
                '''
        return string_kwargs

    @staticmethod
    def get_obj_from_softkey(softkey):
        try:
            return get_object_or_404(Ingredient, id=softkey)
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey, discontinued=False)[0]
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey)[0]
        except:
            pass

        return None


    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            return Ingredient.objects.get(id=softkey)
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey, discontinued=False)[0]
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey)[0]
        except:
            pass
        return None

    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(Ingredient, id=softkey).get_absolute_url()
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey, discontinued=False)[0].get_absolute_url()
        except:
            pass
        try:
            return Ingredient.objects.filter(id=softkey)[0].get_absolute_url()
        except:
            pass

        return None

    @property
    def prefixed_name(self):
        if self.prefix != "":
            return "%s %s" % (self.prefix, self.product_name)
        else:
            return self.product_name

    @property
    def short_prefixed_name(self):
        if len(self.prefixed_name) > 18:
            if self.prefix != "":
                s = "%s %s" % (self.prefix, self.product_name)
                return "%s..." % s[:18]
            else:
                return "%s..." % self.product_name[:18]
        else:
            return self.prefixed_name

    @property
    def short_remainder_name(self):
        if len(self.prefixed_name) > 18:
            return "...%s %s" % (self.prefixed_name[18:], self.part_name2)
        else:
            return self.part_name2

    @property
    def supplier_list(self):
        for i in Ingredient.objects.filter(id=self.id):
            yield i.suppliercode

    @property
    def long_name(self):
        if self.sub_flavor:
            my_name = "%s-%s %s %s %s" % (self.sub_flavor.prefix, self.sub_flavor.number, self.art_nati, self.sub_flavor.table_name, self.sub_flavor.label_type)
        else:
            my_name = " ".join((self.art_nati, self.prefix, self.product_name, self.part_name2))

        if self.discontinued:
            my_name = "DISCONTINUED: %s" % my_name

        return my_name.strip()

    @property
    def table_name(self):
        if self.sub_flavor:
            my_name = "%s %s" % (self.sub_flavor.table_name, self.sub_flavor.label_type)
        elif self.discontinued:
            my_name = "DISCONTINUED: %s %s" % (self.product_name, self.part_name2)
        else:
            my_name = "%s %s" % (self.product_name, self.part_name2)
        return my_name.strip()

    @property
    def name(self):
        if self.sub_flavor:
            my_name = "%s %s" % (self.sub_flavor.table_name, self.sub_flavor.label_type)
        else:
            my_name = self.table_name
        return my_name.strip()

    @property
    def purchase_price_update_short(self):
        return self.purchase_price_update.date()

    @staticmethod
    def get_formula_ingredient(number):
        if number == '':
            return None
        if 'f' in number:
            number_tup = number.partition('f')
            number = number_tup[0] + number_tup[2]
            return Ingredient.objects.get(sub_flavor__number=number)
        else:
            return Ingredient.objects.filter(id=number).order_by('discontinued')[0]

    @transaction.atomic
    def update_price(self, new_price, update_time=None):
        from solutionfixer.models import Solution
        #prepare all valid solutions (contain both base and solvent) for further querying
        valid_solutions = Solution.objects.exclude(my_base=None).exclude(my_solvent=None)

        if update_time == None:
            update_time = datetime.now()
        try:
            dec_new_price = Decimal(new_price)
        except:
            dec_new_price = Decimal(str(new_price))
        delta = (dec_new_price - self.unitprice) / 1000

        if self.unitprice == dec_new_price: #if the price stays the same
            self.purchase_price_update = update_time
            self.save()

            #update lastspdate in products containing this raw material
            for lw in LeafWeight.objects.filter(ingredient=self):
                f = lw.root_flavor
                f.lastspdate = update_time
                f.save()

            #update purchase_price_update in solutions containing this raw material as a base or solvent
            for sol in valid_solutions.filter(Q(my_base=self) | Q(my_solvent=self)):
                i = sol.ingredient
                i.purchase_price_update = update_time
                i.save()

            return True
        else:
            self.unitprice = dec_new_price
            self.purchase_price_update = update_time
            self.save()
        thousandths = Decimal('0.000')

        flavors_updated_info = {}
        for leaf in LeafWeight.objects.select_related().filter(ingredient=self):
            f = leaf.root_flavor
            old_rmc = f.rawmaterialcost
            new_rmc = old_rmc + delta * leaf.weight
            f.rawmaterialcost = new_rmc
            f.lastspdate = update_time
            f.save()
            flavors_updated_info[f] = [old_rmc.quantize(hundredths), new_rmc.quantize(hundredths)]


        #use Q object to find solutions that contain this ingredient as a base OR solvent
        for sol in valid_solutions.filter(Q(my_base=self) | Q(my_solvent=self)):
            #here we calculate the new price of the solution containing this ingredient
            updated_solution_unit_price = sol.calculate_price()

            #update the price of the solution
            sol.ingredient.update_price(updated_solution_unit_price)

        #transaction.commit()
        return flavors_updated_info

    def is_solution_related(self):
        try:
            self.ing_obj
            return True
        except:
            pass
        if self.my_solvent.all().count() > 0:
            return True
        if self.my_base.all().count() > 0:
            return True

        return False

    #this is needed for the summary page after activating/discontinuing an ingredient.  try to get rid of this
    def get_related_links(self):
        related_links = []
        if self.sub_flavor:
            related_links.append(
                ('/access/%s/' % self.id, 'Flavor Formula')
            )

        if self.is_solution_related():
            related_links.append(
                ('/solutionfixer/pin_review/%s/' % self.id, 'Related Solutions')
            )
        related_links.append(('/access/ingredient/pin_review/%s/gzl/' % self.id, 'Gazinta List'))
        return related_links

    def get_product_tabs(self):
        product_tabs = [
                ('/access/ingredient/pin_review/%s/documentation/' % self.id, 'Documentation'),
                ('/solutionfixer/pin_review/%s/' % self.id, 'Related Solutions'),
                ('/access/ingredient/pin_review/%s/gzl/' % self.id, 'Gazinta List'),
            ]

        return product_tabs

#     product_tabs = [
#                        ('#flat_review_table','Formula'),
#                        ('/access/ajax_dispatch/?tn=consolidated&pk=%s' % self.pk,'Consolidated'),
#                        ('/access/ajax_dispatch/?tn=consolidated_indivisible&pk=%s' % self.pk, 'Consolidated-Indivisible'),
#                        ('/access/ajax_dispatch/?tn=explosion&pk=%s' % self.pk,'Explosion'),
#                        ('/access/ajax_dispatch/?tn=legacy_explosion&pk=%s' % self.pk,'Legacy Explosion'),
#                        ('/access/ajax_dispatch/?tn=revision_history&pk=%s' % self.pk, 'Revision History'),
#                        ('/access/ajax_dispatch/?tn=spec_sheet&pk=%s' % self.pk, 'Spec Sheet'),
#                        ('/access/ajax_dispatch/?tn=customer_info&pk=%s' % self.pk, 'Customer Info')
#                        ]
#         if self.retain_superset().count()>0:
#             product_tabs.append(('/access/ajax_dispatch/?tn=production_lots&pk=%s' % self.pk, 'Production Lots'))
#             product_tabs.append(('/access/ajax_dispatch/?tn=retains&pk=%s' % self.pk, 'Retains'))
#
#         try:
#             self.experimentallog
#             product_tabs.append(('/access/ajax_dispatch/?tn=experimental_log&pk=%s' % self.pk,'Experimental'))
#         except:
#             pass
#         try:
#             rmr = self.raw_material_record
#             if rmr:
#                 product_tabs.append(('/access/ajax_dispatch/?tn=raw_material_pin&pk=%s' % self.pk,'Raw Material PIN'))
#                 if Formula.objects.filter(ingredient=rmr).count() > 0:
#                     product_tabs.append(('/access/ajax_dispatch/?tn=gzl_ajax&pk=%s' % self.pk, 'GZL'))
#         except:
#             pass
#
#         return product_tabs

    def resembles(self, ingredient):
        if self.id != ingredient.id:
            return "id"
        if str(self.product_name) != str(ingredient.product_name):
            return "product_name"
        if str(self.part_name2) != str(ingredient.part_name2):
            return "part_name2"
        if str(self.description) != str(ingredient.description):
            return "description"
        if self.discontinued != ingredient.discontinued:
            return "discontinued"
        if str(self.prefix) != str(ingredient.prefix):
            return "prefix"
        if self.flavornum != ingredient.flavornum:
            return "flavornum"
        if self.solution != ingredient.solution:
            return "solution"
        if str(self.solvent) != str(ingredient.solvent):
            return "solvent"
        if str(self.suppliercode) != str(ingredient.suppliercode):
            return "suppliercode"
        return True

    def gzl_traversal(self, row_id=1,
                      parent_id=None, parent_flavors={},
                      formula_qs=Formula.objects.all()):
        """
        This should be just like Flavor.gzl_traversal, except the root
        is an ingredient instead of a flavor.
        """
        self.visited_flavors = {}
        self.row_id = 1
        def inner_traversal(flavor, weight,
                            parent_id, parent_flavors):
            try:
                ingredient = Ingredient.objects.get(sub_flavor=flavor)
            except:
                return
            for formula_row in formula_qs.filter(ingredient=ingredient):
                # get the relevant objects
                super_flavor = formula_row.flavor
                if not super_flavor.valid:
                    continue
#                if super_flavor in self.visited_flavors:
#                    continue
                else:
                    self.visited_flavors[super_flavor] = 1
                # verify there is no cycle on the new object
                if super_flavor.number in parent_flavors:
                    raise FormulaException("Cycle detected on %s: %s" %
                                              (super_flavor, parent_flavors))
                parent_flavors[flavor.number] = len(parent_flavors)

                new_weight = weight*formula_row.amount/1000
                yield (super_flavor, new_weight, self.row_id, parent_id)
                self.row_id += 1
                for duper_flavor in inner_traversal(
                                        super_flavor,
                                        new_weight,
                                        self.row_id -1,
                                        parent_flavors.copy()):
                    yield duper_flavor

        for formula_row in formula_qs.filter(ingredient=self):
            super_flavor = formula_row.flavor
            if not super_flavor.valid:
                continue
            if super_flavor in self.visited_flavors:
                continue
            else:
                self.visited_flavors[super_flavor] = 1
            new_weight = formula_row.amount
            yield (super_flavor, new_weight, self.row_id, None)
            self.row_id += 1
            for flavor in inner_traversal(super_flavor, new_weight, self.row_id-1, {}):
                yield flavor

    import_order = 1

    def get_allergen_text(self):
        i_allergens = []
        allergen_text = "None"
        for allergen in Ingredient.boolean_allergens + Ingredient.text_allergens:
            if getattr(self, allergen):
                if allergen in Ingredient.boolean_allergens:
                    i_allergens.append(allergen)
                elif allergen in Ingredient.text_allergens:
                    i_allergens.append('%s (%s)' % (allergen, getattr(self, allergen)))
        if len(i_allergens) > 0:
            allergen_text = "Yes: %s" % ','.join(i_allergens)

        return allergen_text

    class Meta:
        ordering = ['id']
        default_permissions = ('add', 'change', 'delete')
        # permissions = (
        #         ("changeprice_ingredient","Can change the price of raw materials"),
        #         ('view_ingredient',"Can view ingredients")
        # )
        db_table = 'access_ingredient'

    def save(self, *args, **kwargs):
        self.allergen = self.get_allergen_text()

        if self.id is None:
            self.id = self.rawmaterialcode
        try:
            self.sub_flavor = Flavor.objects.get(number=self.flavornum)
            self.fob_point = "n/a"
            self.lead_time = "0"
        except:
            pass
        super(Ingredient, self).save(*args, **kwargs)




    def get_fdnum(self):
        if self.sub_flavor:
            return self.sub_flavor.number
        else:
            return self.id

    def get_admin_url(self):
        return "/admin/access/ingredient/%s" % self.rawmaterialcode

    def get_review_url(self):
        return "/access/ingredient/pin_review/%s/" % self.id

    def get_branch(self):
        # this is where the Explode? field would be checke
        try:
            if (self.sub_flavor.yield_field == 100):
                return self.sub_flavor
        except:
            pass
        return self.sub_flavor

    @property
    def is_gazinta(self):
        if self.sub_flavor == None:
            return False
        else:
            return True

    def gazinta(self):
        return self.sub_flavor

    def __str__(self):
        if self.discontinued == True:
            return "DISCONTINUED: %s - %s %s %s" % (self.id,
                                   self.art_nati,
                                   self.prefix,
                                   self.product_name)
        return "%s - %s %s %s" % (self.id,
                                   self.art_nati,
                                   self.prefix,
                                   self.product_name)

    headers = (
                    ('id','PIN', 'width="30px"'),
                    ('art_nati','N-A', 'width="30px"'),
                    ('prefix','Prefix','width="30px"'),
                    ('name','Name', ''),
                    ('unitprice','Unit Price', 'width=86px class="{sorter: \'link-digit\'}"'),
                    ('purchase_price_update_short','Price Update', 'width=86px'),

                )

    def retain_list(self):
        from newqc.models import RMRetain
        rmrs = RMRetain.objects.filter(pin=self.id)
        csl = [rmrs[0],] # combed sorted list
        for x in range(1,len(rmrs)):
            if rmrs[x].similar_to(rmrs[x-1]):
                pass
            else:
                csl.append(rmrs[x])

        return csl

    @staticmethod
    def text_search(search_string):
        return Ingredient.objects.filter(
            Q(product_name__icontains=search_string) |
            Q(part_name2__icontains=search_string) |
            Q(description__icontains=search_string)
        )

    @staticmethod
    def fix_header(header):
        if header == 'purchase_price_update_short':
            return 'purchase_price_update'
        elif header == 'name':
            return 'product_name'
        else:
            return header

    def get_solution_formula_list(self):

        """
        This creates a FLI list for a raw material.  This is only used if the raw material is a solution.
        """
        formula_list = []

        from solutionfixer.models import Solution
        solution = Solution.objects.get(ingredient=self)

        solute_percentage = Decimal('0.01') * solution.percentage
        solute = Ingredient.objects.get(pk=solution.my_base_id)
        solute_weight = 1000 * solute_percentage

        formula_list.append(FormulaLineItem(ingredient=solute,
                                            weight=solute_weight))


        solvent_percentage = Decimal('0.01') * (Decimal('100') - solution.percentage)
        solvent = Ingredient.objects.get(pk=solution.my_solvent_id)
        solvent_weight = 1000 * solvent_percentage

        formula_list.append(FormulaLineItem(ingredient=solvent,
                                            weight=solvent_weight))

        return formula_list


    def set_hazards(self):

        if self.hazards_approved == True: #Once hazards have been assigned, don't reassign them
            pass

        else:
            '''
            Possible cases:
            1. The ingredient is a base raw material with or without a cas number.
                a. Without a cas number: No hazards will be set
                b. With a cas number: Simply take the hazards from the corresponding GHS Ingredient

            2. The ingredient is a SOLUTION: Create a hazard_list with FormulaLineItems and calculate the hazards using that
            '''

            from solutionfixer.models import Solution

            if Solution.objects.filter(ingredient=self).exists():
                solution = Solution.objects.get(ingredient=self)
                #Can only separate the components if the solution object has a valid solute and solvent ID
                if solution.my_base_id != None and solution.my_solvent_id != None:
                    formula_list = self.get_solution_formula_list()
                    hazard_dict = calculate_flavor_hazards(formula_list)

                    for hazard, category in hazard_dict.items():
                        if category != 'No' and type(category) != Decimal:
                            try:
                                category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                                            .get(category=category)
                            except ObjectDoesNotExist:
                                category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                                                .get(category=category + 'A')


                            ld50 = None

                            if category.acute:
                                python_hazard_class = category.hazard_class.python_hazard_class
                                if python_hazard_class.ld50_field in hazard_dict:
                                    ld50 = hazard_dict[python_hazard_class.ld50_field]

                            fdi_ici = FDIIngredientCategoryInfo(
                                ingredient = self,
                                category = category,
                                ld50 = ld50
                            )

                            fdi_ici.save()
                            self.hazards_approved = True
                            self.save()

            elif GHSIngredient.objects.filter(cas=self.cas).exists():
                #get corresponding ghs ingredient from cas number and copy the hazards
                ghs_ingredient = GHSIngredient.objects.get(cas=self.cas)

                for ghs_ici in ghs_ingredient.ingredientcategoryinfo_set.all():
                    #create a FDI ingredient category info object for each ghs ingredient category info object
                    fdi_ici = FDIIngredientCategoryInfo(
                                                        ingredient = self,
                                                        category = ghs_ici.category,
                                                        ld50 = ghs_ici.ld50
                              )
                    fdi_ici.save()
                    self.hazards_approved = True
                    self.save()

    def add_hazards_by_hcode(self, hcode_list):
        for hcode in hcode_list:
            for hazard, category_dict in HazardClassDict.items():
                for category, hci in category_dict.items():
                    if hcode not in ['H303','H313','H316','H320','H333'] and hcode == hci.hcode:
                        print("Processing hcode: %s" % hcode)
                        #if the raw material aleady has a certain hazard, we will overwrite it.

                        if hci.subcategories != (''):
                            category += hci.subcategories[-1] #adds the lowest level subcategory if there is one

                        hazard_category = HazardCategory.objects.get(hazard_class__python_class_name=hazard,category=category)
                        hazard_class = hazard_category.hazard_class

                        if self.hazard_set.filter(hazard_class=hazard_class).exists():
                            old_category = self.hazard_set.get(hazard_class=hazard_class)
                            print("Removing category: %s" % old_category)
                            old_fdi_ici = self.fdiingredientcategoryinfo_set.filter(category=old_category)
                            old_fdi_ici.delete()

                        print(hazard_category)

                        #have to create an FDIIngredientCategoryInfo object - if it needs an ld50, use the threshold
                        fdi_ici = FDIIngredientCategoryInfo(
                            ingredient = self,
                            category = hazard_category,
                            ld50 = int(hci.category_test.threshold) if 'AcuteToxicity' in hazard else None,
                        )
                        fdi_ici.save()

                        print("Added new category: %s" % hazard_category)

        self.hazards_approved = True
        self.save()

    @property
    def merged_hcode_info(self):
        if not hasattr(self, '_hcode_info'):
            self._hcode_info = collections.defaultdict(set)
            for hc in self.hazard_set.all():
                if hc.hcode != None:
                    try: #some hcodes have no hazards - we don't want to create a label object for these (and we can't because there is not enough info)
                        hcode_info = hc.get_hcode_info()
                        for k,v in hcode_info.items():
                            if k == 'p_codes':
                                self._hcode_info[k] = self._hcode_info[k].union(v)
                            else:
                                self._hcode_info[k].add(v)
                    except:
                        print("Skipping hcode %s: not hazardous" % hc.hcode)

        return self._hcode_info

    def create_rm_label_objects(self):
        #we need hazard statements and precautionary statements to be objects so they can be directly used in labelview
        #might want to reimplement the whole thing because a lot of the code assumes that they are only hardcoded in one location
        hcode_info = self.merged_hcode_info

        RMPrecautionaryStatement.objects.filter(ingredient=self).delete()
        RMHazardStatement.objects.filter(ingredient=self).delete()
        RMPictogram.objects.filter(ingredient=self).delete()
        RMSignalWord.objects.filter(ingredient=self).delete()

        if hcode_info['statement']:
            for statement in hcode_info['statement']:
                hazard_statement = RMHazardStatement(ingredient = self,
                                                   statement = statement)
                hazard_statement.save()
        else:
            hazard_statement = RMHazardStatement(ingredient = self,
                                               statement = 'This product has no hazard statements.')
            hazard_statement.save()

        if hcode_info['p_codes']:
            for pcode in hcode_info['p_codes']:
                precautionary_statement = RMPrecautionaryStatement(ingredient = self,
                                                                 statement = pcode_dict[pcode])
                precautionary_statement.save()
        else:
            precautionary_statement = RMPrecautionaryStatement(ingredient=self,
                                                             statement = 'This product has no precautionary statements')
            precautionary_statement.save()

        for pictogram_code in hcode_info['pictogram_code']:
            ghs_pictogram = RMPictogram(ingredient = self,
                                         pictogram_code = pictogram_code,
                                         pictogram_location = '%s.png' % pictogram_code)
            ghs_pictogram.save()

        if hcode_info['signal_word']:
            for signal in hcode_info['signal_word']:
                ghs_signal_word = RMSignalWord(ingredient = self,
                                                signal_word = signal)
                ghs_signal_word.save()
        else:
            ghs_signal_word = RMSignalWord(ingredient=self,
                                            signal_word = 'Not Hazardous')
            ghs_signal_word.save()

    def recalculate_inventory(self):
        #Use inventorylog objects to recalculate the inventory of this ingredient
        total = 0
        for iil in IngredientInventoryLog.objects.filter(ingredient=self):
            total += iil.delta

        self.inventory = total
        self.save()

    def get_field_status(self, field_name):
        #Determine whether a field has been verified by looking for the corresponding Document/DocumentVerification objects

        #1. Create a data structure linking field names to doctypes
        #2. Use the field name to obtain the corresponding doctype
        #3. Filter DocumentVerification objects to see if there is currently an unexpired, verified Document

        if field_name in rm_field_to_doctype_dict:
            corresponding_doctype = rm_field_to_doctype_dict[field_name]
            return self.get_document_status(corresponding_doctype)

        else:
            return 'N/A' #field has no corresponding doctype


    def get_document_status(self, doctype):

        # if self.supplier != None:
        #     docs_ordered_by_expiration = Documents.objects.filter(
        #         rawmaterial__supplier__suppliercode=self.supplier.suppliercode, doctype=doctype, rawmaterial=self).order_by(
        #         '-expiration')
        # else:
        docs_ordered_by_expiration = Documents.objects.filter(doctype=doctype, rawmaterial=self).order_by('-expiration')
        if docs_ordered_by_expiration.exists():
            latest_doc = docs_ordered_by_expiration[0]

            if latest_doc.days_until_expiration <= 0:
                return 'Expired'  # expired
            else:
                if latest_doc.verified:
                    return 'Verified'  # verified
                else:
                    if latest_doc.dv_count == 0:
                        return 'Unverified'  # unverified
                    elif latest_doc.dv_count == 1:
                        return 'Single Verification'
                    else:
                        return 'Verification Mismatch'

        else:
            return 'No Documents'  # no documents


    def get_allergens(self):
        from access.scratch import parse_single_rm_allergen
        parse_single_rm_allergen(self)

        return self.allergen


    def get_latest_document(self, doctype):
        docs_ordered_by_expiration = Documents.objects.filter(doctype=doctype, rawmaterial=self).order_by('-expiration')
        if docs_ordered_by_expiration.exists():
            return docs_ordered_by_expiration[0]
        else:
            return False


class FDIIngredientCategoryInfo(models.Model):
    #this contains information specific to an ingredient+category pair (ld50)
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    category = models.ForeignKey(HazardCategory,on_delete=models.CASCADE)
    ld50 = models.DecimalField(decimal_places = 3, max_digits = 10, null=True, blank=True)


class FormulaLineItem(models.Model):
    """
    This model pretty much represents a consolidated leaf weight of a flavor.
    Each instance of this model will contain a cas number and a weight.
    A list of a FormulaLineItem objects will be passed into the main function of this app.
    """

    def __str__(self):
        return "%s-%s" % (self.ingredient, self.weight)

    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    weight = models.DecimalField(decimal_places=3, max_digits=7)

class FormulaInfo(models.Model):
    solvent = models.CharField(
        max_length=50,
        blank=True)

    rawmaterialcost = models.DecimalField(
        decimal_places=3,
        max_digits=7,
        blank=True,
        null=True)

    sulfites = models.BooleanField(default=False)
    sulfites_ppm = models.DecimalField(decimal_places=1,max_digits=6,blank=True,null=True)
    sulfites_usage_threshold = models.DecimalField(decimal_places=3,max_digits=5,blank=True,null=True)

    #These allergens must specifcy the type/species - text fields instead of boolean
    fish = models.CharField("Fish", blank=True, null=True, max_length=100)
    treenuts = models.CharField("Treenuts", blank=True, null=True, max_length=100)
    crustacean = models.CharField("Crustacean", blank=True, null=True, max_length=100)

    eggs = models.BooleanField(default=False)
    milk = models.BooleanField(default=False)
    peanuts = models.BooleanField(default=False)
    soybeans = models.BooleanField(default=False)
    wheat = models.BooleanField(default=False)
    sunflower = models.BooleanField(blank=True, default=False)
    sesame = models.BooleanField(blank=True, default=False)
    mollusks = models.BooleanField(blank=True, default=False)
    mustard = models.BooleanField(blank=True, default=False)
    celery = models.BooleanField(blank=True, default=False)
    lupines = models.BooleanField(blank=True, default=False)
    yellow_5 = models.BooleanField(blank=True, default=False)

    barley_gluten = models.BooleanField("Barley Gluten", blank=True, default=False)

    indivisible = models.BooleanField(blank=True, default=False)

    diacetyl = models.BooleanField("No Diacetyl", default=True)
    no_pg = models.BooleanField("No PG",
        blank=True,
        default=False)

    flashpoint = models.PositiveIntegerField("Flash Point", default=0)
    spg = models.DecimalField(decimal_places=3,max_digits=4,default=0)
    stability = models.CharField(max_length=25, blank=True, default="")
    allergen = models.CharField("Allergens", max_length=100, blank=True, default="")
    yield_field = models.PositiveIntegerField("Percent Yield", default=100) # Field renamed because it was a Python reserved word.lc

    reactionextraction = models.BooleanField("Reaction/Extraction",default=False)
    prop_65 = models.CharField("Prop 65", max_length=50,blank=True, default="") # Field renamed to remove spaces.lc
    # gmo = models.CharField("GMO", max_length=50, choices=YES_NO_CHOICES, blank=True, default="")
    # '''gmo_percentage = models.DecimalField("GMO %",
    #     max_digits=7,
    #     decimal_places=4,
    #     blank=True,
    #     null=True)'''
    prop65 = models.BooleanField(default=False)

    #new fields 11/17
    ovo_vegan = models.BooleanField(blank=True, default=False)
    vegan = models.BooleanField(blank=True, default=False)

    #end new fields


    #TO BE DELETED - keeping until we categorize products
    organic = models.BooleanField(default=False)
    wonf = models.BooleanField("Natural WONF", default=False,blank=True)
    natural_type = models.BooleanField("Natural Type", blank=True, default=False)

    liquid = models.BooleanField(default=False,blank=True)
    dry = models.BooleanField(default=False,blank=True)
    spraydried = models.BooleanField("Spray Dried",
        blank=True,
        default=False)
    flavorcoat = models.BooleanField("Flavorcoat®",blank=True,default=False)

    concentrate = models.BooleanField(default=False,blank=True)
    oilsoluble = models.BooleanField("Oil soluble",default=False,blank=True)
    # solubility = models.CharField(max_length=25,blank=True, default="")
    #END TO BE DELETED

    class Meta:
        abstract = True


@reversion.register
class Flavor(FormulaInfo):

    id = models.PositiveIntegerField(
            primary_key=True,
            default=get_next_flavorid)
    number = models.PositiveIntegerField(
            unique=True)

    # fk to ingredient, one to many
    ingredients = models.ManyToManyField(
            Ingredient,
            through='Formula')

    renumber_of = models.ForeignKey('self', related_name='renumbers', null=True,on_delete=models.CASCADE)

    hazard_set = models.ManyToManyField(HazardCategory, through='FlavorCategoryInfo')

    name = models.CharField(
            max_length=80,)
    prefix = models.CharField(
            max_length=2,)
    code = models.CharField(
            max_length=3,
            blank=True)
    natart = models.CharField(
            max_length=50,
            blank=True,
            choices=NATART_CHOICES)
    label_type = models.CharField(
            max_length=50,
            blank=True,
            db_column="type")

    #NEW FIELDS
    phase = models.CharField(
            max_length=100,
            blank=True,
            default='Undetermined',
            choices=PHASE_CHOICES)

    product_category = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            choices=PRODUCT_CATEGORY_CHOICES)

    wonf_type = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            choices=WONF_TYPE_CHOICES)

    country_of_origin = models.CharField(max_length=200,blank=True,null=True)

    organic_compliant = models.NullBooleanField()
    # oil_soluble = models.NullBooleanField()

    # organic_compliant = models.CharField(
    #         max_length=100,
    #         blank=True,
    #         null=True,
    #         choices=ORGANIC_COMPLIANT_CHOICES)
    #
    organic_compliant_required = models.BooleanField("Organic Compliant Required",blank=True,default=False)
    organic_certified_required = models.BooleanField("Organic Certified Required",blank=True,default=False)
    organic_certification_number = models.CharField(max_length=100,blank=True,null=True)

    solubility = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            choices=SOLUBILITY_CHOICES)

    #END NEW FIELDS

    #SPEC SHEET FIELDS
    # water_activity = models.CharField(max_length=100, blank=True, null=True)
    # bostwick_consistometer = models.CharField(max_length=100, blank=True, null=True)
    # brix = models.CharField(max_length=100, blank=True, null=True)
    #
    # sieve = models.CharField(max_length=100, blank=True, null=True)
    # moisture = models.CharField(max_length=100, blank=True, null=True)
    # description = models.CharField(max_length=300, blank=True, null=True)

    unitprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            blank=True,
            null=True)
    productmemo = models.TextField(
            blank=True)
    mixing_instructions = models.TextField(blank=True)
    color = models.CharField(max_length=200,blank=True)
    organoleptics = models.CharField(max_length=50,blank=True)
    pricing_memo = models.TextField(blank=True)

    entered = models.DateTimeField(auto_now_add=True)
    supportive_potential = models.BooleanField(blank=True, default=False)
    risk_assessment_group = models.PositiveSmallIntegerField(default=7,choices=RISK_ASSESSMENT_CHOICES)
    risk_assessment_memo = models.TextField(blank=True)

    discontinued = models.BooleanField(
            blank=True,
            default=False)
    approved = models.BooleanField(
            blank=True,
            default=False)

    sold = models.BooleanField(
            blank=True,
            default=False)

    lastprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            blank=True,
            null=True)
    experimental = models.CharField(
            max_length=50,
            blank=True)
    lastspdate = models.DateTimeField(
            blank=True,
            default=datetime.now)

    valid = models.BooleanField(
            default=False)
    #flavornumber = models.PositiveIntegerField(db_column='FlavorNumber')
    #productid = models.PositiveIntegerField(db_column='ProductID', blank=True, default=0)
    #flavor = models.OneToOneField('Flavor', null=True)

    kosher = models.CharField("Kosher", max_length=20,default="Not Assigned", choices=KOSHER_CHOICES)
    kosher_id = models.CharField("Kosher ID", max_length=20, default="", blank=True)

    halal = models.CharField("Halal", max_length=20,default="Not Assigned", choices=HALAL_CHOICES)
    halal_id = models.CharField("Kosher ID", max_length=20, default="", blank=True)

    nutri_on_file = models.BooleanField("Nutri On File", default=False) # Field renamed to remove spaces.lc
    flammability = models.CharField(max_length=40, blank=True, default="")
    vaporpressure = models.DecimalField(decimal_places=2,
                                        max_digits=4,
                                        default=0)
    pinnumber = models.PositiveIntegerField(blank=True, null=True)

    label_check = models.BooleanField("Ken Label Check", default=False)

    ccp1 = models.BooleanField("CCP#1 Sieve",default=True)
    ccp2 = models.BooleanField("CCP#2 Allergen Cleaning",default=False)
    ccp3 = models.BooleanField("CCP#3 COA Verification",default=False)
    ccp4 = models.BooleanField("CCP#4 Label Application",default=False)
    ccp5 = models.BooleanField("CP#5 GMO Non-detect",default=False)
    ccp6 = models.BooleanField("CCP#6 Thermal Kill Step",default=False)
    haccp = models.PositiveSmallIntegerField("HACCP", blank=True, null=True)
    batfno = models.CharField("TTB No.", max_length=50,blank=True, default="")
    microtest = models.CharField("Micro Test", max_length=4,default="", blank=True)



    quantityperunit = models.PositiveIntegerField(
            blank=True,
            null=True)
    supplierid = models.PositiveIntegerField(
            blank=True,
            null=True)
    unitsinstock = models.PositiveIntegerField(
            blank=True,
            null=True)
    unitsonorder = models.PositiveIntegerField(
            blank=True,
            null=True)
    reorderlevel = models.PositiveIntegerField(
            blank=True,
            null=True)
    categoryid = models.PositiveIntegerField(
            blank=True,
            null=True)

    keywords = models.TextField(blank=True)
    #flavor
    location_code_n = fields.GenericRelation('LocationCode')
    location_code_old = models.CharField(blank=True, default="",max_length=20)

    keep_refrigerated = models.BooleanField("Keep Refrigerated",default=False)

    def save(self, *args, **kwargs):
        try:
            self.prefix = self.prefix.upper()
        except:
            pass

        super(Flavor, self).save(*args, **kwargs)


        # if not self.flavorspecification_set.filter(name='Specific Gravity').exists():
        #     flavorspec = FlavorSpecification(
        #                                      flavor = self,
        #                                      name = 'Specific Gravity',
        #                                      specification = 'SPG Spec',
        #                                      )
        #     flavorspec.save()
        #
        # if self.flashpoint != 0: #no flashpoint or powder
        #     if not self.flavorspecification_set.filter(name='Flash Point').exists():
        #         flavorspec = FlavorSpecification(
        #                                          flavor = self,
        #                                          name = 'Flash Point',
        #                                          specification = 'Flashpoint Spec',
        #                                          )
        #         flavorspec.save()


    def gazintas(self,):
        for ft in FormulaTree.objects.filter(root_flavor=self)[1:]:
            if ft.node_flavor is not None:
                yield ft.node_flavor

    class Meta:
        db_table = 'access_integratedproduct'
        ordering = ['-valid','number']
        default_permissions = ('add', 'change', 'delete')
        # permissions = (
        #         ('view_flavor',"Can view flavors"),
        # )
    import_order = 0

    @property
    def ingredient_statement(self):
        if IngredientStatement.objects.filter(flavor=self).exists():
            return IngredientStatement.objects.get(flavor=self).ingredient_statement


    @property
    def microsensitive(self):

        #if the product is a powder/flavorcoat, if any ingredient is microsensitive, the product will be considered microsensitive
        if self.phase == "Powder" or self.phase == "Flavorcoat":
            for lw in LeafWeight.objects.filter(root_flavor=self):
                if lw.ingredient.microsensitive == "True":
                    return True
            return False

        else:
            leaf_weights = LeafWeight.objects.filter(root_flavor=self)

            try:
                water = leaf_weights.get(ingredient__id=100).amount
            except:
                water = 0

            #if the product has water < 4%, it is not microsensitive
            if water < Decimal(40):
                return False

            else:

                #get weights of each relevant ingredient, set to 0 if they don't exist
                #could make a function to optimize this
                try:
                    pg = leaf_weights.get(ingredient__id=703).weight
                except:
                    pg = 0
                try:
                    triacetin = leaf_weights.get(ingredient__id=829).weight
                except:
                    triacetin = 0
                try:
                    benzyl_alcohol = leaf_weights.get(ingredient__id=86).weight
                except:
                    benzyl_alcohol = 0
                try:
                    ethyl_alcohol = leaf_weights.get(ingredient__id=321).weight
                except:
                    ethyl_alcohol = 0

                # if theres a total of more than 12.5% of pg, triacetin and benzyl alcohol, not microsensitive
                if pg + triacetin + benzyl_alcohol >= Decimal(125):
                    return False

                # if ethyl alcohol is more than 75%, not microsensitive
                if ethyl_alcohol >= Decimal(750):
                    return False

                # if benzyl alcohol is more than 20%, not microsensitive
                if benzyl_alcohol >= Decimal(200):
                    return False

            return True

    @property
    def location_code(self):
        try:
            return self.location_code_n.all().reverse()[0]
        except:
            return None

    @property
    def url(self):
        return "/access/%s/" % self.number

    @property
    def reconciled(self):
        if ReconciledFlavor.objects.filter(flavor=self,reconciled='True').exists():
            return True
        else:
            return False

    @property
    def status(self):

        dci = self.discontinued_ingredients

        message = []

        if len(dci) != 0:
            message.append("Contains the following discontinued ingredients: %s" % ", ".join(dci))

#         if not self.reconciled:
#             message.append("Does not have a proper reconciled specification sheet.")

        if len(message) != 0:
            return "\n\n".join(message)
        else:
            return ""

    @property
    def reconciled(self):
        if ReconciledFlavor.objects.filter(flavor=self,reconciled='True').exists():
            return True
        else:
            return False

    @property
    def discontinued_ingredients(self):
        dci = []
        for lw in self.leaf_weights.all():
            if lw.ingredient.discontinued == True:
                dci.append(lw.ingredient.__str__())
        return dci

    def quick_validate(self, descend=True):
        sum = 0
        for fr in self.formula_set.all():
            sum+= fr.amount
        if sum != 1000:
            return "%s-%s formula does not add up to 1000 parts." % (self.prefix, self.number)

        if descend == False:
            return True
        else:
            for fr in FormulaTree.objects.filter(root_flavor=self)[1:]:
                g = fr.node_ingredient.gazinta()
                if g is not None:
                    qv = g.quick_validate(descend=False)
                    if qv != True:
                        return "%s-%s formula does not add up to 1000 parts." % (g.prefix, g.number)
            return True




    @property
    def table_name(self):
        return " ".join((self.name, self.label_type))

    @property
    def natart_name_with_type(self):
        return "%s %s %s" % (self.natart, self.name, self.label_type)

    def get_admin_url(self):
        return "/admin/access/flavor/%s" % self.id

    def get_absolute_url(self):
        return "/access/%s/" % self.number

    def get_specs_url(self):
        return "/access/%s/spec_list" % self.number

    def get_reconcile_specs_url(self):
        return "/access/%s/reconcile_specs" % self.number

    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(Flavor, number=softkey).get_absolute_url()
        except:
            return None

    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            return Flavor.objects.get(number=softkey)
        except:
            return None


    def get_fdnum(self):
        return "%s-%s" % (self.prefix, self.number)

    def __str__(self):
        return "%s-%s %s %s %s" % (self.prefix,
                                   self.number,
                                   self.natart,
                                   self.name,
                                   self.label_type)

    @property
    def long_name(self):
        return "%s %s-%s %s %s" % (self.natart, self.prefix, self.number, self.name, self.label_type)

    @staticmethod
    def get_next_tempex_number():
        current_tempex_numbers = set(Flavor.objects.filter(number__gte=50000).filter(number__lt=60000).order_by('-number').values_list('number',flat=True))
        valid_tempex_numbers = set(range(50000,60000))
        available_tempex_numbers = valid_tempex_numbers - current_tempex_numbers
        next_tempex_number = sorted(list(available_tempex_numbers))[-1]
        return next_tempex_number

    @staticmethod
    def get_next_solution_number():
        #Solutions will be in the 6000-6999 range
        current_solution_numbers = set(Flavor.objects.filter(number__gte=6000,number__lt=7000).order_by('-number').values_list('number',flat=True))
        valid_solution_numbers = set(range(6000,7000))
        available_solution_numbers = valid_solution_numbers - current_solution_numbers
        next_solution_number = sorted(list(available_solution_numbers))[0]
        return next_solution_number

    @staticmethod
    def process_special_kwargs(resultant_objects, form_data):
        if 'exclude_any_ingredients' in form_data and form_data['exclude_any_ingredients'] != '':
            exclude_any_ingredients = form_data['exclude_any_ingredients'].replace(' ','').split(',')
            resultant_objects = Flavor.flavors_excluding_ingredients(resultant_objects, exclude_any_ingredients)
        if 'include_any_ingredients' in form_data and form_data['include_any_ingredients'] != '':
            include_any_ingredients = form_data['include_any_ingredients'].replace(' ','').split(',')
            resultant_objects = Flavor.flavors_including_any_ingredients(resultant_objects, include_any_ingredients)
        if 'include_all_ingredients' in form_data and form_data['include_all_ingredients'] != '':
            include_all_ingredients = form_data['include_all_ingredients'].replace(' ','').split(',')
            resultant_objects = Flavor.flavors_including_all_ingredients(resultant_objects, include_all_ingredients)
        if 'flash_point' in form_data and form_data['flash_point'] != '':
            flash_point = form_data['flash_point']
            resultant_objects = resultant_objects.filter(flashpoint__gte=flash_point)
        return resultant_objects

    @staticmethod
    def flavors_excluding_ingredients(flavor_queryset, exclude_ingredients):
        """Modifies flavor_queryset to exclude flavors that contain any
        ingredients with IDs listed in exclude_ingredients.
        """
        exclude_these = LeafWeight.objects.filter(
                ingredient__id__in=exclude_ingredients).values_list(
                'root_flavor',flat=True).order_by().distinct()
        return flavor_queryset.exclude(pk__in=exclude_these)

    @staticmethod
    def flavors_including_any_ingredients(flavor_queryset, include_any_ingredients):
        include_these = LeafWeight.objects.filter(
                ingredient__id__in=include_any_ingredients).values_list(
                'root_flavor',flat=True).order_by().distinct()
        return flavor_queryset.filter(pk__in=include_these)

    @staticmethod
    def flavors_including_all_ingredients(flavor_queryset, include_all_ingredients):
        for ingredient_id in include_all_ingredients:
            include_these = LeafWeight.objects.filter(
                    ingredient__id=ingredient_id).values_list(
                    'root_flavor',flat=True).order_by().distinct()
            flavor_queryset = flavor_queryset.filter(pk__in=include_these)
        return flavor_queryset

    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):

            if key == 'natart':
                keyword = 'natart__in'
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'kosher':
                keyword = 'kosher__in'
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'applications':
                keyword = 'applications__application_type__id__in'
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
                #keyword =
            # TODO fix retains__ntoes
            elif key == 'other':
                for my_arg in qdict.getlist(key):
                    #if my_arg == 'retains__notes':
                    #    string_kwargs['retains__notes'] = ''
                    if my_arg == 'no_pg':
                        string_kwargs['no_pg__in'] = [True]
                    elif my_arg == 'supportive_potential':
                        string_kwargs['supportive_potential__in'] = [True]
            elif key == "risk_assessment_group":
                keyword = "risk_assessment_group__in"
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key in ["exclude_any_ingredients", "include_any_ingredients", "include_all_ingredients", "flash_point"]:
                continue
            else:
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(bool(my_arg))
                string_kwargs[keyword] = arg_list
        return string_kwargs


    def get_related_links(self):
        """This is going to be replaced by get_product_tabs and might
        be able to be removed. Leaving it in for now, just in case.
        """
        related_links = [
                       ('#flat_review_table','Formula'),
                       ('/access/ajax_dispatch/?tn=consolidated&pk=%s' % self.pk,'Consolidated'),
                       ('/access/ajax_dispatch/?tn=consolidated_indivisible&pk=%s' % self.pk, 'Consolidated-Indivisible'),
                       ('/access/ajax_dispatch/?tn=explosion&pk=%s' % self.pk,'Explosion'),
                       ('/access/ajax_dispatch/?tn=legacy_explosion&pk=%s' % self.pk,'Legacy Explosion'),
                       ('/access/ajax_dispatch/?tn=revision_history&pk=%s' % self.pk, 'Revision History'),
                       ('/access/ajax_dispatch/?tn=spec_sheet&pk=%s' % self.pk, 'Spec Sheet'),
                       ('/access/ajax_dispatch/?tn=customer_info&pk=%s' % self.pk, 'Customer Info'),
                       ('/access/ajax_dispatch/?tn=similar_flavors&pk=%s' % self.pk, 'Similar Flavors'),
                       ('/access/ajax_dispatch/?tn=documentation&pk=%s' % self.pk, 'Documentation'),
                       ]
        if self.lot_set.count()>0:
            related_links.append(('/access/ajax_dispatch/?tn=production_lots&pk=%s' % self.pk, 'Production Lots'))
            related_links.append(('/access/ajax_dispatch/?tn=retains&pk=%s' % self.pk, 'Retains'))

        try:
            self.experimentallog
            related_links.append(('/access/ajax_dispatch/?tn=experimental_log&pk=%s' % self.pk,'Experimental'))
        except:
            pass
        try:
            rmr = self.raw_material_record
            if rmr:
                related_links.append(('/access/ajax_dispatch/?tn=raw_material_pin&pk=%s' % self.pk,'Raw Material PIN'))
                if Formula.objects.filter(ingredient=rmr).count() > 0:
                    related_links.append(('/access/ajax_dispatch/?tn=gzl_ajax&pk=%s' % self.pk, 'GZL'))
        except:
            pass

        return related_links

    def get_product_tabs(self):
        product_tabs = [
                       ('#flat_review_table','Formula'),
                       ('/access/ajax_dispatch/?tn=consolidated&pk=%s' % self.pk,'Consolidated'),
                       ('/access/ajax_dispatch/?tn=consolidated_indivisible&pk=%s' % self.pk, 'Consolidated-Indivisible'),
                       ('/access/ajax_dispatch/?tn=explosion&pk=%s' % self.pk,'Explosion'),
                       ('/access/ajax_dispatch/?tn=legacy_explosion&pk=%s' % self.pk,'Legacy Explosion'),
                       ('/access/ajax_dispatch/?tn=revision_history&pk=%s' % self.pk, 'Revision History'),
                       # ('/access/ajax_dispatch/?tn=spec_sheet&pk=%s' % self.pk, 'Spec Sheet'),
                       # ('/access/ajax_dispatch/?tn=customer_info&pk=%s' % self.pk, 'Customer Info'),
                       ('/access/ajax_dispatch/?tn=similar_flavors&pk=%s' % self.pk, 'Similar Flavors'),
                       ('/access/ajax_dispatch/?tn=documentation&pk=%s' % self.pk, 'Documentation'),
                       ]
        if self.lot_set.count()>0:
            product_tabs.append(('/access/ajax_dispatch/?tn=production_lots&pk=%s' % self.pk, 'Production Lots'))
            product_tabs.append(('/access/ajax_dispatch/?tn=retains&pk=%s' % self.pk, 'Retains'))

        try:
            self.experimentallog
            product_tabs.append(('/access/ajax_dispatch/?tn=experimental_log&pk=%s' % self.pk,'Experimental'))
        except:
            pass
        try:
            rmr = self.raw_material_record
            if rmr:
                product_tabs.append(('/access/ajax_dispatch/?tn=raw_material_pin&pk=%s' % self.pk,'Raw Material PIN'))
                if Formula.objects.filter(ingredient=rmr).count() > 0:
                    product_tabs.append(('/access/ajax_dispatch/?tn=gzl_ajax&pk=%s' % self.pk, 'GZL'))
        except:
            pass

        return product_tabs


    @property
    def linked_memo(self):
        tokens = re.split('(\d{3,})', self.productmemo)

        for i in range(len(tokens)):
            try:
                Flavor.objects.get(number=tokens[i])
                tokens[i] = '<a href="/access/%s/">%s</a>' % (tokens[i], tokens[i])
            except:
                pass
        return ''.join(tokens)

    @property
    def naive_linked_memo(self):
        return re.sub('(\d{3,})', r'<a href="/access/\1/">\1</a>', self.productmemo)

    @property
    def allergen_list(self):
        return_list = []
        for aller in Ingredient.boolean_allergens:
            if getattr(self,aller):
                return_list.append(aller)
        for aller in Ingredient.text_allergens:
            if getattr(self, aller):
                return_list.append('%s (%s)' % (aller, getattr(self, aller)))

        return return_list

    @property
    def renumber_list(self):
        return Renumber.objects.filter(a=self).values_list('b',flat=True)


    @property
    def renumber_number_list(self):
        # r = Renumber.objects.filter(a=self).values_list('b__number',flat=True)
        r = Renumber.objects.filter(a=self)
        r_list = ""
        for i in r:
            if not i.customer == None:
                    r_list += '<a href="/access/%s" target="_blank">%s</a> ' % (i.b.number, i.customer.companyname)
            else:
                r_list += '<a href="/access/%s" target="_blank">%s</a> ' % (i.b.number, i.b.number)

        return r_list

    @property
    def loaded_renumber_list(self):
        id_list = [self.id,]
        id_list.extend(self.renumber_list)
        return id_list

    def lot_superset(self):
        from newqc.models import Lot
        return Lot.objects.filter(flavor__in=self.loaded_renumber_list)

    def retain_superset(self):
        from newqc.models import Retain
        return Retain.objects.filter(lot__flavor__in=self.loaded_renumber_list)

    def sorted_retain_superset(self):
        from newqc.models import Retain
        return Retain.objects.filter(lot__flavor__in=self.loaded_renumber_list)

    def combed_sorted_retain_superset(self):
        retains = self.sorted_retain_superset()
        csl = [retains[0],] # combed sorted list
        for x in range(1,len(retains)):
            if retains[x].similar_to(retains[x-1]):
                pass
            else:
                csl.append(retains[x])

        return csl

    @staticmethod
    def anonymize():
        for f in Flavor.objects.all():
            lorem_one = q.get()
            lorem_two = q.get()
            lorem_three = q.get()
            lorem_four = q.get()
            print(f)
            f.name = "%s %s" % (lorem_one, lorem_two)
            f.label_type = "Flavor"
            f.productmemo = "%s %s %s %s" % (lorem_one, lorem_two, lorem_three, lorem_four)
            f.prefix = "FL"
            f.save()

            q.put(lorem_one)
            q.put(lorem_two)
            q.put(lorem_three)
            q.put(lorem_four)

            print(f)

    @property
    def get_max_depth(self):
        max_depth = 0
        for ftnode in FormulaTree.objects.filter(root_flavor=self):
            if ftnode.depth > max_depth:
                max_depth = ftnode.depth

        return max_depth

    def get_max_depth_gazinta(self):

        max_depth = self.get_max_depth
        for ftnode in FormulaTree.objects.filter(root_flavor=self):
            if ftnode.depth == max_depth:
                #max_depth_ingredients.append(ftnode.node_ingredient)
                max_depth_gazinta_node = FormulaTree.objects.get(root_flavor=self, row_id=ftnode.parent_id).node_flavor
                break

        return max_depth_gazinta

    @property
    def leaf_weight_count(self):
        return self.leaf_nodes.count()

    @property
    def consolidated_leaf_weight_count(self):
        return len(self.consolidated_leafs)

    @property
    def gazinta_count(self):  #DOES NOT INCLUDE ROOT FLAVOR
        count = 0

#         for ft in FormulaTree.objects.filter(root_flavor = self)[1:]
#             if ft.node_ingredient.is_gazinta:
#                 count = count+1

        #OR
        for ft in FormulaTree.objects.filter(root_flavor=self)[1:]:
            if ft.node_flavor is not None:
                count = count+1

        #OR

        #total nodes - leaf nodes = gazinta nodes
        #count = FormulaTree.objects.filter(root_flavor=self).count() - fl.leaf_nodes.count() - 1 #minus the root flavor

        return count #this count DOES NOT include the root flavor as a gazinta

    @property
    def leaf_nodes(self):
        return FormulaTree.objects.filter(root_flavor=self).filter(rgt=F('lft') + 1)

    @property
    def indivisible_leaf_nodes(self):
        right_number_check = 0
        for ft in FormulaTree.objects.filter(root_flavor=self)[1:]:
            if ft.lft < right_number_check:
                continue
            else:
                if ft.indivisible_leaf:
                    yield ft
                    right_number_check = ft.rgt


    @property
    def consolidated_leafs(self):
        leaf_ingredients = self.leaf_nodes
        cons_leafs = {}
        for leaf in leaf_ingredients:
            cons_leafs[leaf.node_ingredient] = cons_leafs.get(leaf.node_ingredient, 0) + leaf.weight

        return cons_leafs

    @property
    def consolidated_indivisible_leafs(self):
        indivisible_leafs = self.indivisible_leaf_nodes
        cons_leafs = {}
        for leaf in indivisible_leafs:
            cons_leafs[leaf.node_ingredient] = cons_leafs.get(leaf.node_ingredient, 0) + leaf.weight

        return cons_leafs

    @property
    def leaf_cost(self):
        scl = LeafWeight.objects.filter(root_flavor=self).select_related()
        total_cost = Decimal('0')
        for leaf in scl:
            total_cost += leaf.ingredient.unitprice * leaf.weight
        total_cost = total_cost/Decimal('1000')
        y = self.yield_field
        try:
            return total_cost / (y/one_hundred)
        except:
            return total_cost

    @property
    def sorted_consolidated_leafs(self):
        cons_leafs = sorted(iter(self.consolidated_leafs.items()), key=itemgetter(1), reverse=True)
        cons_formulae = []
        for ingredient, amount in cons_leafs:
            cons_formulae.append(Formula(ingredient=ingredient,amount=amount))
        return cons_formulae

    @property
    def sorted_consolidated_indivisible_leafs(self):
        cil=sorted(iter(self.consolidated_indivisible_leafs.items()), key=itemgetter(1), reverse=True)
        cons_indivisible_formulae = []
        for ingredient, amount in cil:
            cons_indivisible_formulae.append(Formula(ingredient=ingredient, amount=amount))
        return cons_indivisible_formulae


    @property
    def lastspdate_short(self):
        return self.lastspdate.date()

    @property
    def yield_adjusted_rmc(self):
        y = self.yield_field

        if y != zero:
            return self.rawmaterialcost / (y / one_hundred)
        else:
            return self.rawmaterialcost

    def resembles(self, flavor):

        if self.name != flavor.name:
            return "name"
        if self.prefix != flavor.prefix:
            return "prefix"
        if self.code != flavor.code:
            return "code"
        if self.natart != flavor.natart:
            return "natart"
        if self.label_type != flavor.label_type:
            return "label_type"
        if self.productmemo != flavor.productmemo:
            return "productmemo"

        return True

    def gzl_traversal(self, weight_factor=Decimal(1), row_id=1,
                      parent_id=None, parent_flavors={},
                      formula_qs=Formula.objects.all()):
        return self.gazinta.all()[0].gzl_traversal()

    def formula_traversal(self, weight_factor=Decimal(1), row_id=1,
                         parent_id=0, parent_flavors={},
                         formula_qs=Formula.objects.all(),
                         use_cache=False):
        """Yields a tuple:
        (ingredient, weight_factor, row_id, parent_id)

        This is the primary method for traversing the weighted,
        directed graph that represents a flavor formula.
        """

        if use_cache:
            for node in FormulaTree.objects.filter(root_flavor=self):
                yield (node.formula_row, node.weight_factor, node.row_id, node.parent_id)
            return

        def inner_traversal(flavor, weight_factor, row_id,
                            parent_id, parent_flavors):
            for ingredient in formula_qs.filter(flavor=flavor):
                """If an ingredient is a gazinta, first the gazinta itself
                is yielded, then formula_traversal is called on all the sub-
                ingredients. Else, the ingredient is simply yielded,
                because it has no subs.

                Each time the function yields, the row_id increments.
                """
                explode = True
                if ingredient.ingredient.is_gazinta:
                    gaz = ingredient.gazinta()
                    if gaz.number in parent_flavors:
                        raise FormulaException("Cycle detected on %s: %s" %
                                              (gaz, parent_flavors))
                    try:
                        if gaz.yield_field != 100:
                            explode = False
                    except:
                        pass
                else:
                    explode = False
                if explode == True:
                    parent_flavors[flavor.number] = len(parent_flavors)
                    yield (ingredient, weight_factor, row_id, parent_id)
                    row_id += 1
                    new_weight_factor = weight_factor*ingredient.amount/1000
                    for sub_ingredient in inner_traversal(
                                            gaz,
                                            new_weight_factor,
                                            row_id,
                                            row_id - 1,
                                            parent_flavors.copy()):
                        yield sub_ingredient
                        row_id += 1
                else:
                    yield (ingredient, weight_factor, row_id, parent_id)
                    row_id += 1

        row_id = 1
        parent_id = 0
        parent_flavors={}

        for ingredient in inner_traversal(self, weight_factor, row_id, parent_id, parent_flavors):
            yield ingredient



    def complete_formula_traversal(self, weight_factor=Decimal(1), row_id=1,
                         parent_id=0, parent_flavors={},
                         formula_qs=Formula.objects.all(),
                         use_cache=False):
        """Yields a tuple:
        (ingredient, weight_factor, row_id, parent_id)

        This is the complete method for traversing a formula. It will account
        for percentage yield, and spray dry costs to produce the final bill
        of materials and costs.
        """
        def inner_traversal(flavor, weight_factor, row_id,
                            parent_id, parent_flavors):
            for ingredient in formula_qs.filter(flavor=flavor):
                """If an ingredient is a gazinta, first the gazinta itself
                is yielded, then formula_traversal is called on all the sub-
                ingredients. Else, the ingredient is simply yielded,
                because it has no subs.

                Each time the function yields, the row_id increments.
                """
                explode = True
                explode_weight_factor = weight_factor
                if ingredient.ingredient.is_gazinta:
                    gaz = ingredient.gazinta()
                    if gaz.number in parent_flavors:
                        raise FormulaException("Cycle detected on %s: %s" %
                                              (gaz, parent_flavors))
                    try:
                        if gaz.yield_field != 100:
                            explode_weight_factor = weight_factor / (Decimal(gaz.yield_field) / 100)
                    except:
                        pass
                else:
                    explode = False
                if explode == True:
                    parent_flavors[flavor.number] = len(parent_flavors)
                    yield (ingredient, weight_factor, row_id, parent_id)
                    row_id += 1
                    new_weight_factor = explode_weight_factor*ingredient.amount/1000
                    for sub_ingredient in inner_traversal(
                                            gaz,
                                            new_weight_factor,
                                            row_id,
                                            row_id - 1,
                                            parent_flavors.copy()):
                        yield sub_ingredient
                        row_id += 1
                else:
                    yield (ingredient, weight_factor, row_id, parent_id)
                    row_id += 1

        row_id = 1
        parent_id = 0
        parent_flavors={}
        try:
            if self.yield_field != 100:
                weight_factor = weight_factor / (Decimal(self.yield_field) / 100)
        except:
            pass
        for ingredient in inner_traversal(self, weight_factor, row_id, parent_id, parent_flavors):
            yield ingredient


    def get_unique_rm_ingredients(self):
        """Returns a dictionary that has a key for each unique RM
        ingredient in a flavor.
        """
        ing_gen = self.formula_traversal()
        unique_ingredients = {}
        for formula_row in ing_gen:
            if formula_row[0].ingredient.is_gazinta:
                pass
            else:
                ingredient_key = formula_row[0].ingredient.rawmaterialcode
                unique_ingredients[ingredient_key] = 1

        return list(unique_ingredients.keys())

    def get_gazintas(self):
        gazintas = []
        for ingredient in self.ingredients.all():
#            try
            if ingredient.is_gazinta:
                gazintas.append(ingredient.gazinta())
#            except Exception as e:
#                pass
#                self.other_exceptions[ingredient.ingredient.number] = e.args
        return gazintas

    def update_cost(self, update_time=None, verbose=False):
        formula_objects = {}
        for f in Flavor.objects.all():
            formula_objects[f] = Formula.objects.filter(flavor=f)
        print("TEST")
        if update_time == None:
            update_time = datetime.now()
        def cost_traversal(flavor):
            if flavor.lastspdate == update_time:
                return flavor.rawmaterialcost
            ingredients = formula_objects[flavor]
            cost = 0
            for ingredient in ingredients:
                if ingredient.ingredient.is_gazinta:
                    g = ingredient.gazinta()
                    y = one_hundred.__copy__()
                    y = g.yield_field

                    adjustment = y/one_hundred
                    if adjustment == zero:
                        adjustment = 1
                    cost_diff = (cost_traversal(ingredient.gazinta()) *
                             ingredient.amount /
                             1000) / adjustment
                else:
                    cost_diff = (ingredient.ingredient.unitprice *
                             ingredient.amount /
                             1000)
                if verbose:
                    print('"%s","%s","%s","%s"' % (ingredient.ingredient.id, ingredient.ingredient.product_name, ingredient.amount, cost_diff))
                cost += cost_diff
            flavor.rawmaterialcost = cost
            #flavor.lastspdate = update_time
            flavor.save()
            return cost

        y = one_hundred.__copy__()
        y = self.yield_field
        adjustment = y/one_hundred
        if adjustment == zero:
            adjustment = 1

        return cost_traversal(self)/adjustment

    def flat_update_cost(self, update_time=None):
        if update_time == None:
            update_time = datetime.now()
        ingredients = Formula.objects.filter(flavor=self)
        cost = Decimal('0')
        for ingredient in ingredients:
            if ingredient.ingredient.is_gazinta:
                cost += (ingredient.gazinta().rawmaterialcost *
                         ingredient.amount /
                         1000)
            else:
                cost += (ingredient.ingredient.unitprice *
                         ingredient.amount /
                         1000)
        self.rawmaterialcost = cost
        self.lastspdate = datetime.now()
        self.save()
        return cost

    def get_formula_weight(self):
        amount = 0
        for formula_row in self.formula_set.all():
            amount = amount + formula_row.amount
        return amount

    def weight_check(self):
        amount = self.get_formula_weight()
        if amount == Decimal(1000):
            return True
        else:
            raise FormulaWeightException(self)

    def cycle_check(self, s=AncestorSet()):
        s = AncestorSet()
        def inner_check(f, s):
            s.add(f)
            for gazinta in f.get_gazintas():
                inner_check(gazinta, AncestorSet(s))
            return True
        return inner_check(self, s)

        s.add(self)
        for gazinta in self.get_gazintas():
            gazinta.cycle_check(AncestorSet(s))
        return True

    headers = (
                    ('prefix','PF', 'width="12px"'),
                    ('number','Number', 'width="50px" class="{sorter: \'link-digit\'}"'),
                    ('natart','N/A', ''),
                    ('name','Name', ''),
                    ('label_type','Type', ''),
                    ('rawmaterialcost','RMC', 'width=86px'),
                    ('lastspdate_short','Cost Update', 'width=86px'),
                    ('solvent','Solvent', 'width=60px class="{sorter: \'text\'}"'),
                    ('valid','Valid', 'width=30px'),
                    ('approved','Approved', 'width=30px'),
                    ('sold','Sold', 'width=30px'),
                )

    @staticmethod
    def text_search(search_string):
        terms = search_string.split(' ')
        results = None

        for term in terms:
            if results == None:
                results = Flavor.objects.filter(
                    Q(name__icontains=term) |
                    #Q(productmemo__icontains=term) |
                    Q(keywords__icontains=term)
                )
            else:
                results = results & Flavor.objects.filter(
                    Q(name__icontains=term) |
                    #Q(productmemo__icontains=term) |
                    Q(keywords__icontains=term)
                )
        return results

    @staticmethod
    def fix_header(header):
        if header == 'lastspdate_short':
            return 'lastspdate'
        else:
            return header

    @property
    def raw_material_record(self):
        try:
            return self.gazinta.all()[0]
        except:
            return None

    def hazard_statements_contain(self, filter_term):
        if any(filter_term.lower() in statement.lower() for statement in self.merged_hcode_info['statement']):
            return True
        else:
            return False

    def get_hazard_amount(self):

        total = 0

        for val in list(self.get_hazards().values()):
            if val != 'No':
                total = total + 1

        return total

    def get_hazard_formula_list(self):

        from solutionfixer.models import Solution

        """
        Use the imported ghs project to calculate the hazards for a flavor.

        1. Get the consolidated leafs.
        2. Convert the list of consolidated leafs to a list of FormulaLineItem objects.
            -Does the leaf ingredient have a cas number?
            -Is that cas number in the imported hazard data?
        3. create_subhazard_dict(formula_list)
        4. accumulator = HazardAccumulator(subhazard_dict)
        5. accumulator.get_hazard_dict()
        6. Save the hazards into the flavor model. SAVE THEM IN SEPARATE FUNCTION?

        """

        formula_list = []
        no_cas_total = 0
        '''
        GHS project update -> no longer modular
        FDI Raw Materials and hazards are now linked directly

        CAS# no longer really matters - it is only used to suck in hazards from the FEMA spreadsheet
        Should I still show whether or not there is a CAS mismatch?

        Go through all cases:

        1. Has hazards - No CAS, CAS mismatch, CAS found
        2. No hazards - No CAS, CAS mismatch, CAS found

        I should add a hazards_approved field to each raw material.
        This will replace the mismatch/No CAS stuff.

        Changing the FLI model - no more mismatch.
        All we really need is FK to ingredient and weight

        '''

        '''
        Need to account for two possibilities:

        1. The ingredient does not have a cas number in our database.
            -Create a placeholder GHSIngredient with cas number '00-00-00'
                and no hazards.  This placeholder ingredient has no hazards.
            -When an ingredient does not have a cas number, create a FormulaLineItem
                with cas = '00-00-00' and record its weight.
            -For each ingredient without a cas number, add its weight to the 'no_cas_total'
                variable.
            -When the for loop is complete, create a FormulaLineItem with cas = '00-00-00'
                and weight = no_cas_total (we are consolidating all the ingredients without cas #s)


        2. The ingredient cas number is not in the imported data.
            -Do the same as above (Should I handle this case differently?)
        '''


#         if self.consolidated_leafs == {}:
#             raise NoLeafWeightError(self.number)

        lws = LeafWeight.objects.filter(root_flavor=self)
        if not lws.exists():

            if self.formula_set.exists():
                from access.scratch import recalculate_guts
                recalculate_guts(self)

            else:
                raise NoFormulaError(self.number)

#         for ingredient, weight in self.consolidated_leafs.iteritems():


        #this function consolidates leaf weights even further - it breaks down any solutions into its solute and solvent
        super_consolidated_leaf_weights = consolidate_leaf_weight_solutions(lws)

        for ingredient, weight in super_consolidated_leaf_weights:
            fli = FormulaLineItem(ingredient=ingredient,
                                  weight=weight)

            '''
            if ingredient.cas != '' and GHSIngredient.objects.filter(cas=ingredient.cas).exists():
                fli = FormulaLineItem(ingredient=ingredient,
                                      cas=ingredient.cas,
                                      weight=weight,
                                      source_name = '%s: %s' % (ingredient.id, ingredient.product_name),
                                      source_url = ingredient.get_absolute_url(),
                                      mismatch = False)

            else: #this covers both case 1 and 2; if you want to differentiate between them then you need the code below
                if ingredient.cas == '':
                    cas = 'No CAS (%s)' % unknown_count
                else:
                    cas = '%s' % ingredient.cas

                fli = FormulaLineItem(ingredient=ingredient,
                                      cas = cas,
                                      weight = weight,
                                      source_name = '%s: %s' % (ingredient.id, ingredient.product_name),
                                      source_url = ingredient.get_absolute_url(),
                                      mismatch = True)
                unknown_count += 1
            '''
            formula_list.append(fli)

        return formula_list

    def set_hazards(self):
        """
        Use the formula list generated in the function above to calculate
        the hazards for a flavor using calculate_flavor_hazards().
        """
        FlavorCategoryInfo.objects.filter(flavor=self).delete()
        formula_list = self.get_hazard_formula_list()
        hazard_dict = calculate_flavor_hazards(formula_list)
        hazard_dict = update_hazard_dict_with_flammable_hazards(hazard_dict, self.flashpoint)

        for hazard, category in hazard_dict.items():
            if category != 'No' and type(category) != Decimal:
                try:
                    category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                                .get(category=category)
                except ObjectDoesNotExist:
                    category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                                    .get(category=category + 'A')


                ld50 = None

                if category.acute:
                    python_hazard_class = category.hazard_class.python_hazard_class
                    if python_hazard_class.ld50_field in hazard_dict:
                        ld50 = hazard_dict[python_hazard_class.ld50_field]

                flavor_cat_info = FlavorCategoryInfo(
                    flavor = self,
                    category = category,
                    ld50 = ld50
                )

                flavor_cat_info.save()

        return hazard_dict

    def get_ld50s(self):
        #returns human readable ld50s of a flavor, if it has any
        ld50_dict = {}
        for cat_info in self.flavorcategoryinfo_set.all():
            if cat_info.ld50:
                human_readable_ld50 = cat_info.category.hazard_class.python_hazard_class.human_readable_ld50
                ld50_dict[human_readable_ld50] = cat_info.ld50

        return ld50_dict


    def get_hazards(self): #does not create any objects
        formula_list = self.get_hazard_formula_list()

        return calculate_flavor_hazards(formula_list)

    def get_accumulator(self):
        formula_list = self.get_hazard_formula_list()

        return HazardAccumulator(formula_list)

    def get_hazards_url(self):
        try:
            return create_fli_url(self.get_hazard_formula_list(), self.__str__())
        except NoFormulaError as e:
            return e.__str__()

    def get_sds_url(self):
        return '/access/safety_data_sheet/%s' % self.number

    @property
    def merged_hcode_info(self):
        if not hasattr(self, '_hcode_info'):
            self._hcode_info = collections.defaultdict(set)
            for hc in self.hazard_set.all():
                if hc.hcode != None:
                    hcode_info = hc.get_hcode_info()
                    for k,v in hcode_info.items():
                        if k == 'p_codes':
                            self._hcode_info[k] = self._hcode_info[k].union(v)
                        else:
                            self._hcode_info[k].add(v)

        return self._hcode_info

    def create_label_objects(self):
        #we need hazard statements and precautionary statements to be objects so they can be directly used in labelview
        #might want to reimplement the whole thing because a lot of the code assumes that they are only hardcoded in one location
        hcode_info = self.merged_hcode_info

        PrecautionaryStatement.objects.filter(flavor=self).delete()
        HazardStatement.objects.filter(flavor=self).delete()
        GHSPictogram.objects.filter(flavor=self).delete()
        GHSSignalWord.objects.filter(flavor=self).delete()

        if hcode_info['statement']:
            for statement in hcode_info['statement']:
                hazard_statement = HazardStatement(flavor = self,
                                                   statement = statement)
                hazard_statement.save()
        else:
            hazard_statement = HazardStatement(flavor = self,
                                               statement = 'This product has no hazard statements.')
            hazard_statement.save()

        if hcode_info['p_codes']:
            for pcode in hcode_info['p_codes']:
                precautionary_statement = PrecautionaryStatement(flavor = self,
                                                                 statement = pcode_dict[pcode])
                precautionary_statement.save()
        else:
            precautionary_statement = PrecautionaryStatement(flavor=self,
                                                             statement = 'This product has no precautionary statements')
            precautionary_statement.save()

        for pictogram_code in hcode_info['pictogram_code']:
            ghs_pictogram = GHSPictogram(flavor = self,
                                         pictogram_code = pictogram_code,
                                         pictogram_location = '%s.png' % pictogram_code)
            ghs_pictogram.save()

        if hcode_info['signal_word']:
            for signal in hcode_info['signal_word']:
                ghs_signal_word = GHSSignalWord(flavor = self,
                                                signal_word = signal)
                ghs_signal_word.save()
        else:
            ghs_signal_word = GHSSignalWord(flavor=self,
                                            signal_word = 'Not Hazardous')
            ghs_signal_word.save()


    def create_label_csv(self):
        hcode_info = self.merged_hcode_info
        from django.conf import settings
        static_root = settings.STATIC_ROOT
        #elements 1-5: pictogram codes
        data = []
        for pictogram_code in hcode_info['pictogram_code']:
            data.append('%s/images/pictograms/%s.png' % (static_root, pictogram_code))

        #if there are less than 5 pictograms, fill the rest with empty string
        while len(data) < 5:
            data.append('%s/images/pictograms/black.png' % static_root)

        data.append('%s-%s' % (self.prefix, self.number)) #element 6: flavor prefix - number
        data.append(self.name)                            #element 7: flavor name

        data.append(hcode_info['signal_word']) #element 8: signal words
        data.append(' '.join(hcode_info['statement'])) #element 9: hcode statements

        precautionary_statements = []
        for pcode in hcode_info['p_codes']:
            precautionary_statements.append((pcode_dict[pcode]))


        data.append(' '.join(precautionary_statements))

        time_stamp = datetime.now().isoformat()

        filename = '/tmp/%s.csv' % self.number
        with open(filename, 'wb') as csvfile:
            label_writer = csv.writer(csvfile, delimiter=',')
            label_writer.writerow(data)

        return filename

    # @property
    # def gmo_percentage(self):
    #     gmo_weight = 0
    #     total_weight = 0
    #
    #     for lw in LeafWeight.objects.filter(root_flavor=self):
    #         total_weight += lw.weight
    #         if 'yes' in lw.ingredient.gmo.lower():
    #             gmo_weight += lw.weight
    #
    #     if total_weight > 0:
    #         gmo_percentage = Decimal(gmo_weight/total_weight) * 100
    #     else:
    #         gmo_percentage = 0
    #
    #     return gmo_percentage

    @property
    def new_gmo_calculation(self):
        gmo_weight = 0
        total_weight = 0

        for lw in LeafWeight.objects.filter(root_flavor=self):

            total_weight += lw.weight
            if lw.ingredient.new_gmo == 'Genetically Modified':
                gmo_weight += lw.weight

        if total_weight > 0:
            gmo_percentage = Decimal(gmo_weight/total_weight) * 100
        else:
            gmo_percentage = 0

        return gmo_percentage

    @property
    def missing_gmo_data(self):

        ingredients_missing_data = []

        for lw in LeafWeight.objects.filter(root_flavor=self):
            if lw.ingredient.new_gmo == '' or lw.ingredient.new_gmo == None:
                ingredients_missing_data.append(lw.ingredient)

        if ingredients_missing_data:
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.url, x.id) for x in ingredients_missing_data]))
            return_string = 'Missing GMO data for the following ingredients: %s' % ingredient_urls

            return return_string

        return False

    @property
    def new_gmo_string(self):

        if not LeafWeight.objects.filter(root_flavor=self).exists():
            return "Missing Formula"
        if self.missing_gmo_data:
            #return "%s - %s" % (self.new_gmo, self.missing_gmo_data)
            #only show missing data
            return self.missing_gmo_data
        else:
            return self.new_gmo

    # @property
    # def gmo(self):
    #     # Only display GMO Free, GMO Non-Detect, or Genetically Modified
    #     gmo_set = LeafWeight.objects.filter(root_flavor=self).values_list('ingredient__new_gmo', flat=True)
    #     if 'Genetically Modified' in gmo_set:
    #         return 'Genetically Modified'
    #     elif 'GMO Non-Detect' in gmo_set:
    #         return 'GMO Non-Detect'
    #     else:
    #         return 'GMO Free'

    @property
    def new_gmo(self):
        # Only display GMO Free, GMO Non-Detect, or Genetically Modified
        gmo_set = LeafWeight.objects.filter(root_flavor=self).values_list('ingredient__new_gmo', flat=True)
        if 'Genetically Modified' in gmo_set:
            genetically_modified_list = LeafWeight.objects.filter(root_flavor=self, ingredient__new_gmo="Genetically Modified")
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.ingredient.url, x.ingredient.id) for x in genetically_modified_list]))
            return 'Genetically Modified because: %s' % ingredient_urls
        elif 'GMO Non-Detect' in gmo_set:
            non_detect_list = LeafWeight.objects.filter(root_flavor=self, ingredient__new_gmo="GMO Non-Detect")
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.ingredient.url, x.ingredient.id) for x in non_detect_list]))
            return 'GMO Non-Detect because: %s' % ingredient_urls
        else:
            return 'GMO Free'

    @property
    def gmo_print_review(self): #kind of an ugly workaround to get rid of the 'because: ...' for GMO in the flavor printout page
        return ' '.join(self.new_gmo.split()[:2])


    @property
    def calculated_organic_compliant(self):
        organic_compliant_set = LeafWeight.objects.filter(root_flavor=self).values_list('ingredient__organic_compliant', flat=True)
        if False in organic_compliant_set:
            non_organic_list = LeafWeight.objects.filter(root_flavor=self, ingredient__organic_compliant=False)
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.ingredient.url, x.ingredient.id) for x in non_organic_list]))
            return "False because: %s" % ingredient_urls
        else:
            return True

    @property
    def missing_organic_compliant_data(self):
        ingredients_missing_data = []

        for lw in LeafWeight.objects.filter(root_flavor=self):
            if lw.ingredient.organic_compliant == None:
                ingredients_missing_data.append(lw.ingredient)

        if ingredients_missing_data:
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.url, x.id) for x in ingredients_missing_data]))
            return_string = 'Missing Organic Compliant data for the following ingredients: %s' % ingredient_urls

            return return_string

        return False

    @property
    def organic_compliant_string(self):

        if not LeafWeight.objects.filter(root_flavor=self).exists():
            return "Missing Formula"
        if self.missing_organic_compliant_data:
            return self.missing_organic_compliant_data
        else:
            return self.calculated_organic_compliant

    @property
    def calculated_vegan(self):
        vegan_set = LeafWeight.objects.filter(root_flavor=self).values_list('ingredient__vegan', flat=True)
        if False in vegan_set:
            non_vegan_list = LeafWeight.objects.filter(root_flavor=self, ingredient__vegan=False)
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.ingredient.url, x.ingredient.id) for x in non_vegan_list]))
            return "False because: %s" % ingredient_urls
        else:
            return True

    @property
    def missing_vegan_data(self):
        ingredients_missing_data = []

        for lw in LeafWeight.objects.filter(root_flavor=self):
            if lw.ingredient.vegan == None:
                ingredients_missing_data.append(lw.ingredient)

        if ingredients_missing_data:
            ingredient_urls = ", ".join((['<a href=%s>%s</a>' % (x.url, x.id) for x in ingredients_missing_data]))
            return_string = 'Missing Organic Compliant data for the following ingredients: %s' % ingredient_urls

            return return_string

        return False


    @property
    def gluten_ppm(self):
        ppm = 0

        for lw in LeafWeight.objects.filter(root_flavor=self):
            ppm += lw.ingredient.gluten_ppm * lw.weight / Decimal('1000')

        return ppm

    # def update_rm_inventory(self, amount):
    #     for lw in LeafWeight.objects.filter(root_flavor=self):
    #         i = lw.ingredient
    #         i.inventory -= (lw.weight)/1000 * amount #subtract the amount of the ingredient in the flavor
    #         i.save()

    def consolidate_formula(self):
        #This method will be used to fix any instances where there are two formulas with the same ingredient
        #Iterate through each formula, add the ingredient to a set, and if it's already in the set then add its weight

        ingredients = set()

        for formula in Formula.objects.filter(flavor=self):
            if formula.ingredient in ingredients:
                #add the weight of the duplicate formula to the first formula with this ingredient, then delete the dupe
                non_dupe_formula = Formula.objects.filter(flavor=self,ingredient=formula.ingredient)[0]
                non_dupe_formula.amount += formula.amount
                non_dupe_formula.save()

                formula.delete()

            ingredients.add(formula.ingredient)


    def get_field_status(self, field_name):
        #Determine whether a field has been verified by looking for the corresponding Document/DocumentVerification objects

        #1. Create a data structure linking field names to doctypes
        #2. Use the field name to obtain the corresponding doctype
        #3. Filter DocumentVerification objects to see if there is currently an unexpired, verified Document

        if field_name in flavor_field_to_doctype_dict:
            corresponding_doctype = flavor_field_to_doctype_dict[field_name]

            status = 'Verified'

            for lw in LeafWeight.objects.filter(root_flavor=self):

                #just use the Ingredient model's get_field_status for each leafweight to determine whether the corresponding field is completely verified
                if lw.ingredient.get_field_status(field_name) != 'Verified':
                    status = 'Unverified'

            return status

        else:
            return 'N/A'

    def update_text_allergen(self, allergen_name, value):
        current_value = getattr(self, allergen_name)
        if current_value == '':
            setattr(self, allergen_name, value)
        else:
            new_value = current_value + ', ' + value
            setattr(self, allergen_name, new_value)

    def get_allergen_text(self):
        #return the combined allergen text in the format 'Yes: a1, a2, a3..'
        allergen_text = 'None'
        allergens = set()
        for allergen in Ingredient.boolean_allergens:
            if getattr(self, allergen):
                allergens.add(allergen)

        for allergen in Ingredient.text_allergens:
            if getattr(self, allergen):
                allergens.add('%s (%s)' % (allergen, getattr(self, allergen)))

        if self.sulfites == True:
            allergens.add('sulfites')

        if len(allergens) > 0:
            allergen_text = "Yes: %s" % ','.join(allergens)

        return allergen_text


class NoFormulaError(Exception):
    #this is used above and is raised when a flavor has no consolidated leaves
    def __init__(self, num=None):
        self.num = num

    def __str__(self):
        if self.num:
            return "Flavor %s has no formula; cannot calculate hazards" % self.num

class FlavorIterOrder(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)

    def __str__(self):
        return self.flavor.__str__()

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExperimentalLog(models.Model):
    """
    Records of completed ExperimentalProducts.

    TODO FIX ME!!
    """
    ingredients = models.ManyToManyField(
            Ingredient,
            through='ExperimentalFormula')
    experimentalnum = models.PositiveIntegerField(
                            unique=True,
                            db_column='ExperimentalNum')
    datesent = models.DateTimeField(
                            db_column='DateSent')
    customer = models.CharField( # FIX null=True later
                            max_length=50,
                            db_column='Customer',
                            null=True)
    product_name = models.CharField(
                            max_length=100,
                            db_column='ProductName')
    label_type = models.CharField(
            max_length=50,
            blank=True)
    product_category = models.CharField(
            max_length=100,
            blank=True,
            null=True,
            choices=PRODUCT_CATEGORY_CHOICES)
    natart = models.CharField(max_length=50,blank=True)

    #NEW FIELDS
    #physical_property
#     wonf_type = models.CharField(
#             "Wonf/Type",
#             max_length=50,
#             blank=True,
#             choices=WONF_TYPE_CHOICES)
#     organic_compliant = models.CharField( #replaces old organic field
#             "Organic Compliant",
#             max_length=50,
#             choices=ORGANIC_COMPLIANT_CHOICES,
#             default="Undetermined")
#     physical_property = models.CharField(
#             "Physical Property",
#             max_length=50,
#             choices=PHYSICAL_PROPERTY_CHOICES,
#             default="Undetermined")
#     concentrate = models.CharField( #this replaces old concentrate field
#             "Concentrate",
#             max_length=50,
#             blank=True,
#             choices=CONCENTRATE_CHOICES,
#             default="Undetermined")
#     oil_soluble = models.CharField( #this replaces old oilsoluble field
#             "Oil Soluble",
#             max_length=50,
#             blank=True,
#             choices=OIL_SOLUBLE_CHOICES,
#             default="Undetermined")
    #END NEW FIELDS

    initials = models.CharField(
                            max_length=2,
                            db_column='Initials')
    memo = models.TextField(db_column='Memo',
                            null=True,
                            blank=True)
    color = models.CharField(max_length=50,blank=True)
    organoleptics = models.CharField(max_length=50,blank=True)
    mixing_instructions = models.TextField(blank=True)
    yield_field = models.PositiveIntegerField('Percent Yield', blank=True, null=True, default=100)

    liquid = models.BooleanField(db_column='Liquid', default=False)
    dry = models.BooleanField(db_column='Dry', default=False)
    spraydried = models.BooleanField(db_column='Spray Dried', default=False) # Field renamed to remove spaces.lc
    flavorcoat = models.BooleanField("Flavorcoat®", db_column="Flavor Coat", default=False)
    concentrate = models.BooleanField(db_column='Concentrate', default=False)
    oilsoluble = models.BooleanField("Oil soluble", db_column='OilSoluble', default=False)

    na = models.BooleanField("N/A",db_column='N/A', default=False)
    natural = models.BooleanField(db_column='Natural', default=False)
    artificial = models.BooleanField(blank=True,default=False)
    nfi = models.BooleanField("NFI", blank=True,default=False)
    nfi_n = models.BooleanField("NFI", blank=True, default=False)
    nfi_a = models.BooleanField("NFI", blank=True, default=False)
    ttb = models.BooleanField("TTB", blank=True,default=False)
    organic_compliant_required = models.BooleanField("Organic Compliant", db_column='Organic',blank=True,default=False)
    organic_certified_required = models.BooleanField("Organic Certified", blank=True,default=False)

    wonf = models.BooleanField("Natural WONF",db_column='WONF', default=False, blank=True)
    natural_type = models.BooleanField("Natural Type", blank=True, default=False)

    duplication = models.BooleanField(db_column='Duplication',blank=True, default=False)
    duplication_company = models.CharField(max_length=50,blank=True)
    duplication_id = models.CharField(max_length=50, blank=True)
    duplication_name = models.CharField(max_length=50,blank=True)
    promotable = models.BooleanField(db_column='Promotable', default=False)
    holiday = models.BooleanField(db_column='Holiday', default=False)
    chef_assist = models.BooleanField(db_column='Chef Assist', default=False) # Field renamed to remove spaces.lc

    experimental_number = models.PositiveIntegerField(db_column='Experimental Number', default=0) # Field renamed to remove spaces.lc
    spg = models.DecimalField(decimal_places=3,
                              max_digits=4,
                              db_column='SpG',
                              default=0)
    flash = models.PositiveIntegerField(
                                db_column='Flash',
                                default=0)

    usagelevel = models.DecimalField(
                                decimal_places=4,
                                max_digits=6,
                                db_column='UsageLevel',
                                default=0)

    # FOREIGN KEY
    product_number = models.PositiveIntegerField(null=True,blank=True,db_column='ProductNumber')
    #flavor = models.OneToOneField('Flavor',null=True)
    # END FOREIGN KEY



    coffee = models.BooleanField(db_column='Coffee', default=False)
    tea = models.BooleanField(db_column='Tea', default=False)
    fruit = models.BooleanField(db_column='Fruit', default=False)
    sweet = models.BooleanField(db_column='Sweet', default=False)
    nutraceutical = models.BooleanField(db_column='Nutraceutical', default=False)
    personal_care = models.BooleanField(db_column='Personal Care', default=False)  # Field renamed to remove spaces.lc
    meat_and_savory = models.BooleanField(db_column='Meat and Savory', default=False)  # Field renamed to remove spaces.lc
    beverage = models.BooleanField(db_column='Beverage', default=False)
    chai = models.BooleanField(db_column='Chai', default=False)
    baked_goods = models.BooleanField(db_column='Baked Goods', default=False)  # Field renamed to remove spaces.lc
    dairy = models.BooleanField(db_column='Dairy', default=False)
    pet = models.BooleanField(db_column='Pet', default=False)
    snacks = models.BooleanField(db_column='Snacks', default=False)
    tobacco = models.BooleanField(db_column='Tobacco', default=False)
    non_food = models.BooleanField(db_column='Non-Food', default=False)  # Field renamed to remove dashes.lc

    retain_number = models.PositiveIntegerField(db_column='RetainNumber', null=True, blank=True)
    retain_present = models.BooleanField(db_column='RetainPresent', default=False)

    flavor = models.ForeignKey('Flavor', related_name='experimental_log', blank=True, null=True,on_delete=models.CASCADE)
    location_code_old = models.CharField(blank=True, default="", max_length=20)
    exclude_from_reporting = models.BooleanField(default=False)
    def __str__(self):
        return "%s-%s %s %s %s %s" % (self.experimentalnum, self.initials,
                                self.natart, self.product_name, self.label_type, self.datesent_short)

    label_properties = (
        'wonf',
        'natural_type',
        'organic',
        'liquid',
        'dry',
        'spraydried',
        'concentrate',
        'oilsoluble',
        'flavorcoat', # ®
        'na',
        'natural',
        'artificial',
        'nfi',
    )
    incompatible_categories = {
        'wonf':(
            'natural_type',
            'na',
            'artificial',
        ),
        'liquid':(
            'dry',
            'spraydried',
        ),
        'spraydried':(
            'oilsoluble',
            'dry',
        ),
        'flavorcoat':(
            'liquid',
            'dry',
            'spraydried',
            'concentrate',
            'oilsoluble',
        ),
        'na':(
            'natural_type',
            'organic_compliant_required',
            'organic_certified_required',
            'natural',
            'artificial',
            'nfi',
        ),
        'artificial':(
            'natural_type',
            'natural',
            'nfi',
            'organic_compliant_required',
            'organic_certified_required',
        ),
        'nfi':(
            'wonf',
            'natural_type',
            'organic_compliant_required',
            'organic_certified_required',
            'na',
            'natural',
            'artificial',
        ),
    }
    mandatory_categories = (
        ('na','natural','artificial','nfi', 'ttb',),
        ('liquid','dry','spraydried','flavorcoat'),
    )

    def clean_incompatible_categories(self):
        errors = []
        for p, incompatible_p in self.incompatible_categories.items():
            if getattr(self, p) == True:
                for ip in incompatible_p:
                    if getattr(self, ip) == True:
                        errors.append('%s and %s.' % (
                            self._meta.get_field(p)[0].verbose_name,
                            self._meta.get_field(ip)[0].verbose_name,
                        ))

        if len(errors) > 0:
            return ["Incompatible categories for experimental %s: %s" % (self.experimentalnum, " ".join(errors)),]
        else:
            return []

    def clean_mandatory_categories(self):
        errors = []
        for category in self.mandatory_categories:
            has_one = False
            for prop in category:
                if getattr(self, prop) == True:
                    has_one = True
            if not has_one:
                errors.append(str(category))
        if len(errors) > 0:
            return ["Missing property in required categories for experimental %s: %s" % (self.experimentalnum, " ".join(errors)),]
        else:
            return []

    def clean(self):
        errors = []
        errors.extend(self.clean_incompatible_categories())
        errors.extend(self.clean_mandatory_categories())
        if len(errors) > 0:
            raise ValidationError(" ".join(errors))


    def get_natart(self):
        for natart in ('na','artificial','natural','nfi','ttb'):
            if getattr(self, natart) == True:
                return self._meta.get_field(natart)[0].verbose_name

    def get_label_type(self):
        def check_tail_indices(tokens, label_tokens):
            for token in tokens:
                if getattr(self, token) == True:
                    label_tokens.append(self._meta.get_field(token)[0].verbose_name)

        label_tokens = [];
        tokens = ('dry','spraydried','oilsoluble','natural_type')

        check_tail_indices(tokens, label_tokens)

        if self.flavorcoat == True:
            label_tokens.append("Flavorcoat®")
        else:
            label_tokens.append("Flavor")

        tokens = ('concentrate','wonf','organic')

        check_tail_indices(tokens, label_tokens)
        return " ".join(label_tokens)

    #elog
    @property
    def location_code(self):
        try:
            return self.location_code_n.all().reverse()[0]
        except:
            if self.flavor is not None:
                return self.flavor.location_code

    @property
    def batchsheet_memo(self):
        if self.mixing_instructions != "":
            return "%s -- Mixing instructions: %s" % (self.memo, self.mixing_instructions)

    @staticmethod
    def anonymize():
        for e in ExperimentalLog.objects.all():
            lorem_one = q.get()
            lorem_two = q.get()
            lorem_three = q.get()
            lorem_four = q.get()
            print(e)
            e.product_name = "%s %s" % (lorem_one, lorem_two)
            e.customer = lorem_three
            e.memo = "%s %s %s %s" % (lorem_one, lorem_two, lorem_three, lorem_four)
            e.save()
            q.put(lorem_one)
            q.put(lorem_two)
            q.put(lorem_three)
            q.put(lorem_four)

    @property
    def table_name(self):
        return " ".join((self.product_name, self.label_type))

    def get_approve_link(self):
        if self.flavor.approved==True:
            return None
        elif self.flavor.valid == True:
            return "/access/experimental/%s/approve/" % self.experimentalnum
        else:
            return None

    @property
    def datesent_short(self):
        return self.datesent.date()

    def process_changes_to_flavor(self):
        EMPTY_FIELD_LIST = (None,"")
        if self.flavor.prefix == "EX":
            self.flavor.name = self.product_name
            self.flavor.natart = self.natart
            self.flavor.label_type = self.label_type

            if self.yield_field != None:
                self.flavor.yield_field = self.yield_field
            else:
                self.flavor.yield_field = 100

            if self.flash not in EMPTY_FIELD_LIST:
                self.flavor.flashpoint = self.flash

            if self.spg not in EMPTY_FIELD_LIST:
                self.flavor.spg = self.spg

            if self.organoleptics not in EMPTY_FIELD_LIST:
                self.flavor.organoleptics = self.organoleptics

            if self.color not in EMPTY_FIELD_LIST:
                self.flavor.color = self.color

            if self.yield_field not in EMPTY_FIELD_LIST:
                self.flavor.yield_field = self.yield_field
            self.flavor.save()

    def save(self, *args, **kwargs):
        if self.retain_number == -1:
            self.retain_number = 0
#         if self.flavor.prefix == "EX":
#             self.flavor.name = self.product_name
#             self.flavor.natart = self.natart
#             self.flavor.label_type = self.label_type
#             self.flavor()
        super(ExperimentalLog, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return '/access/experimental/%s/' % self.experimentalnum


    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
            if key == 'initials':
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'natart':
                keyword = "%s__in" % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = arg_list
            elif key == 'other':
                for my_arg in qdict.getlist(key):
                    #if my_arg == 'retains__notes':
                    #    string_kwargs['retains__notes'] = ''
                    if my_arg == 'liquid':
                        string_kwargs['liquid__in'] = [True]
                    elif my_arg == 'dry':
                        string_kwargs['dry__in'] = [True]
                    elif my_arg == 'spraydried':
                        string_kwargs['spraydried__in'] = [True]
                    elif my_arg == 'oilsoluble':
                        string_kwargs['oilsoluble__in'] = [True]
                    elif my_arg == 'concentrate':
                        string_kwargs['concentrate__in'] = [True]
        return string_kwargs

    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(ExperimentalLog, experimentalnum=softkey).get_absolute_url()
        except:
            return None

    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            return ExperimentalLog.objects.get(experimentalnum=softkey)
        except:
            return None

    def get_related_links(self):
        related_links = []
        if self.product_number != None and self.product_number != 0:
            related_links.append(
                ('/access/%s/' % self.product_number, 'Flavor Formula')
            )
        related_links.append(('/access/experimental/%s/' % self.experimentalnum,'Experimental'))

        return related_links

    def get_admin_url(self):
        return "/admin/access/experimentallog/%s" % self.id

    import_order = 3

    @property
    def yield_adjusted_rmc(self):
        y = self.yield_field

        if y != zero:
            return self.rawmaterialcost / (y / one_hundred)
        else:
            return self.rawmaterialcost

    class Meta:
        db_table = 'ExperimentalLog'
        ordering = ['experimentalnum']
    headers = (
                    ('experimentalnum','Number', 'width="80px"'),
                    ('natart','N-A', 'width="90px"'),
                    ('table_name','Name', ''),
                    ('initials','Initials', 'width=30x'),
                    ('datesent_short','Date sent', 'width=100px'),
                    ('duplication_company','Dup. Company', 'width=100px'),
                    ('duplication_id','Dup. ID', 'width=80px'),
                )

    @staticmethod
    def text_search(search_string):
        return ExperimentalLog.objects.filter(
            Q(product_name__icontains=search_string) #|
            #Q(memo__icontains=search_string)
        )

    @staticmethod
    def fix_header(header):
        if header == 'datesent_short':
            return 'datesent'
        else:
            return header

class ShipTo(models.Model):
    """Incoming shipping destinations
    """
    shiptoid = models.PositiveIntegerField(primary_key=True, db_column='ShipToID')
    shiptoaddress = models.CharField(max_length=50, db_column='ShipToAddress')
    shiptocontact = models.CharField(max_length=50, db_column='ShipToContact')
    shiptocity = models.CharField(max_length=50, db_column='ShipToCity')
    shiptoregion = models.CharField(max_length=50, db_column='ShipToRegion')
    shiptopostalcode = models.CharField(max_length=50, db_column='ShipToPostalCode')
    shiptocountry = models.CharField(max_length=50, db_column='ShipToCountry')
    shiptophone = models.CharField(max_length=50, db_column='ShipToPhone')
    shiptofax = models.CharField(max_length=50, db_column='ShipToFax')
    shiptocontacttitle = models.CharField(max_length=50, db_column='ShipToContactTitle')
    shiptoname = models.CharField(max_length=50, db_column='ShipToName')

    import_order = 99

    class Meta:
        db_table = 'ShipTo'

    def __str__(self):
        return self.shiptoname

class Shipper(models.Model):
    """Shipping, logistics and/or freight companies.
    """
    shipperid = models.PositiveIntegerField(primary_key=True, db_column='ShipperID')
    shipper_name = models.CharField(max_length=40, db_column='Shipper Name') # Field renamed to remove spaces.lc
    phone = models.CharField(max_length=24, db_column='Phone')

    import_order = 99

    class Meta:
        db_table = 'Shippers'

    def __str__(self):
        return self.shipper_name

def next_id():
    if 'Supplier' in connection.introspection.table_names():
        if Supplier.objects.count() > 0:
            ss = Supplier.objects.all().order_by('id').reverse()[0]
            return ss.id + 1
    else:
        return None

def get_default_ship_to():
    if 'ShipTo' in connection.introspection.table_names():
        if ShipTo.objects.count() > 0:
            return ShipTo.objects.get(shiptoid=1)
    else:
        return None

class Supplier(models.Model):
    """
    Vendors which supply FDI with raw materials for products.
    """
    id = models.PositiveIntegerField(primary_key=True, db_column='ID', default=next_id)
    suppliercode = models.CharField(max_length=255, db_column='SupplierCode', blank=True)
    suppliername = models.CharField(max_length=255, db_column='SupplierName')
    contactname = models.CharField(max_length=255, db_column='ContactName', blank=True)
    contacttitle = models.CharField(max_length=255, db_column='ContactTitle', blank=True)
    address = models.CharField(max_length=255, db_column='Address', blank=True)
    city = models.CharField(max_length=255, db_column='City', blank=True)
    region = models.CharField(max_length=255, db_column='Region', blank=True)
    postalcode = models.CharField(max_length=255, db_column='PostalCode', blank=True)
    country = models.CharField(max_length=255, db_column='Country', blank=True)
    phone = models.CharField(max_length=255, db_column='Phone', blank=True)
    fax = models.CharField(max_length=255, db_column='Fax')
    supplierid = models.PositiveIntegerField(db_column='SupplierID', blank=True, null=True) #FIX this isn't unique in the source, convert to use the serial pk
    rawmaterialcode = models.PositiveIntegerField(db_column='RawMaterialCode', blank=True, null=True)
    homepage = models.CharField(max_length=255, db_column='HomePage', blank=True)
    email = models.CharField(max_length=255, db_column='EMail', blank=True)

    import_order = 99

    class Meta:
        db_table = 'Suppliers'
        ordering=['suppliername']

    def __str__(self):
        return self.suppliername

    def get_absolute_url(self):
        return "/access/purchase/supplier/%s/" % self.pk

    def save(self, *args, **kwargs):
        if self.suppliercode != "":
            super(Supplier,self).save(*args,**kwargs)
        else:
            existing_sup_codes = Supplier.objects.all().values_list('suppliercode')
            test_val = self.suppliername[:3].upper()
            test_val_cmp = (test_val,)
            count = 0
            while(True):
                count += 1
                if test_val_cmp in existing_sup_codes:
                    test_val = "%s%s" % (test_val[:3], count)
                    test_val_cmp = (test_val,)
                else:
                    self.suppliercode = test_val
                    break
            super(Supplier,self).save(*args,**kwargs)


class ExperimentalFormula(models.Model):
    """
    Constituent ingredients of a particular experimental formula.

    Depends on RawMaterial.
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    experimental_log = models.ForeignKey('ExperimentalLog',on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient',on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=3,
                                       max_digits=7,)

    def gazinta(self):
        try:
            return self.ingredient.sub_flavor
        except:
            raise FormulaException("%s contains an invalid formula row trying to point to flavor number: %s" %
                                  (self.flavor, self.ingredient.flavornum))

    def get_exploded_cost(self, weight_factor=1):
        if self.ingredient.is_gazinta:
            g = self.gazinta()
            y = g.yield_field

            if y == 0 or y == 100:
                rmc = g.rawmaterialcost
            else:
                if g.rawmaterialcost is None or y is None:
                    print("Updating %s" % g)
                    g.update_cost()
                rmc = g.rawmaterialcost * y / Decimal('100')

        else:
            rmc = self.ingredient.unitprice
        try:
            return self.amount * weight_factor * rmc / Decimal('1000')
        except TypeError:
            return Decimal('0')

    @property
    def relative_cost(self):
        return self.get_exploded_cost()

class Customer(models.Model):
    """
    Customer billing, shipping, and contact info.
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    rpsupsnumber = models.PositiveSmallIntegerField(
                db_column='RPS/UPSNumber',
                blank=True,
                null=True)
    companyname = models.CharField(
                max_length=60,
                db_column='CompanyName')
    billingaddress = models.CharField(
                max_length=60,
                db_column='BillingAddress',
                blank=True,
                null=True)
    billingaddress2 = models.CharField(
                max_length=60,
                db_column='BillingAddress2',
                blank=True,
                null=True)
    billingcity = models.CharField(
                max_length=35, db_column='BillingCity',
                blank=True,
                null=True)
    billingstate = models.CharField(
                max_length=2,
                db_column='BillingState',
                blank=True,
                null=True)
    billingzip = models.CharField(
                max_length=10,
                db_column='BillingZip',
                blank=True,
                null=True)
    shipaddress = models.CharField(
                max_length=60,
                db_column='ShipAddress',
                blank=True,
                null=True)
    shipaddress2 = models.CharField(
                max_length=20,
                db_column='ShipAddress2',
                blank=True,
                null=True)
    shipcity = models.CharField(
                max_length=35,
                db_column='ShipCity',
                blank=True,
                null=True)
    shipstate = models.CharField(
                max_length=2,
                db_column='ShipState',
                blank=True,
                null=True)
    shipzip = models.CharField(
                max_length=10,
                db_column='ShipZip',
                blank=True,
                null=True)
    billingphone = models.CharField(
                max_length=24,
                db_column='BillingPhone',
                blank=True,
                null=True)
    shipphone = models.CharField(
                max_length=24,
                db_column='ShipPhone',
                blank=True,
                null=True)
    billingfax = models.CharField(
                max_length=24,
                db_column='BillingFax',
                blank=True,
                null=True)
    shipfax = models.CharField(
                max_length=24, db_column='ShipFax',
                blank=True,
                null=True)
    customernotes = models.TextField(
                db_column='CustomerNotes',
                blank=True,
                null=True)
    customerid = models.CharField(
                max_length=5,
                db_column='CustomerID',
                blank=True,
                null=True) # pseudokey that other tables join on
    salesperson = models.CharField(
                max_length=20,
                db_column='Salesperson',
                blank=True,
                null=True)
    prefix = models.CharField(
                max_length=10,
                db_column='Prefix',
                blank=True,
                null=True)
    accountingcode = models.CharField(
                max_length=10,
                db_column='AccountingCode',
                blank=True,
                null=True)
    terms = models.CharField(
                max_length=10,
                db_column='Terms',
                blank=True,
                null=True)
    country = models.CharField(
                max_length=20,
                db_column='Country',
                blank=True,
                null=True)
    categoryid = models.PositiveIntegerField(
                db_column='CategoryID',
                blank=True,
                null=True) # fk to Categories
    fedex = models.CharField(
                max_length=11,
                db_column='Fedex',
                blank=True,
                null=True)
    region = models.CharField(
                max_length=20,
                db_column='Region',
                blank=True,
                null=True)
    extension = models.PositiveIntegerField(
                db_column='Extension',
                blank=True,
                null=True)
    contactname = models.CharField(
                max_length=30,
                db_column='ContactName',
                blank=True)
    gender = models.CharField(
                max_length=4,
                db_column='Gender',
                blank=True,
                null=True)
    contacttitle = models.CharField(
                max_length=30,
                db_column='ContactTitle',
                blank=True,
                null=True)
    address = models.CharField(
                max_length=60,
                db_column='Address',
                blank=True,
                null=True)
    city = models.CharField(
                max_length=25,
                db_column='City',
                blank=True,
                null=True)
    postalcode = models.CharField(
                max_length=10,
                db_column='PostalCode',
                blank=True,
                null=True)
    phone = models.CharField(
                max_length=24,
                db_column='Phone',
                blank=True,
                null=True)
    fax = models.CharField(
                max_length=24,
                db_column='Fax',
                blank=True,
                null=True)
    homepage = models.CharField(
                max_length=50,
                db_column='HomePage',
                blank=True,
                null=True)
    email = models.CharField(
                max_length=50,
                db_column='EMail',
                blank=True,
                null=True)
    customertype = models.CharField(
                max_length=10,
                db_column='CustomerType',
                blank=True,
                null=True)

    import_order = 99

    def __str__(self):
        return self.companyname

    class Meta:
        db_table = 'Customers'
        ordering=['companyname']

    @staticmethod
    def anonymize():
        for f in Customer.objects.all():
            lorem_one = q.get()
            lorem_two = q.get()
            print(f)
            f.companyname = "%s %s" % (lorem_one, lorem_two)
            f.save()

            q.put(lorem_one)
            q.put(lorem_two)

            print(f)
class ExperimentalProduct(models.Model):
    """
    Experimental products.

    Typically, there exists one object per flavorist. This exists as a
    scratch space. Products that complete the development cycle are checked
    into ExperimentalLog.
    """
    productid = models.PositiveIntegerField(primary_key=True, db_column='ProductID')
    flavornumber = models.PositiveIntegerField(db_column='FlavorNumber')
    product_name = models.CharField(max_length=40, db_column='ProductName')
    productprefix = models.CharField(max_length=2, db_column='ProductPrefix')
    flavorcode = models.CharField(max_length=2, db_column='FlavorCode')
    flavornatart = models.CharField(max_length=3, db_column='FlavorNatArt')
    flavortype = models.CharField(max_length=25, db_column='FlavorType')
    categoryid = models.PositiveIntegerField(db_column='CategoryID')
    unitprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='UnitPrice')
    quantityperunit = models.PositiveIntegerField(db_column='QuantityPerUnit')
    supplierid = models.PositiveIntegerField(db_column='SupplierID')
    unitsinstock = models.PositiveIntegerField(db_column='UnitsInStock')
    unitsonorder = models.PositiveIntegerField(db_column='UnitsOnOrder')
    reorderlevel = models.PositiveIntegerField(db_column='ReorderLevel')
    discontinued = models.BooleanField(db_column='Discontinued', default=False)
    approved = models.BooleanField(db_column='Approved', default=False)
    productmemo = models.TextField(db_column='ProductMemo')
    sold = models.BooleanField(db_column='Sold', default=False)
    spraydried = models.BooleanField(db_column='SprayDried', default=False)
    lastprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='LastPrice')
    experimental = models.CharField(max_length=50, db_column='Experimental')
    lastspdate = models.DateTimeField(db_column='LastSPDate')

    import_order = 99

    class Meta:
        db_table = 'Experimental Products'

class Incoming(models.Model):
    """
    Incoming R&D samples.

    Samples can be from clients (e.g. a target to duplicate), or raw materials
    from existing or prospective suppliers.
    """
    incomingid = models.PositiveIntegerField(primary_key=True, db_column='IncomingID')
    incdate = models.DateTimeField(db_column='IncDate')
    incname = models.CharField(max_length=50, db_column='IncName')
    inccompany = models.CharField(max_length=50, db_column='IncCompany')
    incid = models.CharField(max_length=50, db_column='IncID')
    incmemo = models.TextField(db_column='IncMemo')

    import_order = 99

    class Meta:
        db_table = 'Incoming'


def get_default_ship_to():
    if 'ShipTo' in connection.introspection.table_names():
        if ShipTo.objects.count() > 0:
            return ShipTo.objects.get(shiptoid=1)
    else:
        return None

def seven_days_from_now():
    return datetime.now() + timedelta(days=7)

def next_po_number():
    if 'access_purchaseorder' in connection.introspection.table_names():
        today =date.today()
        po_prefix = today.strftime('%y%m')
        ppn = int(po_prefix)*1000
        try:
            last_po_this_month = PurchaseOrder.objects.filter(number__gte=ppn).order_by('-number')[0]
            next_po_number = last_po_this_month.number + 1
        except:
            next_po_number = ppn + 1
        return next_po_number
    else:
        return None

class TSRLISortedManager(models.Manager):
    def get_queryset(self):
        return super(TSRLISortedManager, self).get_queryset().order_by('tsr__number')

class TSRLineItem(models.Model):
    objects = TSRLISortedManager()
    tsr = models.ForeignKey('TSR',on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, null=True, blank=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    product = fields.GenericForeignKey('content_type', 'object_id')

    code = models.PositiveIntegerField()
    usage = models.TextField(blank=True)


class TSR(models.Model):
    date_in = models.DateField(default=date.today)
    assigned_to = models.ForeignKey(User, related_name="assigned_TSRs",on_delete=models.CASCADE)
    entered_by = models.ForeignKey(User, related_name="entered_TSRs",on_delete=models.CASCADE)
    number = models.PositiveIntegerField(unique=True)
    date_out = models.DateField(null=True, blank=True)

    SHIPPING_METHOD_CHOICES = (
        ('red', 'UPS Red'),
        ('blue', 'UPS Blue'),
        ('orange', 'UPS Orange'),
        ('ground', 'UPS Ground'),
        ('international', 'International'),
    )

    shipping_method = models.CharField(max_length=20,
                                       choices=SHIPPING_METHOD_CHOICES)

    customer = models.ForeignKey('Customer',on_delete=models.CASCADE)
    contact = models.CharField(max_length=40)
    title = models.CharField(max_length=40, blank=True)
    telephone = models.CharField(max_length=20)
    country = models.CharField(max_length=30, blank = True)
    email = models.CharField(max_length=50)
    deadline = models.DateField(null=True, blank = True)

    headers = (
                ('number','Number', ''),
                ('date_in','Date In', ''),
                ('date_out','Date Out', ''),
                ('assigned_to', 'Assigned To', ''),
                ('customer','Customer', ''),
                ('contact','Contact', ''),
                ('telephone', 'Phone Number', ''),
                ('email','Email', ''),
            )

    #approvals needed
    kosher_parve = models.BooleanField(default=False)
    kosher_dairy = models.BooleanField(default=False) # not necessary
    usda = models.BooleanField(default=False, verbose_name="USDA") ##
    msds = models.BooleanField(default=False, verbose_name="MSDS") ## paperwork group of fields
    specs = models.BooleanField(default=False)                     ## add nutri, pricing
    cont_guar = models.BooleanField(default=False) # continuing guarantee
    finished_product = models.BooleanField(default=False) # showing finished system

    #flavor form
    liquid = models.BooleanField(default=False)
    dry = models.BooleanField(default=False)
    emulsion = models.BooleanField(default=False) # not necessary
    natural = models.BooleanField(default=False)
    wonf = models.BooleanField(default=False)
    NA = models.BooleanField(default=False)
    artificial = models.BooleanField(default=False)
    organic_comp = models.BooleanField(default=False)

    #requirements
    oil = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    coffee = models.BooleanField(default=False)
    tea = models.BooleanField(default=False) # black, green, herbal
    nopg = models.BooleanField(default=False)
    prop65 = models.BooleanField(default=False)
    nodiacetyl = models.BooleanField(default=False)
    overseas = models.BooleanField(default=False)

    #flash point targets "advise flash point"

    max_price = models.DecimalField(max_digits=7, decimal_places=2) ## max COST field
    lbs_per_year = models.PositiveIntegerField()
    exposed_to_heat = models.BooleanField(default=False)
    temperature = models.DecimalField(null=True, max_digits=5, decimal_places=3, blank=True)
    minutes = models.PositiveIntegerField(null=True, blank=True)

    japan = models.BooleanField(default=False)
    whole_foods = models.BooleanField(default=False)
    lab_select = models.BooleanField(default=False)

    description = models.TextField(max_length=200, verbose_name="Project Description")

    def __str__(self):
        return "%s - %s - %s" % (self.number, self.customer, str(self.date_in))

    def get_related_links(self):
        related_links = [('/access/tsr/%s/tsr_entry/' % self.number, 'Edit Items')]
        return related_links

    def get_absolute_url(self):
        return "/access/tsr/%s/" % self.number

    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            return TSR.objects.get(number=softkey)
        except:
            pass
        try:
            return TSR.objects.filter(number=softkey)[0]
        except:
            pass
        return None

    @staticmethod
    def text_search(search_string):
        return TSR.objects.filter(
            Q(customer__companyname__icontains=search_string)
            #Q(contact__icontains=search_string) |
            #Q(shipping_method__icontains=search_string) |
            #Q(tsrlineitem__code__icontains=search_string) #|
            #Q(tsrlineitem__product__product_name__icontains=search_string) |
            #Q(tsrlineitem__product__name__icontains=search_string)
        )

    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
            if key == 'assigned_to':
                keyword = '%s__id__in' % key
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(my_arg)
                string_kwargs[keyword] = qdict.getlist(key)
            if key == 'other':
                for my_arg in qdict.getlist(key):
                    if my_arg == 'open':
                        string_kwargs['date_out'] = None
#            if key == 'art_nati':
#                keyword = '%s__in' % (key)
#                arg_list = []
#                for my_arg in qdict.getlist(key):
#                    arg_list.append(my_arg)
#                string_kwargs[keyword] = arg_list
#            elif key == 'kosher':
#                keyword = '%s__in' % (key)
#                arg_list = []
#                for my_arg in qdict.getlist(key):
#                    arg_list.append(my_arg)
#                string_kwargs[keyword] = arg_list
#            else:

        return string_kwargs

class PurchaseOrder(models.Model):
    number = models.PositiveIntegerField(blank=True, default=next_po_number) #, default=next_po_number)
    shipper = models.ForeignKey('Shipper', default=38,on_delete=models.CASCADE)
    ship_to = models.ForeignKey('ShipTo', default=get_default_ship_to,on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier',on_delete=models.CASCADE)
    date_ordered = models.DateField(auto_now_add=True)
    memo = models.TextField(blank=True, default=" ALL KOSHER PRODUCTS MUST ARRIVE PER YOUR KOSHER CERTIFICATE OR THEY WILL BE REJECTED.")
    memo2 = models.TextField(blank=True, default="C OF A MUST ACCOMPANY SHIPMENT OR BE FAXED PRIOR TO RECEIVING ITEM")
    due_date = models.DateField(default=seven_days_from_now)
    receive_date = models.DateField(blank=True,null=True)
    qc_date = models.DateField(blank=True,null=True)

    headers = (
                ('number','Number', ''),
                ('due_date','Due Date', ''),
                ('supplier','Supplier', ''),
                ('date_ordered','Date Ordered', ''),
                ('shipper','Shipper', ''),
                ('receive_date','Receive Date', ''),
                ('qc_date','QC Date', ''),
            )

    def __str__(self):
        return "%s - %s - %s" % (self.number, str(self.due_date), self.supplier)

    class Meta:
        ordering=['-date_ordered']

    def get_related_links(self):
        related_links = [('/access/purchase/%s/po_entry/' % self.number, 'Edit Items')]
        return related_links

    def get_absolute_url(self):
        return "/access/purchase/%s/" % self.number

    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(PurchaseOrder, number=softkey).get_absolute_url()
        except:
            pass
        try:
            return PurchaseOrder.objects.filter(number=softkey)[0].get_absolute_url()
        except:
            pass

        return None

    @staticmethod
    def get_object_from_softkey(softkey):
        try:
            return PurchaseOrder.objects.get(number=softkey)
        except:
            pass
        try:
            return PurchaseOrder.objects.filter(number=softkey)[0]
        except:
            pass
        return None

    @staticmethod
    def fix_header(header):
        return header

    @staticmethod
    def text_search(search_string):
        return PurchaseOrder.objects.filter(
            #Q(memo__icontains=search_string) |
            Q(supplier__suppliername__icontains=search_string) |
            Q(purchaseorderlineitem__raw_material__rawmaterialcode__icontains=search_string) |
            Q(purchaseorderlineitem__raw_material__id__icontains=search_string) |
            Q(purchaseorderlineitem__raw_material__product_name__icontains=search_string) |
            Q(memo2__icontains=search_string)
        )

    @staticmethod
    def build_kwargs(qdict, default, get_filter_kwargs):
        string_kwargs = {}
        for key in get_filter_kwargs(qdict):
#            if key == 'art_nati':
#                keyword = '%s__in' % (key)
#                arg_list = []
#                for my_arg in qdict.getlist(key):
#                    arg_list.append(my_arg)
#                string_kwargs[keyword] = arg_list
#            elif key == 'kosher':
#                keyword = '%s__in' % (key)
#                arg_list = []
#                for my_arg in qdict.getlist(key):
#                    arg_list.append(my_arg)
#                string_kwargs[keyword] = arg_list
#            else:
            keyword = '%s__in' % (key)
            arg_list = []
            for my_arg in qdict.getlist(key):
                arg_list.append(bool(int(my_arg)))
            string_kwargs[keyword] = arg_list
        return string_kwargs


class POLISortedManager(models.Manager):
    def get_queryset(self):
        return super(POLISortedManager, self).get_queryset().order_by('po__number')

class PurchaseOrderLineItem(models.Model):
    objects = POLISortedManager()
    po = models.ForeignKey('PurchaseOrder',on_delete=models.CASCADE)
    raw_material = models.ForeignKey('Ingredient',on_delete=models.CASCADE)
    memo = models.TextField(blank=True)
    memo2 = models.TextField(blank=True)
    quantity = models.DecimalField(decimal_places=2, max_digits=7,default=0)
    due_date = models.DateField(default=seven_days_from_now)
    package_size = models.DecimalField(decimal_places=3, max_digits=7,default=0)
    purchase_price = models.DecimalField(decimal_places=3, max_digits=10, default=0)
    legacy_purchase = models.OneToOneField('LegacyPurchase',on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        try:
            lp = self.legacy_purchase
            if lp is None:
                lp = LegacyPurchase()
        except:
            lp = LegacyPurchase()
        po = self.po
        self.raw_material.date_ordered = po.date_ordered
        self.raw_material.save()
        lp.shipperid = po.shipper.shipperid
        lp.shiptoid = po.ship_to.shiptoid
        lp.suppliercode = po.supplier.suppliercode
        lp.rawmaterialcode = self.raw_material.rawmaterialcode
        lp.dateordered = po.date_ordered
        #lp.datereceived = self.date_received
        lp.pomemo = po.memo
        lp.pomemo2 = po.memo2
        lp.ponumber = po.number
        lp.poquantity = self.quantity
        lp.poduedate = po.due_date
        lp.packagesize = self.package_size
        lp.save()
        self.legacy_purchase = lp
        super(PurchaseOrderLineItem,self).save(*args,**kwargs)

    @property
    def received(self): #will return True if there is a corresponding receivinglog - even if there is a backlog/the PO is still open
        if self.receivinglog_set.count() > 0:
            return True
        else:
            return False
#         if hasattr(self, 'receivinglog'):
#             return True
#         else:
#             return False

    @property
    def total_amount_received(self):
        total_amount_received = 0
        for rl in self.receivinglog_set.all():
            total_amount_received += rl.amount_received

        return total_amount_received

    @property
    def total_amount_requested(self):
        return self.quantity * self.package_size

    def __str__(self):
        return "%s - %s - %s" % (self.po, self.raw_material, self.quantity)

    class Meta:
        ordering = ['po__number', ]

def legacy_purchase_auto_number():
    if 'Purchases' in connection.introspection.table_names():
        if LegacyPurchase.objects.count() > 0:
            return LegacyPurchase.objects.all().order_by('-poentry')[0].poentry + 1
        else:
            return 1
    else:
        return None

class LegacyPurchase(models.Model):
    """Records of raw material purchases.
    """
    #    * The original field, SupplierCode, was modified to SupplierID and points
    # to the numeric primary key field of the Suppliers table
    # IMPORT FROM KRISTY'S DATABASE
    #
    poentry = models.PositiveIntegerField(primary_key=True, db_column='POEntry', default=legacy_purchase_auto_number)
    shipperid = models.PositiveIntegerField(db_column='ShipperID', blank=True, null=True) # CONVERT TO FC
    shiptoid = models.PositiveIntegerField(db_column='ShipToID', blank=True, null=True) # CONVERT TO FC
    #original line:
    suppliercode = models.CharField(max_length=50, db_column='SupplierCode', blank=True, null=True) # need to add a foreign key to update this; essential to the access app
    #supplierid = models.ForeignKey('Supplier') #FIX
    orderid = models.PositiveIntegerField(db_column='OrderID', blank=True, null=True, default=0)
    rawmaterialcode = models.PositiveIntegerField(db_column='RawMaterialCode', blank=True, null=True)
    dateordered = models.DateField(db_column='DateOrdered', blank=True, null=True)
    datereceived = models.DateField(db_column='DateReceived', blank=True, null=True)
    pomemo = models.TextField(db_column='POMemo', blank=True, null=True, default=" ALL KOSHER PRODUCTS MUST ARRIVE PER YOUR KOSHER CERTIFICATE OR THEY WILL BE REJECTED.")
    ponumber = models.PositiveIntegerField(db_column='PONumber', blank=True, null=True)
    poquantity = models.DecimalField(decimal_places=2, max_digits=7, db_column='POQuantity', blank=True, null=True)
    poduedate = models.DateField(db_column='PODueDate', blank=True, null=True)
    packagesize = models.DecimalField(decimal_places=3, max_digits=7, db_column='PackageSize')
    pomemo2 = models.TextField(db_column='POMEMO2',
                               blank=True,
                               default="C OF A MUST ACCOMPANY SHIPMENT OR BE FAXED PRIOR TO RECEIVING ITEM",
                               null=True)

    import_order = 99

    class Meta:
        db_table = 'Purchases'
        ordering=['ponumber']

    def __str__(self):
        return str(self.ponumber)


def get_lorem_queue():
    loremfile = open('/var/www/django/fd/loremipsum.txt', 'r')
    lorems = loremfile.read().split(',')
    q = queue.Queue()
    for word in lorems[0:len(lorems)-1]:
        q.put(word)
    return q
q = get_lorem_queue()

class JIList(models.Model):
    a = models.PositiveIntegerField(db_index=True)
    b = models.PositiveIntegerField(db_index=True)
    score = models.FloatField()

    class Meta:
        ordering=['-score', 'a']


class AllerIngredients(Ingredient):
    class Meta:
        proxy=True

class FlavorRiskAssessment(Flavor):
    class Meta:
        proxy=True

class IngredientDescription(Ingredient):
    class Meta:
        proxy=True

class Renumber(models.Model):
    a = models.ForeignKey('Flavor', related_name="renum_a_set",on_delete=models.CASCADE)
    b = models.ForeignKey('Flavor', related_name="renum_b_set",on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', blank=True, null=True,on_delete=models.CASCADE)

class Solvent(models.Model):
    ingredient = models.OneToOneField('Ingredient', primary_key=True, related_name="solvent_listing",on_delete=models.CASCADE)
    def __str__(self):
        return str(self.ingredient)

    @staticmethod
    def get_name_from_name(solvent_number):
        return "%s %s" % (Ingredient.get_obj_from_softkey(solvent_number).prefix, Ingredient.get_obj_from_softkey(solvent_number).product_name)

    @staticmethod
    def get_id_list():
        return Solvent.objects.all().values_list('ingredient__id',flat=True)

class FormulaException(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class FormulaCycleException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return ("Cycle detected on the following sequence of "
                "flavor numbers: " + str(self.value))

    def build_failed_superlist(self):
        failed_flavor_numbers = self.value[:]
        self.failed_superlist = {}
        for cycle_flavor_number in failed_flavor_numbers:
            cycle_flavor = Flavor.objects.get(number=cycle_flavor_number)
            try:
                cycle_ingredient = cycle_flavor.ingredient_set.all()[0]
            except:
                self.failed_superlist[cycle_flavor.flavor.number] = 1
                continue
            cycle_formula_rows = Formula.objects.filter(ingredient=cycle_ingredient)
            for cfr in cycle_formula_rows:
                if cfr.flavor.number in self.failed_superlist:
                    pass
                else:
                    self.failed_superlist[cfr.flavor.number] = 1
                    failed_flavor_numbers.append(cfr.flavor.number)
        return self.failed_superlist

class FormulaWeightException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "Flavor ingredients do not add to 1000: %s" % repr(self.value)

class FEMAIngredient(Ingredient):
    @staticmethod
    def get_absolute_url_from_softkey(search_string):
        try:
            return get_object_or_404(Ingredient, fema=search_string).get_absolute_url()
        except:
            pass

        return None

    @staticmethod
    def get_object_from_softkey(search_string):
        try:
            return Ingredient.objects.get(fema=search_string)
        except:
            pass
        return None

    @staticmethod
    def text_search(search_string):
        return Ingredient.objects.filter(
            fema=search_string
        )

class AntisepticIngredient(models.Model):
    pin = models.PositiveSmallIntegerField()
    concentration = models.PositiveSmallIntegerField()

    def __str__(self):
        return "%s -- %s%%" % (self.pin, self.concentration)

class DigitizedFormula(models.Model):
    experimental_log = models.ForeignKey('ExperimentalLog',on_delete=models.CASCADE)
    ingredient_id = models.PositiveSmallIntegerField(blank=True,null=True)
    raw_row = models.TextField(blank=True,null=True)

class LocationCode(models.Model):
    location_code = models.CharField(max_length=20)
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = fields.GenericForeignKey('content_type','object_id')

    def __str__(self):
        return "%s" % (self.location_code)

    number_re = re.compile('\d+')

    @staticmethod
    def get_next_location_code(inventory_slot):
        if inventory_slot[:2] == "SL":
            last_slot = LocationCode.objects.filter(location_code__istartswith=inventory_slot).order_by('-location_code')[0]

            last_number = int(LocationCode.number_re.search(last_slot.location_code).group())

            next_number = last_number + 1
            return "%s%s" % (inventory_slot, str(next_number)[1:])

        elif inventory_slot == "":
            return ""
        else:
            return inventory_slot

class MagentoFlavor(models.Model):
    def __str__(self):
        return 'MagentoFlavor: %s' % self.flavor

    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    sku = models.CharField(blank=True, max_length=20)
    description = models.TextField(blank=True)
    price = models.CharField(blank=True, max_length=10)
    short_description = models.TextField(blank=True)

class FlavorSpecification(models.Model):
    flavor = models.ForeignKey('Flavor',on_delete=models.CASCADE)
    name = models.CharField(max_length=48) #change this, override save method to enforce uniqueness
    specification = models.CharField(max_length=48)
    micro = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, blank=True, null=True,on_delete=models.CASCADE)
    replaces = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)



    # def __str__(self):
    #     return 'Flavor: %s, Name: %s, Specification: %s' % (self.flavor, self.name, self.specification)

class ReconciledFlavor(models.Model):
    flavor = models.ForeignKey('Flavor',on_delete=models.CASCADE)
    reconciled = models.BooleanField(default=False)
    scraped_data = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    reconciled_by = models.ForeignKey(User,on_delete=models.CASCADE)

    # def __str__(self):
    #     return 'Flavor: %s, Reconciled By: %s' % (self.flavor, self.reconciled_by.username)




# def accumulate_hazards(flavor):
#
#     hazards_to_accumulate = ['skin_corrosion_hazard', 'eye_damage_hazard',]
#
#     #The KEYS in this dictionary are in the format 'hazard_category' (eg. 'skin_corrosion_hazard_1A')
#     #The VALUES are the accumulation of ingredient weights that correspond to each hazard
#     hazard_dict = {}
#
#     #include the total weight of the flavor in the dict
#     hazard_dict['total_weight'] = 0
#
#     #initialize all the values to zero
#     for hazard in hazards_to_accumulate:
#         for category in Ingredient._meta.get_field(hazard).choices:
#             if category[0] != 'No':     #category[0] and category[1] are always the same
#                 hazard_dict[hazard + '_' + category[0]] = 0
#
#
#     #for each base ingredient in the flavor, find any hazards it has and add its weight to each of those
#     for leaf in flavor.consolidated_leafs.iteritems():
#         ingredient = leaf[0]
#         weight = leaf[1]
#
#         hazard_dict['total_weight'] += weight
#
#         for hazard in hazards_to_accumulate:
#             ingredient_hazard_category = getattr(ingredient, hazard)
#             if ingredient_hazard_category != '':
#                 hazard_dict[hazard + '_' + ingredient_hazard_category] += weight
#
#     return hazard_dict



def replace_ingredient_foreignkeys(new_ingredient):

    for lw in LeafWeight.objects.filter(ingredient__id=new_ingredient.id):
        lw.ingredient = new_ingredient
        lw.save()

    for formula in Formula.objects.filter(ingredient__id=new_ingredient.id):
        formula.ingredient=new_ingredient
        formula.save()

    for ft in FormulaTree.objects.filter(node_ingredient__id=new_ingredient.id):
        ft.node_ingredient=new_ingredient
        ft.save()


# def update_prices_and_get_updated_flavors(old_ingredient=None, new_ingredient=None):
#
#     if new_ingredient == None: #DISCONTINUE ALL was selected
#         pass
#
#     if old_ingredient == None: #all ingredients were previously discontinued
#         old_unitprice = 0
#     else:
#         old_unitprice = old_ingredient.unitprice
#
#
#         for lw in LeafWeight.objects.filter(ingredient=new_ingredient):
#             root_flavor = lw.root_flavor
#             old_total = root_flavor.rawmaterialcost
#
#             new_total = old_total + lw.weight/1000 * (new_ingredient.unitprice - 0)
#             root_flavor.rawmaterialcost = new_total
#             root_flavor.save()
#
#             price_change = '-'
#
#
#     updated_flavors = []
#     for lw in LeafWeight.objects.filter(ingredient=new_ingredient):
#
#         root_flavor = lw.root_flavor
#         old_total = root_flavor.rawmaterialcost
#
#
#         #new_total = old_total - old_unit_price * weight/1000 + new_unit_price * weight/1000
#         new_total = old_total + lw.weight/1000 * (new_ingredient.unitprice - old_ingredient.unitprice)
#         root_flavor.rawmaterialcost = new_total  #overwrite and save the new total rawmaterialcost
#         root_flavor.save()
#
#         price_change = new_total - old_total
#
#
#         updated_flavors.append((root_flavor, lw.weight, old_total, new_total, price_change))
#
#     return updated_flavors



def update_prices_and_get_updated_flavors(old_ingredient, new_ingredient):

    #find all flavors that contain the raw material
    updated_flavors = []
    for lw in LeafWeight.objects.filter(ingredient=new_ingredient):


        root_flavor = lw.root_flavor
        old_total = root_flavor.rawmaterialcost


        #new_total = old_total - old_unit_price * weight/1000 + new_unit_price * weight/1000
        new_total = old_total + lw.weight/1000 * (new_ingredient.unitprice - old_ingredient.unitprice)
        root_flavor.rawmaterialcost = new_total  #overwrite and save the new total rawmaterialcost
        root_flavor.save()

        price_change = new_total - old_total


        updated_flavors.append((root_flavor, lw.weight, old_total, new_total, price_change))

    return updated_flavors


class FlavorCategoryInfo(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    category = models.ForeignKey(HazardCategory,on_delete=models.CASCADE)
    ld50 = models.DecimalField(decimal_places = 3, max_digits = 10, null=True, blank=True)

# FLAVOR label objects

class PrecautionaryStatement(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    code = models.CharField(max_length=40)
    statement = models.TextField()

class HazardStatement(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    statement = models.TextField()

class GHSPictogram(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    pictogram_code = models.CharField(max_length=40)
    pictogram_location = models.CharField(max_length=150)

class GHSSignalWord(models.Model):
    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    signal_word = models.CharField(max_length=40)

#RAW MATERIAL label objects

class RMPrecautionaryStatement(models.Model):
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    code = models.CharField(max_length=40)
    statement = models.TextField()

class RMHazardStatement(models.Model):
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    statement = models.TextField()

class RMPictogram(models.Model):
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    pictogram_code = models.CharField(max_length=40)
    pictogram_location = models.CharField(max_length=150)

class RMSignalWord(models.Model):
    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    signal_word = models.CharField(max_length=40)


class SSI(models.Model):
    #this class represents the data collected from a product spec sheet

    flavor = models.ForeignKey(Flavor, blank=True,null=True,on_delete=models.CASCADE)

    one_off_customer = models.ForeignKey('Customer',blank=True,null=True,on_delete=models.CASCADE)
    # one_off_supplier = models.CharField(max_length=1000, blank=True, null=True)

    #   verified = models.BooleanField(blank=True, default=False)
    #   created_manually = models.BooleanField(blank=True, default=False)
    #   edited_manually = models.BooleanField(blank=True, default=False)
    source_path = models.CharField(max_length=1000, blank=True, null=True) #if data was extracted from spec sheet, file path goes here

    date = models.DateField('Date', blank=True, null=True)
    supercedes = models.CharField(max_length=100, blank=True, null=True)
    product_name = models.CharField(max_length=100, blank=True, null=True)
    product_number = models.CharField(max_length=100, blank=True, null=True)
    specification_code = models.CharField('Specification Code', max_length=100, blank=True, null=True)

    solubility = models.CharField('Solubility', max_length=100, blank=True, null=True)
    specific_gravity = models.CharField('Specific Gravity', max_length=100, blank=True, null=True)
    flash_point = models.CharField('Flash Point', max_length=100, blank=True, null=True)

    sieve = models.CharField('Sieve' ,max_length=100, blank=True, null=True)
    moisture = models.CharField('Moisture', max_length=100, blank=True, null=True)

    fat_content = models.CharField('Fat Content', max_length=100, blank=True, null=True)
    salt_content = models.CharField('Salt Content', max_length=100, blank=True, null=True)
    # special_handling = models.CharField(max_length=100, blank=True, null=True) only for heinz

    brix = models.CharField('Brix', max_length=100, blank=True, null=True)
    bostwick_consistometer = models.CharField('Bostwick Consistometer', max_length=100, blank=True, null=True)
    ph = models.CharField('PH Level', max_length=100, blank=True, null=True)
    water_activity = models.CharField('Water Activity', max_length=100, blank=True, null=True)

    aerobic_plate_count = models.CharField('Aerobic Plate Count' , max_length=100, blank=True, null=True)
    escherichia_coli = models.CharField('Escherichia Coli', max_length=100, blank=True, null=True)
    salmonella = models.CharField('Salmonella', max_length=100, blank=True, null=True)
    yeast = models.CharField('Yeast', max_length=100, blank=True, null=True)
    mold = models.CharField('Mold', max_length=100, blank=True, null=True)
    listeria = models.CharField('Listeria', max_length=100, blank=True, null=True)
    staphylococci = models.CharField('Staphylococci', max_length=100, blank=True, null=True)
    coliforms = models.CharField('Coliforms', max_length=100, blank=True, null=True)

    standard_plate_count = models.CharField('Standard Plate Count', max_length=100, blank=True, null=True)

    description = models.CharField('Description', max_length=1000, blank=True, null=True)
    ingredient_statement = models.CharField('Ingredient Statement', max_length=1000, blank=True, null=True)

    shelf_life = models.CharField('Shelf Life', max_length=1000, blank=True, null=True)
    storage = models.CharField('Storage', max_length=1000, blank=True, null=True)

    class Meta:
        abstract = True

class SpecSheetInfo(SSI):
    pass

# from newqc.models import Lot
# from salesorders.models import LineItem
class COA(SSI):
    lot = models.ForeignKey('newqc.Lot',related_name="lot",on_delete=models.CASCADE)
    line = models.ForeignKey('salesorders.LineItem',on_delete=models.CASCADE)
    origin_lot = models.ForeignKey('newqc.Lot',related_name="origin_lot",blank=True,null=True,on_delete=models.CASCADE)
    sp = models.ForeignKey('SpecSheetInfo',on_delete=models.CASCADE)

    # def save(self, *args, **kwargs):
        # if self.lot.flavor == self.specsheetinfo_ptr.flavor:
            # self.flavor = self.lot.flavor
            # super(COA, self).save(*args, **kwargs)
        # else:
        #     raise ValueError("COA's lot flavor and spec sheet flavor do not match!")


class IngredientStatement(models.Model):

    flavor = models.ForeignKey(Flavor,on_delete=models.CASCADE)
    verified = models.BooleanField(blank=True, default=False)
    edited = models.BooleanField(blank=True, default=False)

    #the field below indicates whether the statement was created through the ingredient
    #statement view rather than being extracted from a spec sheet
    extracted_from_spec_sheet = models.BooleanField(blank=True, default=True)

    ingredient_statement = models.CharField(max_length=1000, blank=True, null=True)

def consolidate_leaf_weight_solutions(lws):
    from solutionfixer.models import Solution

    #create a dictionary with the ingredients as keysp
    #iterate through the list of original leaf weights, adding new keys to the dictionary (values would be total weights)
    #if a solution is found, separate it into its two components and add those to their corresponding keys

    super_consolidated_leaf_weight_dict = collections.defaultdict(int)

    for lw in lws:

        if Solution.objects.filter(ingredient=lw.ingredient).exists():

            #ingredient is a solution, add two fli's for the solute and solvent
            solution = Solution.objects.get(ingredient=lw.ingredient)

            #Can only separate the components if the solution object has a valid solute and solvent ID
            if solution.my_base_id != None and solution.my_solvent_id != None:

                solute_percentage = Decimal('0.01') * solution.percentage
                solute = Ingredient.objects.get(pk=solution.my_base_id)
                solute_weight = lw.weight * solute_percentage

                solvent_percentage = Decimal('0.01') * (Decimal('100') - solution.percentage)
                solvent = Ingredient.objects.get(pk=solution.my_solvent_id)
                solvent_weight = lw.weight * solvent_percentage

                super_consolidated_leaf_weight_dict[solute] += solute_weight
                super_consolidated_leaf_weight_dict[solvent] += solvent_weight

            else:
                super_consolidated_leaf_weight_dict[lw.ingredient] += lw.weight

        else:
            super_consolidated_leaf_weight_dict[lw.ingredient] += lw.weight

    #convert the dictionary into a list
    super_consolidated_leaf_weight_list = list(super_consolidated_leaf_weight_dict.items())

    return super_consolidated_leaf_weight_list

def break_down_solution(solution, weight):

    pass


def test_blah(flavor):
    from hazards.models import HazardAccumulator
    from hazards.hazards import simple_cat_list, EyeDamageHazard
    from hazards.initial_data import HazardClassDict

    mct = EyeDamageHazard.get_mixture_calculation_table()

    cat_list = list(HazardClassDict['EyeDamageHazard'].keys())
    simple_cats = list(simple_cat_list(cat_list))

    fli_list = flavor.get_hazard_formula_list()
    acc = HazardAccumulator(fli_list)

    # import pdb
    # pdb.set_trace()

    for cat in simple_cats:
        for sr in mct:
            if cat in sr.threshold_dict:
                if sr.test(cat, acc):
                    return cat

    return 'No'

def get_accumulator(flavor):
    from hazards.models import HazardAccumulator

    fli_list = flavor.get_hazard_formula_list()
    acc = HazardAccumulator(fli_list)

    return acc

def create_test_flavor_2():

    from hazards.models import IngredientCategoryInfo

    test_flavor = Flavor.objects.create(number = 9999,
                    name = "Test Flavor 2",
                    prefix = "TF",
                    natart = "N/A",
                    spg = 0,
                    risk_assessment_group = 1,
                    kosher = "Not Assigned",
                    yield_field = 100,
                    )

    #import_initial_data()

    ghs_component1 = GHSIngredient.objects.create(
                        cas = '00-00-01')
                        # oral_ld50 = 5000,
                        # tost_single_hazard = '3NE, 3-RI')

    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component1,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                        .get(category='3NE')
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component1,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                        .get(category='3RI')
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component1,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                        .get(category='5'),
        ld50 = 5000
    )


    ghs_component2 = GHSIngredient.objects.create(
                        cas = '00-00-02',)
                        # oral_ld50 = 500,
                        # dermal_ld50 = 1500,
                        # eye_damage_hazard = '1',
                        # skin_corrosion_hazard = '1A',
                        # skin_sensitization_hazard = '1B',
                        # aspiration_hazard = '1',)

    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                        .get(category='4'),
        ld50 = 500
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='SkinCorrosionHazard')\
                        .get(category='1A')
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityDermal')\
                        .get(category='4'),
        ld50 = 1500
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='EyeDamageHazard')\
                        .get(category='1')
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='SkinSensitizationHazard')\
                        .get(category='1B')
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component2,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AspirationHazard')\
                        .get(category='1')
    )



    ghs_component3 = GHSIngredient.objects.create(
                        cas = '00-00-03',)
                        # oral_ld50 = 75,
                        # dermal_ld50 = 1000)

    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component3,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityOral')\
                        .get(category='3'),
        ld50 = 75
    )
    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component3,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AcuteToxicityDermal')\
                        .get(category='3'),
        ld50 = 1000
    )



    ghs_component4 = GHSIngredient.objects.create(
                        cas = '00-00-04',)
                        # tost_single_hazard = '3RI',
                        # aspiration_hazard = '1',)

    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component4,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='TOSTSingleHazard')\
                        .get(category='3RI')
    )

    IngredientCategoryInfo.objects.create(
        ingredient = ghs_component4,
        category = HazardCategory.objects.filter(hazard_class__python_class_name='AspirationHazard')\
                        .get(category='1')
    )


    ing_component1 = Ingredient.objects.create(cas = '00-00-01',
                         product_name = "Test Ingredient 1",
                         unitprice = Decimal('10.00'),
                         sulfites_ppm = 0,
                         package_size = Decimal('0.00'),
                         minimum_quantity = Decimal('0.00')
                         )
    ing_component2 = Ingredient.objects.create(cas = '00-00-02',
                         product_name = "Test Ingredient 2",
                         unitprice = Decimal('10.00'),
                         sulfites_ppm = 0,
                         package_size = Decimal('0.00'),
                         minimum_quantity = Decimal('0.00')
                         )
    ing_component3 = Ingredient.objects.create(cas = '00-00-03',
                         product_name = "Test Ingredient 3",
                         unitprice = Decimal('10.00'),
                         sulfites_ppm = 0,
                         package_size = Decimal('0.00'),
                         minimum_quantity = Decimal('0.00')
                         )
    ing_component4 = Ingredient.objects.create(cas = '00-00-04',
                         product_name = "Test Ingredient 4",
                         unitprice = Decimal('10.00'),
                         sulfites_ppm = 0,
                         package_size = Decimal('0.00'),
                         minimum_quantity = Decimal('0.00')
                         )

    formula1 = Formula.objects.create(flavor = test_flavor,
              ingredient = ing_component1,
              acc_flavor = test_flavor.number,
              acc_ingredient = ing_component1.id,
              amount = 5
              )
    formula2 = Formula.objects.create(flavor = test_flavor,
              ingredient = ing_component2,
              acc_flavor = test_flavor.number,
              acc_ingredient = ing_component2.id,
              amount = 40
              )
    formula3 = Formula.objects.create(flavor = test_flavor,
              ingredient = ing_component3,
              acc_flavor = test_flavor.number,
              acc_ingredient = ing_component3.id,
              amount = 500
              )
    formula4 = Formula.objects.create(flavor = test_flavor,
              ingredient = ing_component4,
              acc_flavor = test_flavor.number,
              acc_ingredient = ing_component4.id,
              amount = 455
              )

    from access.scratch import recalculate_guts
    recalculate_guts(test_flavor)

class KosherGroup(models.Model):
    kosher_group = models.CharField(blank=True, max_length=100)

class IngredientInventoryLog(models.Model):
    '''
    This class keeps track of inventory for raw materials.
        Currently, there are 3 ways inventory for a raw material will change:
        1. Data entered into the RM Inventory Data Entry view (add to inventory)
        2. Creation of a receiving log (add to inventory)
        3. Creation of a batchsheet/lot and then it's corresponding retain
    '''

    ingredient = models.ForeignKey(Ingredient,on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    delta = models.DecimalField(max_digits=10, decimal_places=4)
    comment = models.CharField(max_length=255, blank=True, null=True)

    #The 3 fields below set up the generic foreign key for this object
    #It will point to a batchsheet, a receiving log, or nothing
    content_type = models.ForeignKey(ContentType, null=True, blank=True,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def update_ingredient_inventory(self):
        self.ingredient.recalculate_inventory()
        # self.ingredient.inventory += self.delta
        # self.ingredient.save()

    # #Not sure if I should use this.  It prevents having to call update_ingredient_inventory manually
    # #Whenever an IngredientInventoryLog is saved, it automatically updates the ingredient's inventory
    # #It might be more intuitive to create the log, and then call the update_ingredient_inventory function
    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         #This code is only run when the retain is saved for the first time
    #         self.update_ingredient_inventory()
    #
    #     else:
    #         old_obj = IngredientInventoryLog.objects.get(pk=self.pk)
    #         self.ingredient.inventory += old_obj.delta + self.delta
    #         self.ingredient.save()
    #
    #     super(IngredientInventoryLog, self).save(*args, **kwargs)
def check_weight(): # import any nutri info from a csv file

    invalid_pin_numbers = []
    weight = 0
    count = 0
    ind = 0
    with open('nutri.csv', 'rb') as csvfile, open('nutri(copy).csv', 'rb') as csvcopy, open('rm_not100.csv', 'wb') as csvout: #specify csv file name and path here
        reader = csv.DictReader(csvfile)
        rreader = csv.reader(csvcopy)
        next(rreader, None)
        zipped = list(zip(reader, rreader))
        writer = csv.writer(csvout)

        for row, rrow in zipped:
        #     if ind == 0:
        #         rrow.next()
        #         ind+=1
            weight = Decimal(row['FlavorContent']) + Decimal(row['Carbohydrt']) + Decimal(row['Water']) + Decimal(row['Protein']) + Decimal(row['Total Fat']) + Decimal(row['Ash']) + Decimal(row['AlcoholContent'])
            if weight < 98 or weight > 102:
                count += 1
                writer.writerow((row['PinNum'],row['Shrt_Desc'],row['FlavorContent'],row['Carbohydrt'],row['Water'],row['Protein'],row['Total Fat'],row['Ash'],row['AlcoholContent'],weight))
                print(row['Shrt_Desc'], row['PinNum'], weight)
            # else:
            #     print row['PinNum'], weight

        print(count)


def import_nutri():
    for i in Ingredient.objects.filter(sub_flavor=None):
        if not NutriInfo.objects.filter(ingredient=i).exists():
            ni = NutriInfo(
                ingredient      = i,
                Shrt_Desc       = '%s %s %s' % (i.art_nati, i.prefix, i.product_name),
                Trans_Fat       = Decimal(0),
                Water           = Decimal(0),
                Calories        = Decimal(0),
                Protein         = Decimal(0),
                TotalFat        = Decimal(0),
                Carbohydrt      = Decimal(0),
                Fiber_TD        = Decimal(0),
                Ash             = Decimal(0),
                Calcium         = Decimal(0),
                Phosphorus      = Decimal(0),
                Iron            = Decimal(0),
                Sodium          = Decimal(0),
                Potassium       = Decimal(0),
                Magnesium       = Decimal(0),
                Zinc            = Decimal(0),
                Copper          = Decimal(0),
                Manganese       = Decimal(0),
                Selenium        = Decimal(0),
                Vit_A           = Decimal(0),
                Vit_E           = Decimal(0),
                Thiamin         = Decimal(0),
                Riboflavin      = Decimal(0),
                Niacin          = Decimal(0),
                Panto_acid      = Decimal(0),
                Vit_B6          = Decimal(0),
                Folate          = Decimal(0),
                Vit_B12         = Decimal(0),
                Vit_C           = Decimal(0),
                FA_Sat          = Decimal(0),
                FA_Mono         = Decimal(0),
                FA_Poly         = Decimal(0),
                Cholestrl       = Decimal(0),
                GmWt_1          = Decimal(0),
                GmWt_Desc1      = "N/A",
                GmWt_2          = Decimal(0),
                GmWt_Desc2      = "N/A",
                Refuse_Pct      = Decimal(0),
                WaterAmount     = Decimal(0),
                AlcoholContent  = Decimal(0),
                FlavorContent   = Decimal(100),
                Added_Sugars    = Decimal(0),
                Sugars          = Decimal(0),
                Vit_D           = Decimal(0),
                Sugar_Alcohols  = Decimal(0)
            ) #all 0's
            ni.save()


def import_nutri_from_file(): # import any nutri info from a csv file

    invalid_pin_numbers = []

    with open('nutri.csv') as csvfile: #specify csv file name and path here
        reader = csv.DictReader(csvfile)
        for row in reader:
            for field in row:               # defaults any empty fields to 0
                if row[field] in (None, ""):
                    row[field] = '0'

            try:
                ing = Ingredient.objects.get(id=row['PinNum'],discontinued=False)
                new = NutriInfo(
                    ingredient      = ing,
                    Shrt_Desc       = row['Shrt_Desc'],
                    Trans_Fat       = Decimal(row['Trans_Fat']),
                    Water           = Decimal(row['Water']),
                    Calories        = Decimal(row['Calories']),
                    Protein         = Decimal(row['Protein']),
                    TotalFat        = Decimal(row['Total Fat']),
                    Carbohydrt      = Decimal(row['Carbohydrt']),
                    Fiber_TD        = Decimal(row['Fiber_TD']),
                    Ash             = Decimal(row['Ash']),
                    Calcium         = Decimal(row['Calcium']),
                    Phosphorus      = Decimal(row['Phosphorus']),
                    Iron            = Decimal(row['Iron']),
                    Sodium          = Decimal(row['Sodium']),
                    Potassium       = Decimal(row['Potassium']),
                    Magnesium       = Decimal(row['Magnesium']),
                    Zinc            = Decimal(row['Zinc']),
                    Copper          = Decimal(row['Copper']),
                    Manganese       = Decimal(row['Manganese']),
                    Selenium        = Decimal(row['Selenium']),
                    Vit_A           = Decimal(row['Vit_A']),
                    Vit_E           = Decimal(row['Vit_E']),
                    Thiamin         = Decimal(row['Thiamin']),
                    Riboflavin      = Decimal(row['Riboflavin']),
                    Niacin          = Decimal(row['Niacin']),
                    Panto_acid      = Decimal(row['Panto_acid']),
                    Vit_B6          = Decimal(row['Vit_B6']),
                    Folate          = Decimal(row['Folate']),
                    Vit_B12         = Decimal(row['Vit_B12']),
                    Vit_C           = Decimal(row['Vit_C']),
                    FA_Sat          = Decimal(row['FA_Sat']),
                    FA_Mono         = Decimal(row['FA_Mono']),
                    FA_Poly         = Decimal(row['FA_Poly']),
                    Cholestrl       = Decimal(row['Cholestrl']),
                    GmWt_1          = Decimal(row['GmWt_1']),
                    GmWt_Desc1      = row['GmWt_Desc1'],
                    GmWt_2          = Decimal(row['GmWt_2']),
                    GmWt_Desc2      = row['GmWt_Desc2'],
                    Refuse_Pct      = Decimal(row['Refuse_Pct']),
                    WaterAmount     = Decimal(row['WaterAmount']),
                    AlcoholContent  = Decimal(row['AlcoholContent']),
                    FlavorContent   = Decimal(row['FlavorContent']),
                    Added_Sugars    = Decimal(row['Added_Sugars']),
                    Sugars          = Decimal(row['Sugars']),
                    Vit_D           = Decimal(row['Vitamin D']),
                    Sugar_Alcohols  = Decimal(row['Sugar Alcohols'])

                )
                new.save()
            except:
                invalid_pin_numbers.append(row['PinNum'])

    print(invalid_pin_numbers)

            # print (row['PinNum'], row['Trans_Fat'], row['Shrt_Desc'], row['Water'])


class NutriInfoSuperClass(models.Model):
    ingredient = models.ForeignKey('Ingredient',on_delete=models.CASCADE)
    Shrt_Desc   = models.TextField()
    Trans_Fat   = models.DecimalField('Trans Fat', decimal_places=3,max_digits=11, default=0)
    Water       = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Calories    = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Protein     = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    TotalFat    = models.DecimalField('Other Fat', decimal_places=3,max_digits=11,default=0)
    FA_Sat      = models.DecimalField('Saturated Fat', decimal_places=3,max_digits=11,default=0)
    FA_Mono     = models.DecimalField('Monounsaturated Fat',decimal_places=3,max_digits=11,default=0)
    FA_Poly     = models.DecimalField('Polyunsaturated Fat',decimal_places=3,max_digits=11,default=0)
    Carbohydrt  = models.DecimalField('Carbohydrates', decimal_places=3,max_digits=11,default=0)
    Fiber_TD    = models.DecimalField('Dietary Fiber', decimal_places=3,max_digits=11,default=0)
    Ash         = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Calcium     = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Phosphorus  = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Iron        = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Sodium      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Potassium   = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Magnesium   = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Zinc        = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Copper      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Manganese   = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Selenium    = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Vit_A       = models.DecimalField('Vitamin A', decimal_places=3,max_digits=11,default=0)
    Vit_E       = models.DecimalField('Vitamin E', decimal_places=3,max_digits=11,default=0)
    Thiamin     = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Riboflavin  = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Niacin      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Panto_acid  = models.DecimalField('Pantothenic Acid', decimal_places=3,max_digits=11,default=0)
    Vit_B6      = models.DecimalField('Vitamin B6', decimal_places=3,max_digits=11,default=0)
    Folate      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Vit_B12     = models.DecimalField('Vitamin B12', decimal_places=3,max_digits=11,default=0)
    Vit_C       = models.DecimalField('Vitamin C', decimal_places=3,max_digits=11,default=0)
    Cholestrl   = models.DecimalField('Cholesterol', decimal_places=3,max_digits=11,default=0)
    GmWt_1      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    GmWt_Desc1  = models.TextField()
    GmWt_2      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    GmWt_Desc2  = models.TextField()
    Refuse_Pct  = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    WaterAmount = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    AlcoholContent = models.DecimalField('Alcohol Content' ,decimal_places=3,max_digits=11,default=0)
    ethyl = models.DecimalField('Ethyl Alcohol' ,decimal_places=3,max_digits=11,default=0)
    fusel =    models.DecimalField('Fusel Oil' ,decimal_places=3,max_digits=11,default=0)
    pg = models.DecimalField('Propylene Glycol' ,decimal_places=3,max_digits=11,default=0)
    tri_citrate = models.DecimalField('Triethyl Citrate' ,decimal_places=3,max_digits=11,default=0)
    glycerin = models.DecimalField('Glycerin' ,decimal_places=3,max_digits=11,default=0)
    triacetin = models.DecimalField('Triacetin' ,decimal_places=3,max_digits=11,default=0)

    FlavorContent = models.DecimalField('Flavor Content',decimal_places=3,max_digits=11,default=0)
    Added_Sugars = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Sugars      = models.DecimalField(decimal_places=3,max_digits=11,default=0)
    Vit_D       = models.DecimalField('Vitamin D',decimal_places=3,max_digits=11,default=0)
    Sugar_Alcohols = models.DecimalField(decimal_places=3,max_digits=11,default=0)

    class Meta:
        abstract=True

class NutriInfo(NutriInfoSuperClass):
#     ingredient = models.ForeignKey('Ingredient')
#     Shrt_Desc   = models.TextField()
#     Trans_Fat   = models.DecimalField('Trans Fat', decimal_places=3,max_digits=11)
#     Water       = models.DecimalField(decimal_places=3,max_digits=11)
#     Calories    = models.DecimalField(decimal_places=3,max_digits=11)
#     Protein     = models.DecimalField(decimal_places=3,max_digits=11)
#     TotalFat    = models.DecimalField('Total Fat', decimal_places=3,max_digits=11)
#     FA_Sat      = models.DecimalField('Saturated Fat', decimal_places=3,max_digits=11)
#     FA_Mono     = models.DecimalField('Monounsaturated Fat',decimal_places=3,max_digits=11)
#     FA_Poly     = models.DecimalField('Polyunsaturated Fat',decimal_places=3,max_digits=11)
#     Carbohydrt  = models.DecimalField('Carbohydrates', decimal_places=3,max_digits=11)
#     Fiber_TD    = models.DecimalField('Dietary Fiber', decimal_places=3,max_digits=11)
#     Ash         = models.DecimalField(decimal_places=3,max_digits=11)
#     Calcium     = models.DecimalField(decimal_places=3,max_digits=11)
#     Phosphorus  = models.DecimalField(decimal_places=3,max_digits=11)
#     Iron        = models.DecimalField(decimal_places=3,max_digits=11)
#     Sodium      = models.DecimalField(decimal_places=3,max_digits=11)
#     Potassium   = models.DecimalField(decimal_places=3,max_digits=11)
#     Magnesium   = models.DecimalField(decimal_places=3,max_digits=11)
#     Zinc        = models.DecimalField(decimal_places=3,max_digits=11)
#     Copper      = models.DecimalField(decimal_places=3,max_digits=11)
#     Manganese   = models.DecimalField(decimal_places=3,max_digits=11)
#     Selenium    = models.DecimalField(decimal_places=3,max_digits=11)
#     Vit_A       = models.DecimalField('Vitamin A', decimal_places=3,max_digits=11)
#     Vit_E       = models.DecimalField('Vitamin E', decimal_places=3,max_digits=11)
#     Thiamin     = models.DecimalField(decimal_places=3,max_digits=11)
#     Riboflavin  = models.DecimalField(decimal_places=3,max_digits=11)
#     Niacin      = models.DecimalField(decimal_places=3,max_digits=11)
#     Panto_acid  = models.DecimalField('Pantothenic Acid', decimal_places=3,max_digits=11)
#     Vit_B6      = models.DecimalField('Vitamin B6', decimal_places=3,max_digits=11)
#     Folate      = models.DecimalField(decimal_places=3,max_digits=11)
#     Vit_B12     = models.DecimalField('Vitamin B12', decimal_places=3,max_digits=11)
#     Vit_C       = models.DecimalField('Vitamin C', decimal_places=3,max_digits=11)
#     Cholestrl   = models.DecimalField('Cholesterol', decimal_places=3,max_digits=11)
#     GmWt_1      = models.DecimalField(decimal_places=3,max_digits=11)
#     GmWt_Desc1  = models.TextField()
#     GmWt_2      = models.DecimalField(decimal_places=3,max_digits=11)
#     GmWt_Desc2  = models.TextField()
#     Refuse_Pct  = models.DecimalField(decimal_places=3,max_digits=11)
#     WaterAmount = models.DecimalField(decimal_places=3,max_digits=11)
#     AlcoholContent = models.DecimalField('Alcohol Content' ,decimal_places=3,max_digits=11)
#     FlavorContent = models.DecimalField('Flavor Content',decimal_places=3,max_digits=11)
#     Added_Sugars = models.DecimalField(decimal_places=3,max_digits=11)
#     Sugars      = models.DecimalField(decimal_places=3,max_digits=11)
#     Vit_D       = models.DecimalField('Vitamin D',decimal_places=3,max_digits=11)
#     Sugar_Alcohols = models.DecimalField(decimal_places=3,max_digits=11)

    @property
    def total(self):
        return (
                    self.Water + self.Protein + self.Carbohydrt + self.Sugars + self.Fiber_TD + self.TotalFat + self.FA_Sat + self.FA_Poly + self.FA_Mono
                    + self.Ash + self.FlavorContent + self.ethyl + self.fusel + self.pg + self.tri_citrate + self.glycerin + self.triacetin
                )

    @property
    def invalid_total(self):
        if self.total < 98 or self.total > 102:
            return True
        else:
            return False

def scrape_renumbers():
    count = 0
    fl = Flavor.objects.all()
    for f in fl:
        i = Formula.objects.filter(flavor = f)
        if len(i) == 1 and i[0].ingredient.sub_flavor and i[0].amount == 1000:
            count+=1
            print((i[0]))
    return count

# def create_directory(url):
#     folders = ['/specsheet', '/SDS', '/nutri', '/GMO', '/LOG', '/natural', '/origin', '/vegan', '/organic', '/kosher', '/halal', '/COA', '/COI']
#     for f in folders:
#         os.mkdir(url+f)

def set_file_path(instance, filename):
    # if not os.path.splitext(filename)[1] == 'pdf':
    #     filename = os.path.splitext(filename)[0]+'.pdf'
    if not instance.rawmaterial:
        finalurl = 'Temp/{0}'.format(filename)

    else:
        finalurl = 'RawMaterials/{0}/{1}/{2}/{3}'.format(str(instance.rawmaterial.id), str(instance.rawmaterial.rawmaterialcode), instance.doctype, filename)

    return finalurl

def test_upload():
    from django.core.files import File
    i = Ingredient.objects.get(rawmaterialcode = 670)
    f = open('test.txt')
    f = File(f)
    d = Documents(rawmaterial=i,doctype='GMO',uploadfile=f)
    return d

DOC_TYPES = (
    ('specsheet', 'Spec Sheet'),
    ('sds','SDS'),
    ('allergen', 'Allergen'),
    ('nutri', 'Nutri'),
    ('GMO', 'GMO'),
    ('GPVC', 'GMO Project Verified Certificate'),
    ('LOG', 'Letter Of Guarantee'),
    ('natural', 'Natural'),
    ('origin', 'Origin'),
    ('vegan', 'Vegan'),
    ('organic', 'Organic Compliance'),
    ('organic_cert', 'Organic Certified'),
    ('kosher', 'Kosher'),
    ('halal', 'Halal'),
    ('COA', 'Certificate of Analysis'),
    ('COI', 'Certificate of Insurance'),
    ('ingbreak', 'Ingredient Breakdown'),
    ('form20', 'Form #020'),
    ('form20ar', 'Form #020 Audit Report'),
    ('form20c', 'Form #020 Certification'),
    ('form40', 'Form #040'),
)

class Documents(models.Model):

    rawmaterial = models.ForeignKey('Ingredient', blank=True, null=True, default=None,on_delete=models.CASCADE)
    doctype = models.CharField(choices=DOC_TYPES, max_length=30, default="")
    uploadfile = models.FileField(upload_to=set_file_path, unique=False)
    uploader = models.ForeignKey(User, blank=True, null=True,on_delete=models.CASCADE)
    expiration = models.DateField(blank=True, null=True, default=date.today)
    documententry = models.DateField(default=date.today)


    log_rms  = ArrayField(
        models.CharField(max_length=25, null=True, blank=True, default=""),
        blank=True,
        null=True,
        default=[]
    )


    def save(self, *args, **kwargs):
        if not DocumentVerification.objects.filter(document = self, final=True).exists():
            self.log_rms = [str(self.rawmaterial.rawmaterialcode)]
        return super(Documents, self).save(*args, **kwargs)

    def rm_code(self):
        return [str(self.rawmaterial.rawmaterialcode)]

    @property
    def verified(self):
        dv = DocumentVerification.objects.filter(document = self, final=True)
        if len(dv) > 0:
                return True
        else:
            return False

    @property
    def days_until_expiration(self):
        if self.expiration:
            delta = self.expiration - date.today()
            return delta.days
        return None

    @property
    def dv_count(self):
        return DocumentVerification.objects.filter(document = self).count()

    @property
    def get_verifiers(self):
        dv = DocumentVerification.objects.filter(document = self)
        d = []
        for i in dv:
            d.append(i.verifier.username)
        return d

    @property
    def get_rmretain(self):
        dv = DocumentVerification.objects.filter(document=self, final=True)[0]
        return dv.rm_retain

    @property
    def filename(self):
        return os.path.basename(self.uploadfile.name)

    # def __init__(self)

class DocumentVerification(models.Model):
    document = models.ForeignKey("Documents", related_name='verifications',on_delete=models.CASCADE)
    verifier = models.ForeignKey(User, blank=False, null=False,on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    temp_ingredient = models.ForeignKey('IngredientTemp', default=None, blank=True, null=True,on_delete=models.CASCADE)
    temp_nutri = models.ForeignKey("NutriInfoTemp", default=None, blank=True, null=True,on_delete=models.CASCADE)
    final = models.BooleanField(default=False)
    rm_retain = models.ForeignKey("newqc.RMRetain", default=None, blank=True, null=True,on_delete=models.CASCADE)

    # expiration refers to eitherthe document date(True) or the expiration(False) of the document, depending on is_documentdate
    expiration = models.DateField(blank=False, null=True, default=None)
    is_documentdate = models.BooleanField(default=True)

    @property
    def days_until_expiration(self):
        if self.expiration:
            delta = self.expiration - date.today()
            return delta.days
        return None

    class Meta:
        permissions = (
            ('can_verify', "Authorized to verify documents"),
        )



class IngredientTemp(IngredientSuperClass):
    user = models.ForeignKey(User, blank=True, null=True,on_delete=models.CASCADE)
    temp_rmcode = models.PositiveIntegerField(blank=True, null=True, )
    # salmonella = models.NullBooleanField(default=False)

    log_rms  = ArrayField(
        models.CharField(max_length=25, null=True, blank=True, default=""),
        blank=True,
        null=True,
        default=[]
    )

    class Meta:
        unique_together = ('user', 'temp_rmcode')


    @property
    def list_log_rms(self):
        options = ""
        for l in self.log_rms:
            options += "<li>"+ str(Ingredient.objects.get(rawmaterialcode = int(l))) + "</li>"

        if not options:
            return "<li>Document considered supplier specific</li>"

        return options
    @property
    def supplier_spec(self):
        if self.log_rms:
            return "Product Specific"
        return "Supplier Specific"
    # verified = models.DateField(default=date.today)
    # docverification = models.ForeignKey('DocumentVerification', blank=False, null=False)

class NutriInfoTemp(NutriInfoSuperClass):
    user = models.ForeignKey(User, blank=True,on_delete=models.CASCADE)
    # temp_ing = models.ForeignKey('IngredientTemp')
    class Meta:
        unique_together = ('user', 'ingredient')
    # docverification = models.ForeignKey('DocumentVerification', blank=False, null=False)


def remove_duplicates():
    pins = Ingredient.objects.order_by('id').values_list('id', flat=True).distinct()
    for p in pins:
        i = Ingredient.objects.filter(id=p)
        if i.count() == 2 and i[0].suppliercode == i[1].suppliercode:
            print(str(i[0].id) + " " + str(i[0].rawmaterialcode) + " " + str(i[1].rawmaterialcode))
            i.filter(discontinued = True)
            i.delete()


def fix_suppliers(): # fix supplier codes
    delete = []
    blank = []
    with open('suppliers.csv') as csvfile: #specify csv file name and path here
        reader = csv.DictReader(csvfile)

        for row in reader:
        #     # print row['Delete']
        #     if row['Delete']:
        #         print row['Delete']
        #     else:
        #         print "none"
        #     # newcode = 'N/A'
            # if row['New Code']:
            #     newcode = row['New Code']

            # elif Ingredient.objects.filter(suppliercode=row['Ingredient Supplier Code']).exists():
            #     ex = Ingredient.objects.filter(suppliercode=row['Ingredient Supplier Code'])
                # print row['Ingredient Supplier Code'] +" "+ str(ex[0].id)

            i = Ingredient.objects.filter(suppliercode = row['Ingredient Supplier Code'])

            #

                # print row['Ingredient Supplier Code'] +" " + row['New Code'] + " " +row['Delete']
                # if 1 == 1:
            for ing in i:
                if row['Delete'] and Ingredient.objects.filter(id=ing.id).count()>1:

                    # print 'D ' + row['Delete']
                    # print row['Ingredient Supplier Code']
                    # print Ingredient.objects.filter(id=ing.id)
                    # ing.delete()
                    delete.append(ing)
                    ing.delete()
                elif not row['New Code']:
                    blank.append(ing)

            i.update(suppliercode = row['New Code'])
            for ing in i:
                ing.save()

        print(delete)
        print(blank)
        # for d in delete:
        #     print d
        #
        # for b in blank:
        #     print b

class Training(models.Model):
        TEST_TYPES = (
            ('gbpp', 'Glass and Brittle Plastic Policy'),#sign
            ('wiki', 'Wiki Review'),
            # ('foodsafety', 'Food Safety Handbook Test'),
            ('hazcom', 'Hazcom 2012 SDS Training'),
            ('handbook', 'Employee Handbook Confirmation'),#sign
            ('colorblind', 'Color Blind Test'),
            ('fooddefense', 'Food Defense Plan Training'),
            ('facemask', 'Face Mask Fit Test'),#admin
            ('sensory', 'Sensory Evaluation Training'),#admin
            ('ccp', 'CCP and Allergen HACCP Questionaire'),
            ('osha', 'OSHA Lockout Tagout'),#sign
            ('firedrill', 'Fire Drill'),#admin
            ('fltv', 'Forklift Training Video'),
            ('fltdt', 'Forklift Drivers Test'),#admin
            ('wpsafety', 'Workplace Safety'),


            ('bacteria', 'Bacteria Review'),
            ('foodborne', 'Foodborne Illness Review', ),
            ('personalhygiene', 'Personal Hygiene Review' ),
            ('haccp', 'HACCP Review'),
            ('sanitation', 'Sanitation Review'),
            ('time', 'Time and Temperature Controls Review'),
            ('foreign', 'Foreign Material Detection Review'),
            ('cross', 'Cross Contamination Review'),
            ('allergens', 'Allergens Review'),
            ('pest', 'Pest Control Review'),
            ('security', 'Security Review')

        )

        test_type = models.CharField(choices=TEST_TYPES, max_length=30, default="")
        tester = models.ForeignKey(User, blank=True, null=True,on_delete=models.CASCADE)
        completion_date = models.DateField(blank=True, null=True, default=date.today)
        complete = models.BooleanField(default=False, blank=False, null=False)
        passed = models.BooleanField(default=False, blank=False, null=False)

        # source_materials = ArrayField(
        #     models.CharField(max_length=100, blank=True),
        #     default = []
        # )

        # answers = models.ArrayField(
        #     models.CharField(blank=True),
        # )
        @property
        def questions(self):
            return Question.objects.filter(training=self)

        @property
        def test_renewal(self):
            once = ['facemask', 'ccp', 'osha']
            two = ['wpsafety', 'hazcom','bacteria', 'foodborne', 'personalhygiene', 'haccp', 'sanitation', 'time', 'foreign', 'cross', 'allergens', 'pest', 'security', 'firedrill', 'gbpp', 'wiki', 'fooddefense']
            # three = ['ccp']
            # five = ['sensory']

            if not self.test_type in one + two + three + five:
                return False
            elif self.test_type in two:
                return (date.today() - date(self.completion_date.year+2, self.completion_date.month, self.completion_date.day)).days
            elif self.test_type in one:
                return (date.today() - date(self.completion_date.year+1, self.completion_date.month, self.completion_date.day)).days
            # elif self.test_type in five:
            #     return (date.today() - date(self.completion_date.year+5, self.completion_date.month, self.completion_date.day)).days


            # class Training_Test(models.Model):
#     test_type = models.CharField(blank=False, null=False)
#     # questions = models.ForeignKey('Trainging_Question', blank = False, null=False)
#     complete = models.BooleanField(default=False, blank=False, null=False)


# class Training_Question(models.Model):
#     test = models.ForeignKey('Training', blank = False, null = False)
#     question = models.CharField(max_length = 300)
#     answers = models.ArrayField(
#         models.CharField(blank=True),
#     )
class Question(models.Model):
        question = models.CharField(max_length=500,default="")
        answer = models.CharField(max_length=2000,default="")
        training = models.ForeignKey('Training', blank=False, null=False,on_delete=models.CASCADE)
        # any images or documents that are associated with question
        # source_material = models.CharField(max_length=100, default = "")
