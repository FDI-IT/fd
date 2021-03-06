# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

# Import from purchases db: Purchases

class ExperimentalFormula(models.Model):
    """
    Constituent ingredients of a particular experimental formula.
    
    Depends on RawMaterial.
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    flavornumber = models.IntegerField(db_column='FlavorNumber') #many lines with the same flavor number; each line is one part of the recipe
    productid = models.IntegerField(db_column='ProductID') #pseudokey to RawMaterial - points to the higher level pin, not the unique identifier, because multiple suppliers' products could be tied to a pin
    flavoramount = models.DecimalField(decimal_places=6,
                                       max_digits=10,
                                       db_column='FlavorAmount',)
    totalweight = models.DecimalField(decimal_places=6,
                                       max_digits=10,
                                       db_column='TotalWeight')
    flavorextendedprice = models.DecimalField(decimal_places=4, 
                                              max_digits=12,
                                              db_column='FlavorExtendedPrice')
    price = models.DecimalField(decimal_places=4, 
                                max_digits=12,
                                db_column='Price')
    discontinued = models.BooleanField(db_column='Discontinued')
    batchamount = models.IntegerField(db_column='BatchAmount')
    machinebatch = models.IntegerField(db_column='MachineBatch')
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') #not sure what the purpose of this field is in here...to specify an ingredient from a certain supplier?
    class Meta:
        db_table = u'Experimental Formulas'
              
class FlavorFormula(models.Model):
    """
    Constituent ingredients of a particular approved formula.
    
    Depends on RawMaterial
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    flavornumber = models.IntegerField(db_column='FlavorNumber') #FK to product
    productid = models.IntegerField(db_column='ProductID') #pseudokey to RawMaterial LEGACY
    flavoramount = models.DecimalField(decimal_places=6,
                                       max_digits=10,
                                       db_column='FlavorAmount')
    totalweight = models.DecimalField(decimal_places=6,
                                       max_digits=10,db_column='TotalWeight')
    flavorextendedprice = models.DecimalField(decimal_places=4, 
                                              max_digits=12, 
                                              db_column='FlavorExtendedPrice')
    price = models.DecimalField(decimal_places=4,
                                max_digits=12,
                                db_column='Price')
    discontinued = models.BooleanField(db_column='Discontinued')
    batchamount = models.IntegerField(db_column='BatchAmount')
    machinebatch = models.IntegerField(db_column='MachineBatch')
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') #not really used since the pseudokey is the field on which relevant queries are joined
    
    #The below fields are added to create true foreign keys to the related tables, not just the pseudo keys used by the legacy joins
    #product = models.ForeignKey('Product', related_name='ingredients')
    
    class Meta:
        db_table = u'Flavors - Formulae'
        ordering = ['flavornumber', '-flavoramount',]
        
    def __unicode__(self):
        return "%s %s lbs" % (self.productid, self.flavoramount)

class Customer(models.Model):
    """
    Customer billing, shipping, and contact info.
    """
    #
    # NO SPECIFIED PRIMARY KEY -- USE 'id'
    #
    rpsupsnumber = models.SmallIntegerField(db_column='RPS/UPSNumber')
    companyname = models.CharField(max_length=40, db_column='CompanyName')
    billingaddress = models.CharField(max_length=60, db_column='BillingAddress')
    billingaddress2 = models.CharField(max_length=20, db_column='BillingAddress2')
    billingcity = models.CharField(max_length=35, db_column='BillingCity')
    billingstate = models.CharField(max_length=2, db_column='BillingState')
    billingzip = models.CharField(max_length=10, db_column='BillingZip')
    shipaddress = models.CharField(max_length=60, db_column='ShipAddress')
    shipaddress2 = models.CharField(max_length=20, db_column='ShipAddress2')
    shipcity = models.CharField(max_length=35, db_column='ShipCity')
    shipstate = models.CharField(max_length=2, db_column='ShipState')
    shipzip = models.CharField(max_length=10, db_column='ShipZip')
    billingphone = models.CharField(max_length=24, db_column='BillingPhone')
    shipphone = models.CharField(max_length=24, db_column='ShipPhone')
    billingfax = models.CharField(max_length=24, db_column='BillingFax')
    shipfax = models.CharField(max_length=24, db_column='ShipFax')
    customernotes = models.TextField(db_column='CustomerNotes')
    customerid = models.CharField(unique=True, max_length=5, db_column='CustomerID') # pseudokey that other tables join on
    salesperson = models.CharField(max_length=15, db_column='Salesperson')
    prefix = models.CharField(max_length=10, db_column='Prefix')
    accountingcode = models.CharField(max_length=10, db_column='AccountingCode')
    terms = models.CharField(max_length=10, db_column='Terms')
    country = models.CharField(max_length=15, db_column='Country')
    categoryid = models.IntegerField(db_column='CategoryID') # fk to Categories
    fedex = models.CharField(max_length=11, db_column='Fedex')
    region = models.CharField(max_length=15, db_column='Region')
    extension = models.IntegerField(db_column='Extension')
    contactname = models.CharField(max_length=30, db_column='ContactName')
    gender = models.CharField(max_length=4, db_column='Gender')
    contacttitle = models.CharField(max_length=30, db_column='ContactTitle')
    address = models.CharField(max_length=60, db_column='Address')
    city = models.CharField(max_length=25, db_column='City')
    postalcode = models.CharField(max_length=10, db_column='PostalCode')
    phone = models.CharField(max_length=24, db_column='Phone')
    fax = models.CharField(max_length=24, db_column='Fax')
    homepage = models.CharField(max_length=50, db_column='HomePage')
    email = models.CharField(max_length=50, db_column='EMail')
    customertype = models.CharField(max_length=10, db_column='CustomerType')
    class Meta:
        db_table = u'Customers'

class Product(models.Model):
    """
    Finished products available for sale.
    """
    productid = models.IntegerField(primary_key=True, db_column='ProductID')
    flavorformula = models.IntegerField(db_column='FlavorNumber') # fk to FlavorFormula
    solvent = models.CharField(max_length=50, db_column='Solvent')
    productname = models.CharField(max_length=40, db_column='ProductName')
    productprefix = models.CharField(max_length=2, db_column='ProductPrefix')
    flavorcode = models.CharField(max_length=2, db_column='FlavorCode')
    flavornatart = models.CharField(max_length=3, db_column='FlavorNatArt')
    flavortype = models.CharField(max_length=25, db_column='FlavorType')
    categoryid = models.IntegerField(db_column='CategoryID')
    unitprice = models.DecimalField(decimal_places=4, max_digits=12, db_column='UnitPrice')
    quantityperunit = models.IntegerField(db_column='QuantityPerUnit')
    supplierid = models.IntegerField(db_column='SupplierID')
    unitsinstock = models.IntegerField(db_column='UnitsInStock')
    unitsonorder = models.IntegerField(db_column='UnitsOnOrder')
    reorderlevel = models.IntegerField(db_column='ReorderLevel')
    discontinued = models.BooleanField(db_column='Discontinued')
    approved = models.BooleanField(db_column='Approved')
    productmemo = models.TextField(db_column='ProductMemo')
    sold = models.BooleanField(db_column='Sold')
    spraydried = models.BooleanField(db_column='SprayDried')
    lastprice = models.DecimalField(decimal_places=4, max_digits=12, db_column='LastPrice')
    experimental = models.CharField(max_length=50, db_column='Experimental')
    lastspdate = models.DateTimeField(db_column='LastSPDate')
    
    class Meta:
        db_table = u'Products'
        ordering = ['flavorformula']
        
    def __unicode__(self):
        return "%s-%s %s %s %s" % (self.productprefix, self.flavorformula, self.flavornatart, self.productname, self.flavortype)

    def get_ingredients(self):
        flavor_ingredients = FlavorFormula.objects.filter(flavornumber=flavor_number).order_by('-flavoramount')

class ExperimentalProduct(models.Model):
    """
    Experimental products.
    
    Typically, there exists one object per flavorist. This exists as a
    scratch space. Products that complete the development cycle are checked
    into ExperimentalLog.
    """
    productid = models.IntegerField(primary_key=True, db_column='ProductID')
    flavornumber = models.IntegerField(db_column='FlavorNumber')
    productname = models.CharField(max_length=40, db_column='ProductName')
    productprefix = models.CharField(max_length=2, db_column='ProductPrefix')
    flavorcode = models.CharField(max_length=2, db_column='FlavorCode')
    flavornatart = models.CharField(max_length=3, db_column='FlavorNatArt')
    flavortype = models.CharField(max_length=25, db_column='FlavorType')
    categoryid = models.IntegerField(db_column='CategoryID')
    unitprice = models.DecimalField(decimal_places=4, max_digits=12, db_column='UnitPrice')
    quantityperunit = models.IntegerField(db_column='QuantityPerUnit')
    supplierid = models.IntegerField(db_column='SupplierID')
    unitsinstock = models.IntegerField(db_column='UnitsInStock')
    unitsonorder = models.IntegerField(db_column='UnitsOnOrder')
    reorderlevel = models.IntegerField(db_column='ReorderLevel')
    discontinued = models.BooleanField(db_column='Discontinued')
    approved = models.BooleanField(db_column='Approved')
    productmemo = models.TextField(db_column='ProductMemo')
    sold = models.BooleanField(db_column='Sold')
    spraydried = models.BooleanField(db_column='SprayDried')
    lastprice = models.DecimalField(decimal_places=4, max_digits=12, db_column='LastPrice')
    experimental = models.CharField(max_length=50, db_column='Experimental')
    lastspdate = models.DateTimeField(db_column='LastSPDate')
    class Meta:
        db_table = u'Experimental Products'
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
    spraydried = models.BooleanField(db_column='Spray Dried', default=False) # Field renamed to remove spaces.lc
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

class Incoming(models.Model):
    """
    Incoming R&D samples. 
    
    Samples can be from clients (e.g. a target to duplicate), or raw materials
    from existing or prospective suppliers.
    """
    incomingid = models.IntegerField(primary_key=True, db_column='IncomingID')
    incdate = models.DateTimeField(db_column='IncDate')
    incname = models.CharField(max_length=50, db_column='IncName')
    inccompany = models.CharField(max_length=50, db_column='IncCompany')
    incid = models.CharField(max_length=50, db_column='IncID')
    incmemo = models.TextField(db_column='IncMemo')
    class Meta:
        db_table = u'Incoming'

class ProductSpecialInformation(models.Model):
    """
    Special information relevant to related products.
    """
    flavornumber = models.IntegerField(primary_key=True, db_column='FlavorNumber')
    productid = models.IntegerField(db_column='ProductID')
    flashpoint = models.IntegerField(db_column='FlashPoint')
    kosher = models.CharField(max_length=15, db_column='Kosher')
    solubility = models.CharField(max_length=25, db_column='Solubility')
    stability = models.CharField(max_length=25, db_column='Stability')
    nutri_on_file = models.BooleanField(db_column='Nutri on File') # Field renamed to remove spaces.lc
    flammability = models.CharField(max_length=40, db_column='Flammability')
    allergen = models.CharField(max_length=50, db_column='Allergen')
    yield_field = models.IntegerField(db_column='Yield') # Field renamed because it was a Python reserved word.lc
    pinnumber = models.IntegerField(db_column='PINNumber')
    kosher_id = models.CharField(max_length=15, db_column='Kosher_ID')
    label_check = models.BooleanField(db_column='Label_Check')
    vaporpressure = models.DecimalField(decimal_places=6,
                                       max_digits=10,db_column='VaporPressure')
    reactionextraction = models.BooleanField(db_column='ReactionExtraction')
    prop_65 = models.CharField(max_length=50, db_column='PROP 65') # Field renamed to remove spaces.lc
    gmo = models.CharField(max_length=50, db_column='GMO')
    ccp1 = models.BooleanField(db_column='CCP1')
    ccp2 = models.BooleanField(db_column='CCP2')
    ccp3 = models.BooleanField(db_column='CCP3')
    ccp4 = models.BooleanField(db_column='CCP4')
    ccp5 = models.BooleanField(db_column='CCP5')
    ccp6 = models.BooleanField(db_column='CCP6')
    haccp = models.SmallIntegerField(db_column='HACCP')
    batfno = models.CharField(max_length=50, db_column='BATFNo')
    microtest = models.CharField(max_length=4, db_column='MicroTest')
    crustacean = models.BooleanField(db_column='Crustacean')
    eggs = models.BooleanField(db_column='Eggs')
    fish = models.BooleanField(db_column='Fish')
    milk = models.BooleanField(db_column='Milk')
    peanuts = models.BooleanField(db_column='Peanuts')
    soybeans = models.BooleanField(db_column='Soybeans')
    treenuts = models.BooleanField(db_column='TreeNuts')
    wheat = models.BooleanField(db_column='Wheat')
    sulfites = models.BooleanField(db_column='Sulfites')
    organic = models.BooleanField(db_column='Organic')
    diacetyl = models.BooleanField(db_column='Diacetyl')
    entered = models.DateTimeField(db_column='Entered')
    class Meta:
        db_table = u'Products - Special Information'

#
# PURCHASES SECTION - DATA FROM KRISTY'S DATABASE
# IMPORT IN THIS ORDER
#


class Purchase(models.Model):
    """
    Records of raw material purchases.
    """
    #    * The original field, SupplierCode, was modified to SupplierID and points
    # to the numeric primary key field of the Suppliers table
    # IMPORT FROM KRISTY'S DATABASE
    #
    poentry = models.IntegerField(primary_key=True, db_column='POEntry')
    shipperid = models.IntegerField(db_column='ShipperID') # CONVERT TO FC
    shiptoid = models.IntegerField(db_column='ShipToID') # CONVERT TO FC
    #original line:
    suppliercode = models.CharField(max_length=50, db_column='SupplierCode') # need to add a foreign key to update this; essential to the access app
    #supplierid = models.ForeignKey('Supplier') #FIX
    orderid = models.IntegerField(db_column='OrderID')
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode')
    dateordered = models.DateTimeField(db_column='DateOrdered')
    datereceived = models.DateTimeField(db_column='DateReceived')
    pomemo = models.TextField(db_column='POMemo')
    ponumber = models.IntegerField(db_column='PONumber')
    poquantity = models.DecimalField(decimal_places=4, max_digits=12, db_column='POQuantity')
    poduedate = models.DateTimeField(db_column='PODueDate')
    packagesize = models.DecimalField(decimal_places=4, max_digits=12, db_column='PackageSize')
    pomemo2 = models.TextField(db_column='POMEMO2')
    
    class Meta:
        db_table = u'Purchases'

class RawMaterial(models.Model):
    """
    Raw materials for use in production.
    
    The unique indentifier for this table is 'rawmaterialcode'. Multiple
    unique 'rawmaterialcode' fields can exist with the same productid; this
    represents equivalent raw materials from alternate suppliers.
    """
    rawmaterialcode = models.IntegerField(primary_key=True, db_column='RawMaterialCode')
    productid = models.IntegerField(db_column='ProductID')
    lstpricdat = models.DateTimeField(db_column='LSTPRICDAT')
    productname = models.CharField(max_length=45, db_column='ProductName')
    part_name2 = models.CharField(max_length=45, db_column='PART_NAME2')
    descript = models.CharField(max_length=30, db_column='DESCRIPT')
    date_ordered = models.DateTimeField(db_column='Date_Ordered')
    lead_time = models.DecimalField(decimal_places=4, max_digits=12, db_column='LEAD_TIME')
    unitsonorder = models.DecimalField(decimal_places=4, max_digits=12, db_column='UnitsOnOrder')
    unitsinstock = models.DecimalField(decimal_places=4, max_digits=12, db_column='UnitsInStock')
    discontinued = models.BooleanField(db_column='Discontinued')
    unitprice = models.DecimalField(decimal_places=4, max_digits=12, db_column='UnitPrice')
    prefix = models.CharField(max_length=20, db_column='PREFIX')
    comments = models.CharField(max_length=30, db_column='COMMENTS')
    committed = models.DecimalField(decimal_places=4, max_digits=12, db_column='COMMITTED')
    cas = models.CharField(max_length=15, db_column='CAS')
    fema = models.CharField(max_length=15, db_column='FEMA')
    art_nati = models.CharField(max_length=3, db_column='ART_NATI')
    kosher = models.CharField(max_length=15, db_column='KOSHER')
    reorderlevel = models.DecimalField(decimal_places=4, max_digits=12, db_column='ReorderLevel')
    lastkoshdt = models.DateTimeField(db_column='LASTKOSHDT')
    prodnum = models.CharField(max_length=10, db_column='PRODNUM')
    solution = models.DecimalField(decimal_places=4, max_digits=12, db_column='SOLUTION')
    solvent = models.CharField(max_length=10, db_column='SOLVENT')
    suppliercode = models.CharField(max_length=50, db_column='SupplierCode')
    supplierid = models.IntegerField(db_column='SupplierID')
    gmo = models.CharField(max_length=50, db_column='GMO')
    natural_document_on_file = models.BooleanField(db_column='Natural_Document_On_File')
    allergen = models.CharField(max_length=50, db_column='Allergen')
    sprayed = models.BooleanField(db_column='Sprayed')
    inventoryng = models.BooleanField(db_column='InventoryNG')
    kencheck = models.BooleanField(db_column='Kencheck')
    kosher_code = models.CharField(max_length=50, db_column='Kosher Code') # Field renamed to remove spaces.lc
    fldr = models.CharField(max_length=50, db_column='FLDR')
    microsensitive = models.CharField(max_length=20, db_column='Microsensitive')
    prop65 = models.BooleanField(db_column='Prop65')
    nutri = models.BooleanField(db_column='Nutri')
    transfat = models.BooleanField(db_column='TransFat')
    
    class Meta:
        db_table = u'access_ingredient'
        
    def __unicode__(self):
        return "%s %s" % (self.prefix, self.productname)

class ShipTo(models.Model):
    """
    Incoming shipping destinations
    """
    shiptoid = models.IntegerField(primary_key=True, db_column='ShipToID')
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
    class Meta:
        db_table = u'ShipTo'

class Shipper(models.Model):
    """
    Shipping, logistics and/or freight companies.
    """
    shipperid = models.IntegerField(primary_key=True, db_column='ShipperID')
    shipper_name = models.CharField(max_length=40, db_column='Shipper Name') # Field renamed to remove spaces.lc
    phone = models.CharField(max_length=24, db_column='Phone')
    class Meta:
        db_table = u'Shippers'

class Supplier(models.Model):
    """
    Vendors which supply FDI with raw materials for products.
    """
    id = models.IntegerField(primary_key=True, db_column='ID')
    suppliercode = models.CharField(unique=True, max_length=255, db_column='SupplierCode')
    suppliername = models.CharField(max_length=255, db_column='SupplierName')
    contactname = models.CharField(max_length=255, db_column='ContactName')
    contacttitle = models.CharField(max_length=255, db_column='ContactTitle')
    address = models.CharField(max_length=255, db_column='Address')
    city = models.CharField(max_length=255, db_column='City')
    region = models.CharField(max_length=255, db_column='Region')
    postalcode = models.CharField(max_length=255, db_column='PostalCode')
    country = models.CharField(max_length=255, db_column='Country')
    phone = models.CharField(max_length=255, db_column='Phone')
    fax = models.CharField(max_length=255, db_column='Fax')
    supplierid = models.DecimalField(unique=True, decimal_places=4, max_digits=12, db_column='SupplierID') #FIX this isn't unique in the source, convert to use the serial pk
    rawmaterialcode = models.DecimalField(decimal_places=4, max_digits=12, db_column='RawMaterialCode')
    homepage = models.CharField(max_length=255, db_column='HomePage')
    email = models.CharField(max_length=255, db_column='EMail')
    class Meta:
        db_table = u'Suppliers'

