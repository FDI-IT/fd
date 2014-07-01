# -*- coding: utf-8 -*-
from decimal import Decimal
from datetime import datetime, timedelta, date
import re
import Queue
import os
from operator import itemgetter

from django.db import models
from django.db.models import Q, F
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


from hazard_calculator.models import FormulaLineItem, HazardAccumulator, GHSIngredient
from hazard_calculator.tasks import create_subhazard_dict
#from access.controller import hazard_list, acute_toxicity_list
#from access.controller import make_hazard_class, skin_hazard_dict, eye_hazard_dict, respiratory_hazard_dict, germ_mutagenicity_dict


from pluggable.sets import AncestorSet

one_hundred = Decimal('100')
hundredths = Decimal('0.00')
zero = Decimal('0')
one_thousand = Decimal('1000')
NATART_CHOICES = (
    ('N/A','N/A'),
    ('Nat','Nat'),
    ('Art','Art'),
    ('NFI','NFI'),
    ('NI','NI'),
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
}

SOLUBILITY_CHOICES = (
   ('Oil','Oil'),
   ('Water','Water'),
   ('Other - see memo','Other - see memo'),
)

KOSHER_CHOICES = (
    ('Not assigned','Not assigned'),
    ('Not kosher','Not kosher'),
    ('Pareve','Pareve'),
    ('Dairy','Dairy'),
    ('Meat','Meat'),
    ('Passover','Passover'),
    ('Rabbi Present','Rabbi Present'),
)

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

DIACETYL_PKS = [262,]
PG_PKS = [670,6717]

def get_next_flavorid():
    return Flavor.objects.all().order_by('-id')[0].id+1

def get_next_rawmaterialcode():
    try:
        return Ingredient.objects.all().order_by('-rawmaterialcode')[0].rawmaterialcode+1
    except:
        return 1
    
def get_next_experimentalnum():
    try:
        return ExperimentalLog.objects.all().order_by('-experimentalnum')[0].experimentalnum+1
    except:
        return 1

class FormulaTree(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="formula_rows", db_index=True)
    lft = models.PositiveSmallIntegerField()
    rgt = models.PositiveSmallIntegerField()
    formula_row = models.ForeignKey('Formula', null=True, blank=True)
    node_ingredient = models.ForeignKey('Ingredient', null=True, blank=True, db_index=True)
    node_flavor = models.ForeignKey('Flavor', null=True, blank=True)
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

    def __unicode__(self):
        return "%s: l%s r%s parent%s" % (self.root_flavor.__unicode__(), self.lft, self.rgt, self.parent_id)
        
class LeafWeight(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="leaf_weights", db_index=True)
    ingredient = models.ForeignKey('Ingredient', db_index=True)
    weight = models.DecimalField(decimal_places=3, max_digits=7)
    quant_weight = models.IntegerField(null=True)
    
class IndivisibleLeafWeight(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="indivisible_leaf_weights", db_index=True)
    ingredient = models.ForeignKey('Ingredient', db_index=True)
    weight = models.DecimalField(decimal_places=3, max_digits=7)
    quant_weight = models.IntegerField(null=True)
    
    def __unicode__(self):
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
    
    flavor = models.ForeignKey('Flavor')
    ingredient = models.ForeignKey('Ingredient')
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
        db_table = u'access_integratedformula'
        ordering = ['acc_flavor',]

    def __unicode__(self):
        return "%s-%s: %s %s lbs" % (self.flavor.prefix, self.flavor.number, self.ingredient.__unicode__(), self.amount)
    
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
                    print "Updating %s" % g
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




class Ingredient(models.Model):
    """Raw materials for use in production.
    
    The unique indentifier for this table is 'rawmaterialcode'.
    Multiple unique 'rawmaterialcode' fields can exist with the same
    productid; this represents equivalent raw materials from alternate
    suppliers.
    """

    id = models.PositiveIntegerField("PIN", 
                                      db_column='ProductID',
                                      default=get_next_rawmaterialcode)
    cas = models.CharField( 
            max_length=15,
            blank=True)
    rawmaterialcode = models.PositiveIntegerField(
            primary_key=True,
            db_column='RawMaterialCode',
            blank=True,
            default=get_next_rawmaterialcode)
    art_nati = models.CharField(
            max_length=3,
            db_column='ART_NATI',
            choices=NATART_CHOICES)
    prefix = models.CharField(
            max_length=60,
            db_column='PREFIX',
            blank=True)
    product_name = models.CharField(
            max_length=60,
            db_column='ProductName')
    part_name2 = models.CharField(
            max_length=60,
            db_column='PART_NAME2',
            blank=True)
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
            related_name="gazinta")
    discontinued = models.BooleanField(
            db_column='Discontinued',
            blank=True)
    experimental = models.BooleanField(blank=True) #AKDJFLKJADLFDAFLADFAFKDADFDAfkj
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
    fldr = models.CharField(
            max_length=50,
            db_column='FLDR',
            blank=True)
    kosher = models.CharField(
            max_length=20,
            db_column='KOSHER',
            blank=True)
    kosher_code = models.CharField(
            max_length=50,
            db_column='Kosher Code',
            blank=True)
    lastkoshdt = models.DateTimeField(
            db_column='LASTKOSHDT',
            blank=True,
            default=datetime(1990,1,1))
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
            max_length=15,
            db_column='FEMA',
            blank=True)
    gmo = models.CharField(
            max_length=50,
            db_column='GMO',
            blank=True)
    natural_document_on_file = models.BooleanField(
            db_column='Natural_Document_On_File',
            blank=True)
    allergen = models.CharField(
            max_length=50,
            db_column='Allergen',
            blank=True)
    sprayed = models.BooleanField(
            db_column='Sprayed',
            blank=True)
    microsensitive = models.CharField(
            max_length=20,
            db_column='Microsensitive',
            blank=True)
    prop65 = models.BooleanField(
            db_column='Prop65',
            blank=True)
    nutri = models.BooleanField(
            db_column='Nutri',
            blank=True)
    transfat = models.BooleanField(
            db_column='TransFat',
            blank=True)
    sulfites = models.BooleanField(blank=True)
    sulfites_ppm = models.PositiveSmallIntegerField()
    
    eggs = models.BooleanField(blank=True)
    fish = models.BooleanField(blank=True)
    milk = models.BooleanField(blank=True)
    peanuts = models.BooleanField(blank=True)
    soybeans = models.BooleanField(blank=True)
    treenuts = models.BooleanField(blank=True)
    wheat = models.BooleanField(blank=True)
    
    sunflower = models.BooleanField(blank=True)
    sesame = models.BooleanField(blank=True)
    mollusks = models.BooleanField(blank=True)
    mustard = models.BooleanField(blank=True)
    celery = models.BooleanField(blank=True)
    lupines = models.BooleanField(blank=True)
    yellow_5 = models.BooleanField(blank=True)
    crustacean = models.BooleanField(blank=True)
    has_allergen_text = models.BooleanField(blank=True)
    
    hazardous = models.BooleanField(blank=True)
    
    package_size = models.DecimalField("Package size (lbs)", max_digits=7,decimal_places=2)
    minimum_quantity = models.DecimalField("Minimum quantity (lbs)", max_digits=7,decimal_places=2)
    quantity_discount = models.CharField(max_length=50, blank=True)
    fob_point = models.CharField("FOB point", max_length=50)
    lead_time = models.CharField(db_column='lead_time',max_length=50)
    solubility = models.CharField(max_length=50,
                                  choices=SOLUBILITY_CHOICES,
                                  blank=True)
    solubility_memo = models.CharField(max_length=50,blank=True)
    supplier_catalog_number = models.CharField(max_length=50,blank=True)
    
   
    
    # these values have something to do with inventory, or solutions, or gazintas?
    inventoryng = models.BooleanField(db_column='InventoryNG', blank=True)
    kencheck = models.BooleanField(db_column='Kencheck', blank=True)    
    # these values were to be part of an inventory system that was never done
    unitsinstock = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsInStock', blank=True, default=0)
    committed = models.DecimalField(decimal_places=2, max_digits=6, db_column='COMMITTED', blank=True, default=0)
    reorderlevel = models.DecimalField(decimal_places=2, max_digits=6, db_column='ReorderLevel', blank=True, default=0)
    old_lead_time = models.DecimalField(decimal_places=2, max_digits=6, db_column='LEAD_TIME', blank=True, default=0, null=True)
    unitsonorder = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsOnOrder', blank=True, default=0)
    # simply not used
    supplierid = models.PositiveIntegerField(db_column='SupplierID',  blank=True, default=0)
    
    aller_attrs = [
        'crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
    ]
    
    #ing
    location_code_n = generic.GenericRelation('LocationCode')    

    
    @staticmethod
    def anonymize():
        supplier_code_queue = Queue.Queue()
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
            print rm
    
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
        if self.discontinued == False:
            return "/access/ingredient/pin_review/%s/" % self.id
        else:
            return "/access/ingredient/%s/" % self.rawmaterialcode

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
            return u"%s %s" % (self.prefix, self.product_name)
        else:
            return self.product_name
        
    @property
    def short_prefixed_name(self):
        if len(self.prefixed_name) > 18:
            if self.prefix != "":
                s = u"%s %s" % (self.prefix, self.product_name)
                return u"%s..." % s[:18]
            else:
                return "%s..." % self.product_name[:18]
        else:
            return self.prefixed_name
        
    @property
    def short_remainder_name(self):
        if len(self.prefixed_name) > 18:
            return u"...%s %s" % (self.prefixed_name[18:], self.part_name2)
        else:
            return self.part_name2

    @property
    def supplier_list(self):
        for i in Ingredient.objects.filter(id=self.id):
            yield i.suppliercode
            
    @property
    def long_name(self):
        if self.sub_flavor:
            my_name = "%s %s %s" % (self.art_nati, self.sub_flavor.table_name, self.sub_flavor.label_type)
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
            return Ingredient.objects.get(flavornum=number)
        else:
            return Ingredient.objects.filter(id=number).order_by('discontinued')[0]
    
    @transaction.commit_manually
    def update_price(self, new_price, update_time=None):
        if update_time == None:
            update_time = datetime.now()
        try:
            dec_new_price = Decimal(new_price)
        except:
            dec_new_price = Decimal(str(new_price))
        delta = (dec_new_price - self.unitprice) / 1000
        if self.unitprice == dec_new_price:
            self.purchase_price_update = update_time
            self.save()
            transaction.commit()
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
            
        transaction.commit()
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

    def resembles(self, ingredient):
        if self.id != ingredient.id:
            return "id"
        if unicode(self.product_name) != unicode(ingredient.product_name):
            return "product_name"
        if unicode(self.part_name2) != unicode(ingredient.part_name2):
            return "part_name2"
        if unicode(self.description) != unicode(ingredient.description):
            return "description"
        if self.discontinued != ingredient.discontinued:
            return "discontinued"
        if unicode(self.prefix) != unicode(ingredient.prefix):
            return "prefix"
        if self.flavornum != ingredient.flavornum:
            return "flavornum"
        if self.solution != ingredient.solution:
            return "solution"
        if unicode(self.solvent) != unicode(ingredient.solvent):
            return "solvent"
        if unicode(self.suppliercode) != unicode(ingredient.suppliercode):
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
    
    class Meta:
        ordering = ['id']
        permissions = (
                ("changeprice_ingredient","Can change the price of raw materials"),
                ('view_ingredient',"Can view ingredients")
        )
        db_table = u'Raw Materials'
        
    def save(self, *args, **kwargs):
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
        
    def __unicode__(self):
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
        csl = [retains[0],] # combed sorted list
        for x in range(1,len(retains)):
            if retains[x].similar_to(retains[x-1]):
                pass
            else:
                csl.append(retains[x])
            
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
    
    crustacean = models.BooleanField(default=False)
    eggs = models.BooleanField(default=False)
    fish = models.BooleanField(default=False)
    milk = models.BooleanField(default=False)
    peanuts = models.BooleanField(default=False)
    soybeans = models.BooleanField(default=False)
    treenuts = models.BooleanField(default=False)
    wheat = models.BooleanField(default=False)
    sunflower = models.BooleanField(blank=True)
    sesame = models.BooleanField(blank=True)
    mollusks = models.BooleanField(blank=True)
    mustard = models.BooleanField(blank=True)
    celery = models.BooleanField(blank=True)
    lupines = models.BooleanField(blank=True)
    yellow_5 = models.BooleanField(blank=True)
    
    organic = models.BooleanField(default=False)
    diacetyl = models.BooleanField("No Diacetyl", default=True)
    indivisible = models.BooleanField(blank=True)
    
    no_pg = models.BooleanField("No PG", 
        blank=True,
        default=False)
    spraydried = models.BooleanField("Spray Dried",
        blank=True,
        default=False)
    
    flashpoint = models.PositiveIntegerField("Flash Point", default=0)
    solubility = models.CharField(max_length=25,blank=True, default="")
    stability = models.CharField(max_length=25, blank=True, default="")
    allergen = models.CharField("Allergens", max_length=50, blank=True, default="")
    yield_field = models.PositiveIntegerField("Percent Yield", default=100) # Field renamed because it was a Python reserved word.lc
    
    reactionextraction = models.BooleanField("Reaction/Extraction",default=False)
    prop_65 = models.CharField("Prop 65", max_length=50,blank=True, default="") # Field renamed to remove spaces.lc
    gmo = models.CharField("GMO", max_length=50, blank=True, default="")
    prop65 = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class Flavor(FormulaInfo):
    
    #retains = generic.GenericRelation(Retain)
    id = models.PositiveIntegerField(
            primary_key=True,
            default=get_next_flavorid)
    number = models.PositiveIntegerField(
            unique=True)
    # fk to ingredient, one to many
    ingredients = models.ManyToManyField(
            Ingredient,
            through='Formula')
    name = models.CharField(
            max_length=80,)
    prefix = models.CharField(
            max_length=2,)
    code = models.CharField(
            max_length=3,
            blank=True)
    natart = models.CharField(
            max_length=3,
            blank=True,
            choices=NATART_CHOICES)
    label_type = models.CharField(
            max_length=50,
            blank=True,
            db_column="type")
    unitprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            blank=True,
            null=True)
    productmemo = models.TextField(
            blank=True)
    mixing_instructions = models.TextField(blank=True)
    color = models.CharField(max_length=50,blank=True)
    organoleptics = models.CharField(max_length=50,blank=True)
    pricing_memo = models.TextField(blank=True)
    spg = models.DecimalField(decimal_places=3,max_digits=4,default=0)
    
    entered = models.DateTimeField(auto_now_add=True)
    supportive_potential = models.BooleanField(blank=True)
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
    kosher_id = models.CharField("Kosher ID", max_length=15, default="", blank=True)

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
    batfno = models.CharField("BATFNO", max_length=50,blank=True, default="")
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
    location_code_n = generic.GenericRelation('LocationCode')
    location_code_old = models.CharField(blank=True, default="",max_length=20)
    
    #textfields for spec sheet info
    ingredient_statement = models.TextField(blank=True)
    shelf_life = models.TextField(blank=True)
    shipping_storage = models.TextField(blank=True)
    
    
    
    def save(self, *args, **kwargs):
        try:
            self.prefix = self.prefix.upper()
        except:
            pass
        
        super(Flavor, self).save(*args, **kwargs)
        
        if not self.flavorspecification_set.filter(name='Specific Gravity').exists():
            flavorspec = FlavorSpecification(
                                             flavor = self,
                                             name = 'Specific Gravity',
                                             specification = 'SPG Spec',
                                             )
            flavorspec.save()      
            
        if self.flashpoint != 0: #no flashpoint or powder
            if not self.flavorspecification_set.filter(name='Flash Point').exists():
                flavorspec = FlavorSpecification(
                                                 flavor = self,
                                                 name = 'Flash Point',
                                                 specification = 'Flashpoint Spec',
                                                 )
                flavorspec.save()


        
  
        
    def gazintas(self,):
        for ft in FormulaTree.objects.filter(root_flavor=self)[1:]:
            if ft.node_flavor is not None:
                yield ft.node_flavor
    
    class Meta:
        db_table = u'access_integratedproduct'
        ordering = ['-valid','number']
        permissions = (
                ('view_flavor',"Can view flavors"),
        )
    import_order = 0

    
    @property
    def location_code(self):
        try:
            return self.location_code_n.all().reverse()[0]
        except:
            return None
#    
#    @property
#    def organoleptics(self):
#        try:
#            return self.experimental_log.all()[0].organoleptics
#        except:
#            return ""
#        
#    @property
#    
#    
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
                dci.append(lw.ingredient.__unicode__())
        return dci
    
    def quick_validate(self, descend=True):
        sum = 0
        for fr in self.formula_set.all():
            sum+= fr.amount
        if sum != 1000:
            return u"%s-%s formula does not add up to 1000 parts." % (self.prefix, self.number) 
        
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
        return "%s %s" % (self.name, self.label_type)
    
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

    def __unicode__(self):
        return u"%s-%s %s %s %s" % (self.prefix,
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
            elif key == 'application':
                keyword = 'application__application_type__id__in'
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
            else:
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(bool(my_arg))
                string_kwargs[keyword] = arg_list
        return string_kwargs
    
    def get_related_links(self):
        related_links = [
                       ('#flat_review_table','Formula'),
                       ('/access/ajax_dispatch/?tn=consolidated&pk=%s' % self.pk,'Consolidated'),
                       ('/access/ajax_dispatch/?tn=consolidated_indivisible&pk=%s' % self.pk, 'Consolidated-Indivisible'),
                       ('/access/ajax_dispatch/?tn=explosion&pk=%s' % self.pk,'Explosion'),
                       ('/access/ajax_dispatch/?tn=legacy_explosion&pk=%s' % self.pk,'Legacy Explosion'),
                       ('/access/ajax_dispatch/?tn=revision_history&pk=%s' % self.pk, 'Revision History'),
                       ('/access/ajax_dispatch/?tn=spec_sheet&pk=%s' % self.pk, 'Spec Sheet'),
                       ('/access/ajax_dispatch/?tn=customer_info&pk=%s' % self.pk, 'Customer Info')
                       ]
        if self.retain_superset().count()>0:
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
        aller_attrs = [
                'crustacean',
                'eggs',
                'fish',
                'milk',
                'peanuts',
                'soybeans',
                'treenuts',
                'wheat',
                'sunflower',
                'sesame',
                'mollusks',
                'mustard',
                'celery',
                'lupines',
                'yellow_5',
                'sulfites',
            ]
        for aller in aller_attrs:
            val = getattr(self,aller)
            if val == True:
                return_list.append(aller)
        return return_list
        
    @property
    def renumber_list(self):
        return Renumber.objects.filter(a=self).values_list('b',flat=True)
    
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
            print f
            f.name = "%s %s" % (lorem_one, lorem_two)
            f.label_type = "Flavor"
            f.productmemo = "%s %s %s %s" % (lorem_one, lorem_two, lorem_three, lorem_four)
            f.prefix = "FL"
            f.save()
            
            q.put(lorem_one)
            q.put(lorem_two)
            q.put(lorem_three)
            q.put(lorem_four)
            
            print f
            
    
#     def get_max_depth(self):
#         return max(for ftnode.depth in FormulaTree.objects.filter(root_flavor=self))
    
    
#     #returns the depth of a formula tree node (recursively)        
#     def get_depth(self, ftnode):
#         #base case: node is root node, depth = 0
#         if(ftnode.row_id == 0):
#             return 0
#         else:
#             parent_node = FormulaTree.objects.get(root_flavor=self, row_id=ftnode.parent_id)
#             return 1 + self.get_depth(parent_node)
#     
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
        cons_leafs = sorted(self.consolidated_leafs.iteritems(), key=itemgetter(1), reverse=True)
        cons_formulae = []
        for ingredient, amount in cons_leafs:
            cons_formulae.append(Formula(ingredient=ingredient,amount=amount))
        return cons_formulae
    
    @property
    def sorted_consolidated_indivisible_leafs(self):
        cil=sorted(self.consolidated_indivisible_leafs.iteritems(), key=itemgetter(1), reverse=True)
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
            
        return unique_ingredients.keys()
    
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
        print "TEST"   
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
                    print '"%s","%s","%s","%s"' % (ingredient.ingredient.id, ingredient.ingredient.product_name, ingredient.amount, cost_diff)
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
                    Q(productmemo__icontains=term) |
                    Q(keywords__icontains=term)
                )  
            else:
                results = results & Flavor.objects.filter( 
                    Q(name__icontains=term) |
                    Q(productmemo__icontains=term) |
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



    def get_hazards(self):
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
        
        
        no_cas_total = 0
        
        for ingredient, weight in self.consolidated_leafs.iteritems():
            
            #case 1
            if ingredient.cas == '':
                no_cas_total = no_cas_total + weight
            
            else:
                #case 2: the cas number is not in the imported ingredients
                if not GHSIngredient.objects.filter(cas=ingredient.cas).exists():
                    no_cas_total = no_cas_total + weight
                
                else:
                    fli = FormulaLineItem(cas=ingredient.cas, weight=weight)
                    formula_list.append(fli)
                    
            #add the placeholder if any no cas ingredients exist
            if no_cas_total != 0:
                fli = FormulaLineItem(cas='00-00-00', weight=no_cas_total)
                formula_list.append(fli)
                
        #return formula_list
             
        subhazard_dict = create_subhazard_dict(formula_list)
              
        accumulator = HazardAccumulator(subhazard_dict)
          
        hazard_dict = accumulator.get_hazard_dict()
          
        return hazard_dict
         
        

 
class FlavorIterOrder(models.Model):
    flavor = models.ForeignKey(Flavor)
    
    def __unicode__(self):
        return self.flavor.__unicode__()


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
    natart = models.CharField(max_length=20,blank=True)
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
     
    liquid = models.BooleanField(db_column='Liquid')
    dry = models.BooleanField(db_column='Dry')
    spray_dried = models.BooleanField(db_column='Spray Dried', default=False) # Field renamed to remove spaces.lc
    flavorcoat = models.BooleanField(u"Flavorcoat®", db_column="Flavor Coat", default=False)
    concentrate = models.BooleanField(db_column='Concentrate', default=False)
    oilsoluble = models.BooleanField("Oil soluble", db_column='OilSoluble')
        
    na = models.BooleanField("N/A",db_column='N/A')
    natural = models.BooleanField(db_column='Natural')
    artificial = models.BooleanField(blank=True,default=False)
    nfi = models.BooleanField("NFI", blank=True,default=False)
    organic = models.BooleanField("Organic Compliant", db_column='Organic',blank=True,default=False)
    wonf = models.BooleanField("Natural WONF",db_column='WONF', default=False)
    natural_type = models.BooleanField("Natural Type", blank=True, default=False)
    
    duplication = models.BooleanField(db_column='Duplication',blank=True)
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
    
    flavor = models.ForeignKey('Flavor', related_name='experimental_log', blank=True, null=True)
    location_code_old = models.CharField(blank=True, default="", max_length=20)
    exclude_from_reporting = models.BooleanField(default=False)
    def __unicode__(self):
        return "%s-%s %s %s %s %s" % (self.experimentalnum, self.initials,
                                self.natart, self.product_name, self.label_type, self.datesent_short)
    
    label_properties = (
        'wonf',
        'natural_type',
        'organic',
        'liquid',
        'dry',
        'spray_dried',
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
            'spray_dried',
        ),
        'spray_dried':(
            'oilsoluble',
            'dry',
        ),
        'flavorcoat':(
            'liquid',
            'dry',
            'spray_dried',
            'concentrate',
            'oilsoluble',
        ),
        'na':(
            'natural_type',
            'organic',
            'natural',
            'artificial',
            'nfi',
        ),
        'artificial':(
            'natural_type',
            'natural',
            'nfi',
            'organic',
        ),
        'nfi':(
            'wonf',
            'natural_type',
            'organic',
            'na',
            'natural',
            'artificial',
        ),
    }
    mandatory_categories = (
        ('na','natural','artificial','nfi'),
        ('liquid','dry','spray_dried','flavorcoat'),
    )
    
    def clean_incompatible_categories(self):
        errors = []
        for p, incompatible_p in self.incompatible_categories.iteritems():
            if getattr(self, p) == True:
                for ip in incompatible_p:
                    if getattr(self, ip) == True:
                        errors.append('%s and %s.' % (
                            self._meta.get_field_by_name(p)[0].verbose_name,
                            self._meta.get_field_by_name(ip)[0].verbose_name,
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
                errors.append(unicode(category))
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
        for natart in ('na','artificial','natural','nfi'):
            if getattr(self, natart) == True:
                return self._meta.get_field_by_name(natart)[0].verbose_name

    def get_label_type(self):
        def check_tail_indices(tokens, label_tokens):
            for token in tokens:
                if getattr(self, token) == True:
                    label_tokens.append(self._meta.get_field_by_name(token)[0].verbose_name)

        label_tokens = [];
        tokens = ('dry','spray_dried','oilsoluble','natural_type')
        
        check_tail_indices(tokens, label_tokens)        
        
        if self.flavorcoat == True:
            label_tokens.append(u"Flavorcoat®")
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
            print e
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
        if self.flavor.prefix == "EX":
            self.flavor.name = self.product_name
            self.flavor.natart = self.natart
            self.flavor.label_type = self.label_type

            if self.yield_field != None:
                self.flavor.yield_field = self.yield_field
            else:
                self.flavor.yield_field = 100
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
                    elif my_arg == 'spray_dried':
                        string_kwargs['spray_dried__in'] = [True]
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
        db_table = u'ExperimentalLog'
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
            Q(product_name__icontains=search_string) |
            Q(memo__icontains=search_string)
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
        db_table = u'ShipTo'
        
    def __unicode__(self):
        return self.shiptoname

class Shipper(models.Model):
    """Shipping, logistics and/or freight companies.
    """
    shipperid = models.PositiveIntegerField(primary_key=True, db_column='ShipperID')
    shipper_name = models.CharField(max_length=40, db_column='Shipper Name') # Field renamed to remove spaces.lc
    phone = models.CharField(max_length=24, db_column='Phone')
    
    import_order = 99
    
    class Meta:
        db_table = u'Shippers'
        
    def __unicode__(self):
        return self.shipper_name

def next_id():
    ss = Supplier.objects.all().order_by('id').reverse()[0]
    return ss.id + 1


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
        db_table = u'Suppliers'
        ordering=['suppliername']
        
    def __unicode__(self):
        return self.suppliername   
 
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
    experimental_log = models.ForeignKey('ExperimentalLog') 
    ingredient = models.ForeignKey('Ingredient')
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
                    print "Updating %s" % g
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
                max_length=15, 
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
                max_length=15, 
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
                max_length=15, 
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
    
    def __unicode__(self):
        return self.companyname
    
    class Meta:
        db_table = u'Customers'
        ordering=['companyname']
        
    @staticmethod
    def anonymize():
        for f in Customer.objects.all():
            lorem_one = q.get()
            lorem_two = q.get()
            print f
            f.companyname = "%s %s" % (lorem_one, lorem_two)
            f.save()
            
            q.put(lorem_one)
            q.put(lorem_two)
            
            print f
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
    discontinued = models.BooleanField(db_column='Discontinued')
    approved = models.BooleanField(db_column='Approved')
    productmemo = models.TextField(db_column='ProductMemo')
    sold = models.BooleanField(db_column='Sold')
    spraydried = models.BooleanField(db_column='SprayDried')
    lastprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='LastPrice')
    experimental = models.CharField(max_length=50, db_column='Experimental')
    lastspdate = models.DateTimeField(db_column='LastSPDate')
    
    import_order = 99
    
    class Meta:
        db_table = u'Experimental Products'

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
        db_table = u'Incoming'


def get_default_ship_to():
    return ShipTo.objects.get(shiptoid=1) 
    
def seven_days_from_now():
    return datetime.now() + timedelta(days=7)    

def next_po_number():
    today =date.today()
    po_prefix = today.strftime('%y%m')
    ppn = int(po_prefix)*1000
    try:
        last_po_this_month = PurchaseOrder.objects.filter(number__gte=ppn).order_by('-number')[0]
        next_po_number = last_po_this_month.number + 1
    except:
        next_po_number = ppn + 1
    return next_po_number

class TSRLISortedManager(models.Manager):
    def get_query_set(self):
        return super(TSRLISortedManager, self).get_query_set().order_by('tsr__number')  

class TSRLineItem(models.Model):
    objects = TSRLISortedManager()
    tsr = models.ForeignKey('TSR')
    
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    product = generic.GenericForeignKey('content_type', 'object_id')
    
    code = models.PositiveIntegerField(max_length = 10,)
    usage = models.TextField(blank=True)
    
    
class TSR(models.Model):
    date_in = models.DateField(default=date.today)
    assigned_to = models.ForeignKey(User, related_name="assigned_TSRs")
    entered_by = models.ForeignKey(User, related_name="entered_TSRs")
    number = models.PositiveIntegerField(max_length=7, unique=True)
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
    
    customer = models.ForeignKey('Customer')
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
    
    def __unicode__(self):
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
    number = models.PositiveIntegerField(max_length=7, blank=True, default=next_po_number) #, default=next_po_number)
    shipper = models.ForeignKey('Shipper', default=38)
    ship_to = models.ForeignKey('ShipTo', default=get_default_ship_to)
    supplier = models.ForeignKey('Supplier')
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

    def __unicode__(self):
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
            Q(memo__icontains=search_string) |
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
    def get_query_set(self):
        return super(POLISortedManager, self).get_query_set().order_by('po__number')        

class PurchaseOrderLineItem(models.Model):
    objects = POLISortedManager()
    po = models.ForeignKey('PurchaseOrder')
    raw_material = models.ForeignKey('Ingredient')
    date_received = models.DateTimeField(blank=True, default=datetime.now)
    memo = models.TextField(blank=True)
    memo2 = models.TextField(blank=True)
    quantity = models.DecimalField(decimal_places=2, max_digits=7,default=0)
    due_date = models.DateField(default=seven_days_from_now)
    package_size = models.DecimalField(decimal_places=3, max_digits=7,default=0)
    purchase_price = models.DecimalField(decimal_places=3, max_digits=10, default=0)
    legacy_purchase = models.OneToOneField('LegacyPurchase')
    

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
        lp.datereceived = self.date_received
        lp.pomemo = po.memo
        lp.pomemo2 = po.memo2
        lp.ponumber = po.number
        lp.poquantity = self.quantity
        lp.poduedate = po.due_date
        lp.packagesize = self.package_size
        lp.save()
        self.legacy_purchase = lp
        super(PurchaseOrderLineItem,self).save(*args,**kwargs)

    def __unicode__(self):
        return "%s - %s - %s" % (self.po, self.raw_material, self.quantity)
    
    class Meta:
        ordering = ['po__number', ]
        
def legacy_purchase_auto_number():
    try:
        return LegacyPurchase.objects.all().order_by('-poentry')[0].poentry + 1
    except:
        return 1

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
        db_table = u'Purchases'
        ordering=['ponumber']

    def __unicode__(self):
        return unicode(self.ponumber)


def get_lorem_queue():
    loremfile = open('/var/www/django/fd/loremipsum.txt', 'r')
    lorems = loremfile.read().split(',')
    q = Queue.Queue()
    for word in lorems[0:len(lorems)-1]:
        q.put(word)
    return q
q = get_lorem_queue()

class JIList(models.Model):
    a = models.PositiveIntegerField()
    b = models.PositiveIntegerField()
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
    a = models.ForeignKey('Flavor', related_name="renum_a_set")
    b = models.ForeignKey('Flavor', related_name="renum_b_set")
    
class Solvent(models.Model):
    ingredient = models.OneToOneField('Ingredient', primary_key=True, related_name="solvent_listing")
    def __unicode__(self):
        return unicode(self.ingredient)
    
    @staticmethod
    def get_name_from_name(solvent_number):
        return Ingredient.get_obj_from_softkey(solvent_number).product_name
    
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
        
    def __unicode__(self):
        return "%s -- %s%%" % (self.pin, self.concentration)
    
    
class DigitizedFormula(models.Model):
    experimental_log = models.ForeignKey('ExperimentalLog')
    ingredient_id = models.PositiveSmallIntegerField(blank=True,null=True)
    raw_row = models.TextField(blank=True,null=True)
    
class LocationCode(models.Model):
    location_code = models.CharField(max_length=20)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

    def __unicode__(self):
        return u"%s" % (self.location_code)
    
    
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
    def __unicode__(self):
        return 'MagentoFlavor: %s' % self.flavor
    
    flavor = models.ForeignKey(Flavor)
    sku = models.CharField(blank=True, max_length=20)
    description = models.TextField(blank=True)
    price = models.CharField(blank=True, max_length=10)
    short_description = models.TextField(blank=True)
    
        
        
        
        
        
        

class FlavorSpecification(models.Model):
    flavor = models.ForeignKey('Flavor')
    name = models.CharField(max_length=48) #change this, override save method to enforce uniqueness
    specification = models.CharField(max_length=48)
    micro = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, blank=True, null=True)
    replaces = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    


    def __unicode__(self):
        return 'Flavor: %s, Name: %s, Specification: %s' % (self.flavor, self.name, self.specification)
    
class ReconciledFlavor(models.Model):
    flavor = models.ForeignKey('Flavor')
    reconciled = models.BooleanField(default=False)
    scraped_data = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    reconciled_by = models.ForeignKey(User)
    
    def __unicode__(self):
        return 'Flavor: %s, Reconciled By: %s' % (self.flavor, self.reconciled_by.username)




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

        
        

