from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta, date
import re
import Queue
from operator import itemgetter
from itertools import chain

from django.db import models
from django.db.models import Q, F
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.shortcuts import render_to_response, get_object_or_404

from pluggable.sets import OrderedSet, AncestorSet
from access.exceptions import FormulaException, FormulaWeightException
from access.anonymizer import Anonymizer
#from newqc.models import ProductInfo, Retain
one_hundred = Decimal('100')
zero = Decimal('0')
NATART_CHOICES = (
    ('N/A','N/A'),
    ('Nat','Nat'),
    ('Art','Art'),
    ('NFI','NFI'),
    ('NI','NI'),
)

KOSHER_CHOICES = (
    ('Not assigned','Not assigned'),
    ('Not kosher','Not kosher'),
    ('Pareve','Pareve'),
    ('Dairy','Dairy'),
    ('Meat','Meat'),
    ('Passover','Passover'),
)

def get_next_flavorid():
    return Flavor.objects.all().order_by('-id')[0].id+1

def get_next_rawmaterialcode():
    try:
        return Ingredient.objects.all().order_by('-rawmaterialcode')[0].rawmaterialcode+1
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
        
    @property
    def relative_cost(self):
        return self.get_exploded_cost()

    def __unicode__(self):
        return "%s: l%s r%s parent%s" % (self.root_flavor.__unicode__(), self.lft, self.rgt, self.parent_id)
        
class LeafWeight(models.Model):
    root_flavor = models.ForeignKey('Flavor', related_name="leaf_weights", db_index=True)
    ingredient = models.ForeignKey('Ingredient', db_index=True)
    weight = models.DecimalField(decimal_places=3, max_digits=7)

    
class Formula(models.Model):
    """Constituent ingredients of a particular approved formula.
    Referenced by Flavor number.
    
    Depends on RawMaterial
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    # Flavor points here; one flavor points to many ingredients
    acc_flavor = models.PositiveIntegerField(db_column='FlavorNumber') 
    # Points to the Ingredient table, which actually may be a flavor or rawmat
    acc_ingredient = models.PositiveIntegerField(db_column='ProductID')
    
    # The below fields are added to create true foreign keys to the
    # related tables, not just the pseudo keys used by the legacy joins
    # product = models.ForeignKey('Product', related_name='ingredients')
    flavor = models.ForeignKey('Flavor')
    ingredient = models.ForeignKey('Ingredient')
    amount = models.DecimalField(decimal_places=3,
            max_digits=7,
            db_column='FlavorAmount')
    totalweight = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            db_column='TotalWeight',
            default=Decimal('0'))    
    flavorextendedprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            db_column='FlavorExtendedPrice',
            default=Decimal('0'))
    price = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            db_column='Price',
            default=Decimal('0'))
    discontinued = models.BooleanField(db_column='Discontinued',default=False)
    batchamount = models.PositiveIntegerField(db_column='BatchAmount',default=0)
    machinebatch = models.PositiveIntegerField(db_column='MachineBatch',default=0)
    rawmaterialcode = models.PositiveIntegerField(db_column='RawMaterialCode',default=0)
    # ^not really used since formulas point to PINs not primary keys to the
    # Ingredient table.
    
    # this helps the import-data management command know which order to
    # import tables so that foreign-key dependencies are met
    import_order = 2
    
    class Meta:
        db_table = u'Flavors - Formulae'
        #ordering = ['flavornumber', '-amount',]

    def __unicode__(self):
        return "%s-%s: %s %s lbs" % (self.flavor.prefix, self.flavor.number, self.ingredient.__unicode__(), self.amount)
    
    def get_exploded_weight(self, weight_factor):
        return Decimal(self.amount * weight_factor)
    
    def get_admin_url(self):
        return "BORKEN!"
    
    def get_exploded_cost(self, weight_factor=1):
        if self.ingredient.is_gazinta:
            g = self.gazinta()
            
            try:
                y = g.productspecialinformation.yield_field
            except ProductSpecialInformation.DoesNotExist:
                y = None
            else:
                if y == 0:
                    y = None
            try:
                rmc = g.rawmaterialcost / y / 100
            except:
                rmc = g.rawmaterialcost
        else:
            rmc = self.ingredient.unitprice
        try:
            return self.amount * weight_factor * rmc / 1000
        except TypeError:
            return Decimal('0')
    
    @property
    def relative_cost(self):
        return self.get_exploded_cost()
    
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
    # This is the formula identifier. there may be multiple but only one active
    id = models.PositiveIntegerField("PIN", 
                                     db_column='ProductID',
                                     default=get_next_rawmaterialcode)
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
    unitprice = models.DecimalField(
            decimal_places=3,
            max_digits=10,
            db_column='UnitPrice',)
    purchase_price_update = models.DateTimeField(
            "Date of last purchase price update",
            db_column='LSTPRICDAT',
            blank=True,
            default=datetime(1990,1,1))
    kosher = models.CharField(
            max_length=20,
            db_column='KOSHER',
            blank=True)
    part_name2 = models.CharField(
            max_length=60,
            db_column='PART_NAME2',
            blank=True)
    description = models.CharField(
            max_length=60,
            db_column='DESCRIPT',
            blank=True)
    date_ordered = models.DateTimeField(
            db_column='Date_Ordered',
            blank=True,
            default=datetime(1990,1,1))
    lead_time = models.DecimalField(
            decimal_places=2,
            max_digits=6,
            db_column='LEAD_TIME',
            blank=True,
            default=0)
    unitsonorder = models.DecimalField(
            decimal_places=2,
            max_digits=6,
            db_column='UnitsOnOrder',
            blank=True,
            default=0)
    unitsinstock = models.DecimalField(
            decimal_places=2,
            max_digits=6,
            db_column='UnitsInStock',
            blank=True,
            default=0)
    discontinued = models.BooleanField(
            db_column='Discontinued',
            blank=True)
    comments = models.TextField(
            db_column='COMMENTS',
            blank=True)
    committed = models.DecimalField(
            decimal_places=2,
            max_digits=6,
            db_column='COMMITTED',
            blank=True,
            default=0)
    cas = models.CharField(
            max_length=15,
            db_column='CAS',
            blank=True)
    fema = models.CharField(
            max_length=15,
            db_column='FEMA',
            blank=True)
    
    reorderlevel = models.DecimalField(
            decimal_places=2,
            max_digits=6,
            db_column='ReorderLevel',
            blank=True,
            default=0)
    lastkoshdt = models.DateTimeField(
            db_column='LASTKOSHDT',
            blank=True,
            default=datetime(1990,1,1))
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
    suppliercode = models.CharField(
            max_length=50,
            db_column='SupplierCode',
            blank=True)
    supplierid = models.PositiveIntegerField(
            db_column='SupplierID',
            blank=True,
            default=0)
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
    inventoryng = models.BooleanField(
            db_column='InventoryNG',
            blank=True)
    kencheck = models.BooleanField(
            db_column='Kencheck',
            blank=True)
    kosher_code = models.CharField(
            max_length=50,
            db_column='Kosher Code',
            blank=True)
    fldr = models.CharField(
            max_length=50,
            db_column='FLDR',
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
    
    eggs = models.BooleanField(blank=True)
    fish = models.BooleanField(blank=True)
    milk = models.BooleanField(blank=True)
    peanuts = models.BooleanField(blank=True)
    soybeans = models.BooleanField(blank=True)
    treenuts = models.BooleanField(blank=True)
    wheat = models.BooleanField(blank=True)
    sulfites = models.BooleanField(blank=True)
    sunflower = models.BooleanField(blank=True)
    sesame = models.BooleanField(blank=True)
    mollusks = models.BooleanField(blank=True)
    mustard = models.BooleanField(blank=True)
    celery = models.BooleanField(blank=True)
    lupines = models.BooleanField(blank=True)
    yellow_5 = models.BooleanField(blank=True)
    crustacean = models.BooleanField(blank=True)
    has_allergen_text = models.BooleanField(blank=True)
    
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
        if self.discontinued == False:
            return "/access/ingredient/pin_review/%s/" % self.id
        else:
            return "/access/ingredient/%s/" % self.rawmaterialcode
    
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
            else:
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(bool(int(my_arg)))
                string_kwargs[keyword] = arg_list
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
    def name(self):
        return "%s %s %s - %s" % (self.prefix, self.product_name, self.part_name2, self.description)
    
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
            return Ingredient.objects.filter(discontinued=False).get(flavornum=number)
        else:
            return Ingredient.objects.filter(discontinued=False).get(id=number)
    
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
            flavors_updated_info[f] = [old_rmc.quantize(thousandths), new_rmc.quantize(thousandths)]
            
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
        )
        db_table = u'Raw Materials'
        
    def save(self, *args, **kwargs):
        try:
            self.sub_flavor = Flavor.objects.get(number=self.flavornum)
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
            if (self.sub_flavor.productspecialinformation.yield_field == 100):
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
        return "%s - %s %s %s" % (self.id,
                                   self.art_nati,
                                   self.prefix,
                                   self.product_name)
        
    headers = (
                    ('id','PIN', 'width="30px"'),
                    ('art_nati','N-A', 'width="30px"'),
                    ('name','Name', ''),
                    ('unitprice','Unit Price', 'width=86px class="{sorter: \'link-digit\'}"'),
                    ('purchase_price_update_short','Price Update', 'width=86px'),
                           
                )
    
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


class Flavor(models.Model):
    """Finished products available for sale.
    """
    #retains = generic.GenericRelation(Retain)
    id = models.PositiveIntegerField(
            primary_key=True,
            db_column='ProductID',
            default=get_next_flavorid)
    number = models.PositiveIntegerField(
            db_column='FlavorNumber',
            unique=True)
    # fk to ingredient, one to many
    ingredients = models.ManyToManyField(
            Ingredient,
            through='Formula')
    solvent = models.CharField(
            max_length=50,
            db_column='Solvent',
            blank=True)
    name = models.CharField(
            max_length=40,
            db_column='ProductName')
    prefix = models.CharField(
            max_length=2,
            db_column='ProductPrefix')
    code = models.CharField(
            max_length=3,
            db_column='FlavorCode',
            blank=True)
    natart = models.CharField(
            max_length=3,
            db_column='FlavorNatArt',
            blank=True,
            choices=NATART_CHOICES)
    type = models.CharField(
            max_length=25,
            db_column='FlavorType',
            blank=True)
    categoryid = models.PositiveIntegerField(
            db_column='CategoryID',
            blank=True,
            null=True)
    unitprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            db_column='UnitPrice',
            blank=True,
            null=True)
    quantityperunit = models.PositiveIntegerField(
            db_column='QuantityPerUnit',
            blank=True,
            null=True)
    supplierid = models.PositiveIntegerField(
            db_column='SupplierID',
            blank=True,
            null=True)
    unitsinstock = models.PositiveIntegerField(
            db_column='UnitsInStock',
            blank=True,
            null=True)
    unitsonorder = models.PositiveIntegerField(
            db_column='UnitsOnOrder',
            blank=True,
            null=True)
    reorderlevel = models.PositiveIntegerField(
            db_column='ReorderLevel',
            blank=True,
            null=True)
    discontinued = models.BooleanField(
            db_column='Discontinued',
            blank=True,
            default=False)
    approved = models.BooleanField(
            db_column='Approved',
            blank=True,
            default=False)
    no_pg = models.BooleanField(
            blank=True,
            default=False)
    productmemo = models.TextField(
            db_column='ProductMemo',
            blank=True)
    sold = models.BooleanField(
            db_column='Sold',
            blank=True,
            default=False)
    spraydried = models.BooleanField(
            db_column='SprayDried',
            blank=True,
            default=False)
    lastprice = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            db_column='LastPrice',
            blank=True,
            null=True)
    experimental = models.CharField(
            max_length=50,
            db_column='Experimental',
            blank=True)
    lastspdate = models.DateTimeField(
            db_column='LastSPDate',
            blank=True,
            default=datetime.now)
    rawmaterialcost = models.DecimalField(
            decimal_places=3,
            max_digits=7,
            blank=True,
            null=True)
    valid = models.BooleanField(
            default=False)
    
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
    
    def lot_superset(self):
        examined_flavors = set()
        memo_re = re.compile('Same as (\d{1,8})')
        self.lots = self.lot_set.none()
        def inner_merge_lot_list(f):
            if f in examined_flavors:
                return []
            examined_flavors.add(f)
            self.lots = self.lots | f.lot_set.all()
            
            try:
                match = memo_re.search(f.productmemo)
                if match:
                    f = Flavor.objects.get(number=match.group(1))
                    inner_merge_lot_list(f)
            except Flavor.DoesNotExist:
                pass
    
            try:
                formula_rows = f.formula_set.all()
                if formula_rows.count() == 1:
                    inner_merge_lot_list(formula_rows[0].ingredient.sub_flavor)
            except:
                pass
            
            try:
                i = f.gazinta.all()[0]
                for formula in Formula.objects.filter(ingredient=i, amount=1000):
                    inner_merge_lot_list(formula.flavor)
            except IndexError:
                pass
    
            return
        inner_merge_lot_list(self)                
        return self.lots
        
    def retain_superset(self):
        try:
            lots = self.lot_superset()
            retains = lots[0].retain_set.all()
            for x in range(1,lots.count()):
                retains = retains | lots[x].retain_set.all()
        except:
            return Flavor.objects.none() # this is technically the wrong type
        return retains
    
    def sorted_retain_superset(self):
        return sorted(
            self.retain_superset(),
            key=lambda retain: (retain.date.year, retain.retain),
            reverse=True
        )
        
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
            f.type = "Flavor"
            f.productmemo = "%s %s %s %s" % (lorem_one, lorem_two, lorem_three, lorem_four)
            f.prefix = "FL"
            f.save()
            
            q.put(lorem_one)
            q.put(lorem_two)
            q.put(lorem_three)
            q.put(lorem_four)
            
            print f
            
    @property
    def leaf_nodes(self):
        return FormulaTree.objects.filter(root_flavor=self).filter(rgt=F('lft') + 1)
    
    @property
    def consolidated_leafs(self):
        leaf_ingredients = self.leaf_nodes
        cons_leafs = {}
        for leaf in leaf_ingredients:
            cons_leafs[leaf.node_ingredient] = cons_leafs.get(leaf.node_ingredient, 0) + leaf.weight
        
        return cons_leafs
    
                     
    @property
    def leaf_cost(self):
        scl = LeafWeight.objects.filter(root_flavor=self).select_related()
        total_cost = Decimal('0')
        for leaf in scl:
            total_cost += leaf.ingredient.unitprice * leaf.weight
        total_cost = total_cost/Decimal('1000')
        return total_cost
        
    
    
    @property
    def sorted_consolidated_leafs(self):
        cons_leafs = sorted(self.consolidated_leafs.iteritems(), key=itemgetter(1), reverse=True)
        cons_formulae = []
        for ingredient, amount in cons_leafs:
            cons_formulae.append(Formula(ingredient=ingredient,amount=amount))
        return cons_formulae
            
    
    @property
    def lastspdate_short(self):
        return self.lastspdate.date()
    
    @property
    def yield_adjusted_rmc(self):
        y = None
        try:
            y = self.productspecialinformation.yield_field
        except:
            y = None
        if y and y != zero:
            return self.rawmaterialcost / (y / one_hundred)
        else:
            return self.rawmaterialcost

# TODO: Replace this code with code that works with the new model.
#    @property
#    def qc_card_info(self):
#        try:
#            return ProductInfo.objects.get(object_id=self.pk)
#        except:
#            return None
#    
    import_order = 0
    
    @property
    def url(self):
        return "/access/%s/" % self.number
    
    def get_absolute_url(self):
        return "/access/%s/" % self.number
    
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
                keyword = 'productspecialinformation__%s__in' % (key)
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
            else:
                keyword = '%s__in' % (key)
                arg_list = []
                for my_arg in qdict.getlist(key):
                    arg_list.append(bool(my_arg))
                string_kwargs[keyword] = arg_list
        return string_kwargs
    
    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(Flavor, number=softkey).get_absolute_url()
        except:
            return None

    def get_related_links(self):
        related_links = [
                       ('#flat_review_table','Formula'),
                       ('/access/ajax_dispatch/?tn=consolidated&pk=%s' % self.pk,'Consolidated'),
                       ('/access/ajax_dispatch/?tn=explosion&pk=%s' % self.pk,'Explosion'),
                       ('/access/ajax_dispatch/?tn=legacy_explosion&pk=%s' % self.pk,'Legacy Explosion'),
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
 
    def resembles(self, flavor):

        if self.name != flavor.name:         
            return "name"
        if self.prefix != flavor.prefix:
            return "prefix"
        if self.code != flavor.code:
            return "code"
        if self.natart != flavor.natart:
            return "natart"
        if self.type != flavor.type:
            return "type"
        if self.productmemo != flavor.productmemo:
            return "productmemo"

        return True
    
    class Meta:
        db_table = u'Products'
        ordering = ['number']
        
    def get_fdnum(self):
        return "%s-%s" % (self.prefix, self.number)
    
    def get_admin_url(self):
        return "/admin/access/flavor/%s" % self.id
        
    def __unicode__(self):
        return u"%s-%s %s %s %s" % (self.prefix,
                                   self.number,
                                   self.natart,
                                   self.name,
                                   self.type)
        
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
                        if gaz.productspecialinformation.yield_field != 100:
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
                        if gaz.productspecialinformation.yield_field != 100:
                            explode_weight_factor = weight_factor / (Decimal(gaz.productspecialinformation.yield_field) / 100)
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
            if self.productspecialinformation.yield_field != 100:
                weight_factor = weight_factor / (Decimal(self.productspecialinformation.yield_field) / 100)
        except:
            pass
        for ingredient in inner_traversal(self, weight_factor, row_id, parent_id, parent_flavors):
            yield ingredient

    @staticmethod 
    def get_next_temp_experimental_number():
        """
        Returns the next available number in the experimental range, i.e.
        200,000 through 210,000
        """
        flavors = Flavor.objects.filter(number__gte=200000)\
                                .filter(number__lte=210000)\
                                .order_by('-number')
        try:
            return 1 + flavors[0].number
        except IndexError:
            return 200000
                
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
                    try:
                        y = g.productspecialinformation.yield_field
                    except ProductSpecialInformation.DoesNotExist:
                        pass
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
        try:
            y = self.productspecialinformation.yield_field
        except ProductSpecialInformation.DoesNotExist:
            pass
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
        
    def cycle_check(self, set=AncestorSet()):
        set = AncestorSet()
        def inner_check(f, set):
            set.add(f)
            for gazinta in f.get_gazintas():
                inner_check(gazinta, AncestorSet(set))
            return True
        return inner_check(self, set)
        
        set.add(self)
        for gazinta in self.get_gazintas():
            gazinta.cycle_check(AncestorSet(set))
        return True
    
    headers = (
                    ('prefix','PF', 'width="12px"'),
                    ('number','Number', 'width="50px" class="{sorter: \'link-digit\'}"'),
                    ('natart','N/A', ''),
                    ('name','Name', ''),
                    ('type','Type', ''),
                    ('rawmaterialcost','RMC', 'width=86px'),
                    ('lastspdate_short','Cost Update', 'width=86px'),
                    ('solvent','Solvent', 'width=60px class="{sorter: \'text\'}"'),
                    ('valid','Valid', 'width=30px'),
                    ('approved','Approved', 'width=30px'),
                    ('sold','Sold', 'width=30px'),
                )
    
    @staticmethod
    def text_search(search_string):
        return Flavor.objects.filter( 
            name__icontains=search_string
        )  
    
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

class FlavorIterOrder(models.Model):
    flavor = models.ForeignKey(Flavor)
    
    def __unicode__(self):
        return self.flavor.__unicode__()

class ExperimentalLog(models.Model):
    """
    Records of completed ExperimentalProducts.
    
    TODO FIX ME!!
    """
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
                            max_length=50, 
                            db_column='ProductName')
    initials = models.CharField(
                            max_length=2, 
                            db_column='Initials')
    memo = models.TextField(db_column='Memo',
                            null=True,
                            blank=True)
    liquid = models.BooleanField(db_column='Liquid')
    dry = models.BooleanField(db_column='Dry')
    oilsoluble = models.BooleanField(db_column='OilSoluble')
    organic = models.BooleanField(db_column='Organic')
    duplication = models.BooleanField(db_column='Duplication')
    na = models.BooleanField(db_column='N/A')
    natural = models.BooleanField(db_column='Natural')
    experimental_number = models.PositiveIntegerField(db_column='Experimental Number') # Field renamed to remove spaces.lc
    spg = models.DecimalField(decimal_places=3,
                              max_digits=4, 
                              db_column='SpG')
    flash = models.PositiveIntegerField(
                                db_column='Flash', 
                                default=0)
    usagelevel = models.DecimalField(
                                decimal_places=4,
                                max_digits=6, 
                                db_column='UsageLevel')
    
    # FOREIGN KEY
    product_number = models.PositiveIntegerField(null=True,blank=True,db_column='ProductNumber')
    #flavor = models.OneToOneField('Flavor',null=True)
    # END FOREIGN KEY
    
    concentrate = models.BooleanField(db_column='Concentrate', default=False)
    spray_dried = models.BooleanField(db_column='Spray Dried', default=False) # Field renamed to remove spaces.lc
    promotable = models.BooleanField(db_column='Promotable', default=False)
    holiday = models.BooleanField(db_column='Holiday', default=False)
    coffee = models.BooleanField(db_column='Coffee', default=False)
    tea = models.BooleanField(db_column='Tea', default=False)
    fruit = models.BooleanField(db_column='Fruit', default=False)
    sweet = models.BooleanField(db_column='Sweet', default=False)
    nutraceutical = models.BooleanField(db_column='Nutraceutical', default=False)
    personal_care = models.BooleanField(db_column='Personal Care', default=False) # Field renamed to remove spaces.lc
    meat_and_savory = models.BooleanField(db_column='Meat and Savory', default=False) # Field renamed to remove spaces.lc
    beverage = models.BooleanField(db_column='Beverage', default=False)
    chai = models.BooleanField(db_column='Chai', default=False)
    baked_goods = models.BooleanField(db_column='Baked Goods', default=False) # Field renamed to remove spaces.lc
    dairy = models.BooleanField(db_column='Dairy', default=False)
    pet = models.BooleanField(db_column='Pet', default=False)
    snacks = models.BooleanField(db_column='Snacks', default=False)
    tobacco = models.BooleanField(db_column='Tobacco', default=False)
    non_food = models.BooleanField(db_column='Non-Food', default=False) # Field renamed to remove dashes.lc
    wonf = models.BooleanField(db_column='WONF', default=False)
    chef_assist = models.BooleanField(db_column='Chef Assist', default=False) # Field renamed to remove spaces.lc
    flavor_coat = models.BooleanField(db_column='Flavor Coat', default=False) # Field renamed to remove spaces.lc
    retain_number = models.PositiveIntegerField(db_column='RetainNumber',null=True,blank=True)
    retain_present = models.BooleanField(db_column='RetainPresent',default=False)
    
    def __unicode__(self):
        return "%s-%s %s %s" % (self.initials, self.experimentalnum,
                                self.product_name, self.datesent_short)
    
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
    def datesent_short(self):
        return self.datesent.date()
    
    def save(self, *args, **kwargs):
        if self.retain_number == -1:
            self.retain_number = 0
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
        return string_kwargs
    
    @staticmethod
    def get_absolute_url_from_softkey(softkey):
        try:
            return get_object_or_404(ExperimentalLog, experimentalnum=softkey).get_absolute_url()
        except:
            return None
    
    def get_related_links(self):
        related_links = []
        if self.flavor:
            related_links.append(
                ('/access/%s/' % self.flavor.number, 'Flavor Formula')
            )
        related_links.append(('/access/experimental/%s/' % self.experimentalnum,'Experimental'))
            
        return related_links

    def get_admin_url(self):
        return "/admin/access/experimentallog/%s" % self.id

    import_order = 3
    
    class Meta:
        db_table = u'ExperimentalLog'
        ordering = ['experimentalnum']
    headers = (
                    ('experimentalnum','Number', 'width="80px"'),
                    ('na','N-A', 'width="30px"'),
                    ('product_name','Name', ''),
                    ('initials','Initials', 'width=30x'),
                    ('datesent_short','Date sent', 'width=80px'),
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
    flavornumber = models.PositiveIntegerField(db_column='FlavorNumber') #many lines with the same flavor number; each line is one part of the formula
    productid = models.PositiveIntegerField(db_column='ProductID') #pseudokey to RawMaterial - points to the higher level pin, not the unique identifier, because multiple suppliers' products could be tied to a pin
    flavoramount = models.DecimalField(decimal_places=3,
                                       max_digits=7,
                                       db_column='FlavorAmount',)
    totalweight = models.DecimalField(decimal_places=3,
                                       max_digits=7,
                                       db_column='TotalWeight')
    flavorextendedprice = models.DecimalField(decimal_places=3,
                                              max_digits=7,
                                              db_column='FlavorExtendedPrice')
    price = models.DecimalField(decimal_places=3,
                                max_digits=7,
                                db_column='Price')
    discontinued = models.BooleanField(db_column='Discontinued')
    batchamount = models.PositiveIntegerField(db_column='BatchAmount')
    machinebatch = models.PositiveIntegerField(db_column='MachineBatch')
    rawmaterialcode = models.PositiveIntegerField(db_column='RawMaterialCode') #not sure what the purpose of this field is in here...to specify an ingredient from a certain supplier?
    
    import_order = 99
    
    class Meta:
        db_table = u'Experimental Formulas'
              


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
                max_length=40, 
                db_column='CompanyName')
    billingaddress = models.CharField(
                max_length=60, 
                db_column='BillingAddress',
                blank=True,
                null=True)
    billingaddress2 = models.CharField(
                max_length=20,
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

class ProductSpecialInformation(models.Model):
    """
    Special information relevant to related products.
    """
    flavornumber = models.PositiveIntegerField(primary_key=True, db_column='FlavorNumber')
    productid = models.PositiveIntegerField(db_column='ProductID', blank=True, default=0)
    flavor = models.OneToOneField('Flavor', null=True)
    flashpoint = models.PositiveIntegerField(db_column='FlashPoint', default=0)
    kosher = models.CharField(max_length=20, db_column='Kosher', default="Not Yet Assigned", choices=KOSHER_CHOICES)
    solubility = models.CharField(max_length=25, db_column='Solubility', blank=True, default="")
    stability = models.CharField(max_length=25, db_column='Stability', blank=True, default="")
    nutri_on_file = models.BooleanField(db_column='Nutri on File', default=False) # Field renamed to remove spaces.lc
    flammability = models.CharField(max_length=40, db_column='Flammability', blank=True, default="")
    allergen = models.CharField(max_length=50, db_column='Allergen', blank=True, default="")
    yield_field = models.PositiveIntegerField(db_column='Yield', default=100) # Field renamed because it was a Python reserved word.lc
    pinnumber = models.PositiveIntegerField(db_column='PINNumber', blank=True, null=True)
    kosher_id = models.CharField(max_length=15, db_column='Kosher_ID', default="", blank=True)
    label_check = models.BooleanField(db_column='Label_Check', default=False)
    vaporpressure = models.DecimalField(decimal_places=2,
                                        max_digits=4,
                                        db_column='VaporPressure',
                                        default=0)
    reactionextraction = models.BooleanField(db_column='ReactionExtraction', default=False)
    prop_65 = models.CharField(max_length=50, db_column='PROP 65', blank=True, default="") # Field renamed to remove spaces.lc
    gmo = models.CharField(max_length=50, db_column='GMO', blank=True, default="")
    ccp1 = models.BooleanField(db_column='CCP1', default=False)
    ccp2 = models.BooleanField(db_column='CCP2', default=False)
    ccp3 = models.BooleanField(db_column='CCP3', default=False)
    ccp4 = models.BooleanField(db_column='CCP4', default=False)
    ccp5 = models.BooleanField(db_column='CCP5', default=False)
    ccp6 = models.BooleanField(db_column='CCP6', default=False)
    haccp = models.PositiveSmallIntegerField(db_column='HACCP', blank=True, null=True)
    batfno = models.CharField(max_length=50, db_column='BATFNo', blank=True, default="")
    microtest = models.CharField(max_length=4, db_column='MicroTest', default="", blank=True)
    crustacean = models.BooleanField(db_column='Crustacean', default=False)
    eggs = models.BooleanField(db_column='Eggs', default=False)
    fish = models.BooleanField(db_column='Fish', default=False)
    milk = models.BooleanField(db_column='Milk', default=False)
    peanuts = models.BooleanField(db_column='Peanuts', default=False)
    soybeans = models.BooleanField(db_column='Soybeans', default=False)
    treenuts = models.BooleanField(db_column='TreeNuts', default=False)
    wheat = models.BooleanField(db_column='Wheat', default=False)
    sulfites = models.BooleanField(db_column='Sulfites', default=False)
    organic = models.BooleanField(db_column='Organic', default=False)
    diacetyl = models.BooleanField(db_column='Diacetyl', default=False)
    entered = models.DateTimeField(db_column='Entered', auto_now_add=True)
    spg = models.DecimalField(decimal_places=3,
                              max_digits=4, 
                              blank=True,null=True)
    
    sunflower = models.BooleanField(blank=True)
    sesame = models.BooleanField(blank=True)
    mollusks = models.BooleanField(blank=True)
    mustard = models.BooleanField(blank=True)
    celery = models.BooleanField(blank=True)
    lupines = models.BooleanField(blank=True)
    yellow_5 = models.BooleanField(blank=True)
    
    import_order = 4
    
    def get_admin_url(self):
        return "/admin/access/productspecialinformation/%s" % self.flavornumber
    
    class Meta:
        db_table = u'Products - Special Information'
        
    def __unicode__(self):
        return self.flavor.__unicode__()
    
    def save(self, *args, **kwargs):
        self.productid = self.flavor.pk
        super(ProductSpecialInformation, self).save(*args, **kwargs) 

def get_default_ship_to():
    return ShipTo.objects.get(shiptoid=1) 
    
def seven_days_from_now():
    return datetime.now() + timedelta(days=7)    

def next_po_number():
    today =date.today()
    if today.year == 2012 and today.month == 1:
        po_prefix = today.strftime('%y%m')
        ppn = int(po_prefix)*100
        return int( "%s%02d" % (po_prefix,PurchaseOrder.objects.filter(number__gte=ppn).filter(number__lte=ppn+99).count()))
    else:
        po_prefix = today.strftime('%y%m')
        ppn = int(po_prefix)*1000
        return int( "%s%03d" % (po_prefix,PurchaseOrder.objects.filter(number__gte=ppn).filter(number__lte=ppn+999).count()))
    
    
class PurchaseOrder(models.Model):
    number = models.PositiveIntegerField(max_length=7, blank=True, default=next_po_number) #, default=next_po_number)
    shipper = models.ForeignKey('Shipper', default=38)
    ship_to = models.ForeignKey('ShipTo', default=get_default_ship_to)
    supplier = models.ForeignKey('Supplier')
    date_ordered = models.DateField(auto_now_add=True)
    memo = models.TextField(blank=True, default=" ALL KOSHER PRODUCTS MUST ARRIVE PER YOUR KOSHER CERTIFICATE OR THEY WILL BE REJECTED.")
    memo2 = models.TextField(blank=True, default="C OF A MUST ACCOMPANY SHIPMENT OR BE FAXED PRIOR TO RECEIVING ITEM")
    due_date = models.DateField(default=seven_days_from_now)

    headers = (
                ('number','Number', ''),
                ('due_date','Due Date', ''),
                ('supplier','Supplier', ''),
                ('date_ordered','Date Ordered', ''),
                ('shipper','Shipper', ''),
            )

    def __unicode__(self):
        return "%s - %s - %s" % (self.number, str(self.due_date), self.supplier)
    
    class Meta:
        ordering=['date_ordered']
        
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
    loremfile = open('/home/stachurski/loremipsum.txt', 'r')
    lorems = loremfile.read().split(',')
    q = Queue.Queue()
    for word in lorems[0:len(lorems)-1]:
        q.put(word)
    return q
q = get_lorem_queue()

class ProductSpecialInformation(models.Model):
    """
    Special information relevant to related products.
    """
    flavornumber = models.PositiveIntegerField(primary_key=True, db_column='FlavorNumber')
    productid = models.PositiveIntegerField(db_column='ProductID', blank=True, default=0)

class Flavor(models.Model):
    """Finished products available for sale.
    """
    #retains = generic.GenericRelation(Retain)
    id = models.PositiveIntegerField(
            primary_key=True,
            db_column='ProductID',
            default=get_next_flavorid)
    number = models.PositiveIntegerField(
            db_column='FlavorNumber',
            unique=True)









