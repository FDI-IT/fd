# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class FlavorbaseRawmaterial(models.Model):
    product_ptr = models.ForeignKey(FlavorbaseProduct)
    class Meta:
        db_table = u'flavorbase_rawmaterial'

class FlavorbaseProduct(models.Model):
    id = models.IntegerField(primary_key=True)
    real_type = models.ForeignKey(DjangoContentType)
    number = models.IntegerField()
    name = models.CharField(max_length=100)
    class Meta:
        db_table = u'flavorbase_product'

class FormsMeetinglog(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField()
    attendees = models.TextField()
    meeting_type = models.TextField()
    topic = models.TextField()
    conclusions = models.TextField()
    action_items = models.TextField()
    signatures = models.TextField()
    class Meta:
        db_table = u'forms_meetinglog'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        db_table = u'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    message = models.TextField()
    class Meta:
        db_table = u'auth_message'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        db_table = u'auth_user_user_permissions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    content_type = models.ForeignKey(DjangoContentType)
    object_id = models.TextField()
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = u'django_admin_log'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        db_table = u'auth_user_groups'

class DjangoComments(models.Model):
    id = models.IntegerField(primary_key=True)
    content_type = models.ForeignKey(DjangoContentType)
    object_pk = models.TextField()
    site = models.ForeignKey(DjangoSite)
    user = models.ForeignKey(AuthUser)
    user_name = models.CharField(max_length=50)
    user_email = models.CharField(max_length=75)
    user_url = models.CharField(max_length=200)
    comment = models.TextField()
    submit_date = models.DateTimeField()
    ip_address = models.IPAddressField()
    is_public = models.BooleanField()
    is_removed = models.BooleanField()
    class Meta:
        db_table = u'django_comments'

class DjangoCommentFlags(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    comment = models.ForeignKey(DjangoComments)
    flag = models.CharField(max_length=30)
    flag_date = models.DateTimeField()
    class Meta:
        db_table = u'django_comment_flags'

class DjangoSession(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = u'django_session'

class FlavorbaseFlavor(models.Model):
    product_ptr = models.ForeignKey(FlavorbaseProduct)
    prefix = models.CharField(max_length=2)
    appearance = models.CharField(max_length=100)
    organoleptic_properties = models.CharField(max_length=100)
    testing_procedure = models.TextField()
    flash_point = models.FloatField()
    specific_gravity = models.FloatField()
    notes = models.TextField()
    renumber = models.ForeignKey('self')
    class Meta:
        db_table = u'flavorbase_flavor'

class QcRetain(models.Model):
    id = models.IntegerField(primary_key=True)
    retain = models.SmallIntegerField()
    date = models.DateField()
    lot = models.ForeignKey(ProductionLot)
    status = models.CharField(max_length=25)
    notes = models.TextField()
    content_type = models.ForeignKey(DjangoContentType)
    object_id = models.IntegerField()
    class Meta:
        db_table = u'qc_retain'

class ProductionLot(models.Model):
    id = models.IntegerField(primary_key=True)
    lot = models.IntegerField()
    sub_lot = models.SmallIntegerField()
    date = models.DateField()
    status = models.CharField(max_length=25)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    flavor = models.ForeignKey(FlavorbaseFlavor)
    class Meta:
        db_table = u'production_lot'

class Supplier(models.Model):
    id = models.IntegerField(primary_key=True)
    supplier_name = models.CharField(max_length=50)
    class Meta:
        db_table = u'supplier'

class ExperimentalFormulas(models.Model):
    id = models.IntegerField(primary_key=True)
    flavornumber = models.IntegerField(db_column='FlavorNumber') # Field name made lowercase.
    productid = models.IntegerField(db_column='ProductID') # Field name made lowercase.
    flavoramount = models.DecimalField(decimal_places=3, max_digits=7, db_column='FlavorAmount') # Field name made lowercase.
    totalweight = models.DecimalField(decimal_places=3, max_digits=7, db_column='TotalWeight') # Field name made lowercase.
    flavorextendedprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='FlavorExtendedPrice') # Field name made lowercase.
    price = models.DecimalField(decimal_places=3, max_digits=7, db_column='Price') # Field name made lowercase.
    discontinued = models.BooleanField(db_column='Discontinued') # Field name made lowercase.
    batchamount = models.IntegerField(db_column='BatchAmount') # Field name made lowercase.
    machinebatch = models.IntegerField(db_column='MachineBatch') # Field name made lowercase.
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') # Field name made lowercase.
    class Meta:
        db_table = u'Experimental Formulas'

class Customers(models.Model):
    id = models.IntegerField(primary_key=True)
    rps/upsnumber = models.SmallIntegerField(db_column='RPS/UPSNumber') # Field name made lowercase.
    companyname = models.CharField(max_length=40, db_column='CompanyName') # Field name made lowercase.
    billingaddress = models.CharField(max_length=60, db_column='BillingAddress') # Field name made lowercase.
    billingaddress2 = models.CharField(max_length=20, db_column='BillingAddress2') # Field name made lowercase.
    billingcity = models.CharField(max_length=35, db_column='BillingCity') # Field name made lowercase.
    billingstate = models.CharField(max_length=2, db_column='BillingState') # Field name made lowercase.
    billingzip = models.CharField(max_length=10, db_column='BillingZip') # Field name made lowercase.
    shipaddress = models.CharField(max_length=60, db_column='ShipAddress') # Field name made lowercase.
    shipaddress2 = models.CharField(max_length=20, db_column='ShipAddress2') # Field name made lowercase.
    shipcity = models.CharField(max_length=35, db_column='ShipCity') # Field name made lowercase.
    shipstate = models.CharField(max_length=2, db_column='ShipState') # Field name made lowercase.
    shipzip = models.CharField(max_length=10, db_column='ShipZip') # Field name made lowercase.
    billingphone = models.CharField(max_length=24, db_column='BillingPhone') # Field name made lowercase.
    shipphone = models.CharField(max_length=24, db_column='ShipPhone') # Field name made lowercase.
    billingfax = models.CharField(max_length=24, db_column='BillingFax') # Field name made lowercase.
    shipfax = models.CharField(max_length=24, db_column='ShipFax') # Field name made lowercase.
    customernotes = models.TextField(db_column='CustomerNotes') # Field name made lowercase.
    customerid = models.CharField(unique=True, max_length=5, db_column='CustomerID') # Field name made lowercase.
    salesperson = models.CharField(max_length=15, db_column='Salesperson') # Field name made lowercase.
    prefix = models.CharField(max_length=10, db_column='Prefix') # Field name made lowercase.
    accountingcode = models.CharField(max_length=10, db_column='AccountingCode') # Field name made lowercase.
    terms = models.CharField(max_length=10, db_column='Terms') # Field name made lowercase.
    country = models.CharField(max_length=15, db_column='Country') # Field name made lowercase.
    categoryid = models.IntegerField(db_column='CategoryID') # Field name made lowercase.
    fedex = models.CharField(max_length=11, db_column='Fedex') # Field name made lowercase.
    region = models.CharField(max_length=15, db_column='Region') # Field name made lowercase.
    extension = models.IntegerField(db_column='Extension') # Field name made lowercase.
    contactname = models.CharField(max_length=30, db_column='ContactName') # Field name made lowercase.
    gender = models.CharField(max_length=4, db_column='Gender') # Field name made lowercase.
    contacttitle = models.CharField(max_length=30, db_column='ContactTitle') # Field name made lowercase.
    address = models.CharField(max_length=60, db_column='Address') # Field name made lowercase.
    city = models.CharField(max_length=25, db_column='City') # Field name made lowercase.
    postalcode = models.CharField(max_length=10, db_column='PostalCode') # Field name made lowercase.
    phone = models.CharField(max_length=24, db_column='Phone') # Field name made lowercase.
    fax = models.CharField(max_length=24, db_column='Fax') # Field name made lowercase.
    homepage = models.CharField(max_length=50, db_column='HomePage') # Field name made lowercase.
    email = models.CharField(max_length=50, db_column='EMail') # Field name made lowercase.
    customertype = models.CharField(max_length=10, db_column='CustomerType') # Field name made lowercase.
    class Meta:
        db_table = u'Customers'

class ExperimentalProducts(models.Model):
    productid = models.IntegerField(primary_key=True, db_column='ProductID') # Field name made lowercase.
    flavornumber = models.IntegerField(db_column='FlavorNumber') # Field name made lowercase.
    product_name = models.CharField(max_length=40, db_column='ProductName') # Field name made lowercase.
    productprefix = models.CharField(max_length=2, db_column='ProductPrefix') # Field name made lowercase.
    flavorcode = models.CharField(max_length=2, db_column='FlavorCode') # Field name made lowercase.
    flavornatart = models.CharField(max_length=3, db_column='FlavorNatArt') # Field name made lowercase.
    flavortype = models.CharField(max_length=25, db_column='FlavorType') # Field name made lowercase.
    categoryid = models.IntegerField(db_column='CategoryID') # Field name made lowercase.
    unitprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='UnitPrice') # Field name made lowercase.
    quantityperunit = models.IntegerField(db_column='QuantityPerUnit') # Field name made lowercase.
    supplierid = models.IntegerField(db_column='SupplierID') # Field name made lowercase.
    unitsinstock = models.IntegerField(db_column='UnitsInStock') # Field name made lowercase.
    unitsonorder = models.IntegerField(db_column='UnitsOnOrder') # Field name made lowercase.
    reorderlevel = models.IntegerField(db_column='ReorderLevel') # Field name made lowercase.
    discontinued = models.BooleanField(db_column='Discontinued') # Field name made lowercase.
    approved = models.BooleanField(db_column='Approved') # Field name made lowercase.
    productmemo = models.TextField(db_column='ProductMemo') # Field name made lowercase.
    sold = models.BooleanField(db_column='Sold') # Field name made lowercase.
    spraydried = models.BooleanField(db_column='SprayDried') # Field name made lowercase.
    lastprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='LastPrice') # Field name made lowercase.
    experimental = models.CharField(max_length=50, db_column='Experimental') # Field name made lowercase.
    lastspdate = models.DateTimeField(db_column='LastSPDate') # Field name made lowercase.
    class Meta:
        db_table = u'Experimental Products'

class Experimentallog(models.Model):
    experimentalnum = models.IntegerField(primary_key=True, db_column='ExperimentalNum') # Field name made lowercase.
    datesent = models.DateTimeField(db_column='DateSent') # Field name made lowercase.
    customer = models.CharField(max_length=50, db_column='Customer') # Field name made lowercase.
    product_name = models.CharField(max_length=50, db_column='ProductName') # Field name made lowercase.
    initials = models.CharField(max_length=2, db_column='Initials') # Field name made lowercase.
    memo = models.TextField(db_column='Memo') # Field name made lowercase.
    liquid = models.BooleanField(db_column='Liquid') # Field name made lowercase.
    dry = models.BooleanField(db_column='Dry') # Field name made lowercase.
    oilsoluble = models.BooleanField(db_column='OilSoluble') # Field name made lowercase.
    organic = models.BooleanField(db_column='Organic') # Field name made lowercase.
    duplication = models.BooleanField(db_column='Duplication') # Field name made lowercase.
    n/a = models.BooleanField(db_column='N/A') # Field name made lowercase.
    natural = models.BooleanField(db_column='Natural') # Field name made lowercase.
    experimental_number = models.IntegerField(db_column='Experimental Number') # Field renamed to remove spaces. Field name made lowercase.
    spg = models.DecimalField(decimal_places=3, max_digits=4, db_column='SpG') # Field name made lowercase.
    flash = models.IntegerField(db_column='Flash') # Field name made lowercase.
    usagelevel = models.DecimalField(decimal_places=4, max_digits=5, db_column='UsageLevel') # Field name made lowercase.
    productnumber = models.IntegerField(db_column='ProductNumber') # Field name made lowercase.
    concentrate = models.BooleanField(db_column='Concentrate') # Field name made lowercase.
    spraydried = models.BooleanField(db_column='Spray Dried') # Field renamed to remove spaces. Field name made lowercase.
    promotable = models.BooleanField(db_column='Promotable') # Field name made lowercase.
    holiday = models.BooleanField(db_column='Holiday') # Field name made lowercase.
    coffee = models.BooleanField(db_column='Coffee') # Field name made lowercase.
    tea = models.BooleanField(db_column='Tea') # Field name made lowercase.
    fruit = models.BooleanField(db_column='Fruit') # Field name made lowercase.
    sweet = models.BooleanField(db_column='Sweet') # Field name made lowercase.
    nutraceutical = models.BooleanField(db_column='Nutraceutical') # Field name made lowercase.
    personal_care = models.BooleanField(db_column='Personal Care') # Field renamed to remove spaces. Field name made lowercase.
    meat_and_savory = models.BooleanField(db_column='Meat and Savory') # Field renamed to remove spaces. Field name made lowercase.
    beverage = models.BooleanField(db_column='Beverage') # Field name made lowercase.
    chai = models.BooleanField(db_column='Chai') # Field name made lowercase.
    baked_goods = models.BooleanField(db_column='Baked Goods') # Field renamed to remove spaces. Field name made lowercase.
    dairy = models.BooleanField(db_column='Dairy') # Field name made lowercase.
    pet = models.BooleanField(db_column='Pet') # Field name made lowercase.
    snacks = models.BooleanField(db_column='Snacks') # Field name made lowercase.
    tobacco = models.BooleanField(db_column='Tobacco') # Field name made lowercase.
    non_food = models.BooleanField(db_column='Non-Food') # Field renamed to remove dashes. Field name made lowercase.
    wonf = models.BooleanField(db_column='WONF') # Field name made lowercase.
    chef_assist = models.BooleanField(db_column='Chef Assist') # Field renamed to remove spaces. Field name made lowercase.
    flavor_coat = models.BooleanField(db_column='Flavor Coat') # Field renamed to remove spaces. Field name made lowercase.
    class Meta:
        db_table = u'ExperimentalLog'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(max_length=100)
    name = models.CharField(max_length=50)
    class Meta:
        db_table = u'django_site'

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        db_table = u'auth_group'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey(DjangoContentType)
    codename = models.CharField(max_length=100)
    class Meta:
        db_table = u'auth_permission'

class Incoming(models.Model):
    incomingid = models.IntegerField(primary_key=True, db_column='IncomingID') # Field name made lowercase.
    incdate = models.DateTimeField(db_column='IncDate') # Field name made lowercase.
    incname = models.CharField(max_length=50, db_column='IncName') # Field name made lowercase.
    inccompany = models.CharField(max_length=50, db_column='IncCompany') # Field name made lowercase.
    incid = models.CharField(max_length=50, db_column='IncID') # Field name made lowercase.
    incmemo = models.TextField(db_column='IncMemo') # Field name made lowercase.
    class Meta:
        db_table = u'Incoming'

class ProductsSpecialInformation(models.Model):
    flavornumber = models.IntegerField(primary_key=True, db_column='FlavorNumber') # Field name made lowercase.
    productid = models.IntegerField(db_column='ProductID') # Field name made lowercase.
    flashpoint = models.IntegerField(db_column='FlashPoint') # Field name made lowercase.
    kosher = models.CharField(max_length=15, db_column='Kosher') # Field name made lowercase.
    solubility = models.CharField(max_length=25, db_column='Solubility') # Field name made lowercase.
    stability = models.CharField(max_length=25, db_column='Stability') # Field name made lowercase.
    nutri_on_file = models.BooleanField(db_column='Nutri on File') # Field renamed to remove spaces. Field name made lowercase.
    flammability = models.CharField(max_length=40, db_column='Flammability') # Field name made lowercase.
    allergen = models.CharField(max_length=50, db_column='Allergen') # Field name made lowercase.
    yield_field = models.IntegerField(db_column='Yield') # Field renamed because it was a Python reserved word. Field name made lowercase.
    pinnumber = models.IntegerField(db_column='PINNumber') # Field name made lowercase.
    kosher_id = models.CharField(max_length=15, db_column='Kosher_ID') # Field name made lowercase.
    label_check = models.BooleanField(db_column='Label_Check') # Field name made lowercase.
    vaporpressure = models.DecimalField(decimal_places=2, max_digits=4, db_column='VaporPressure') # Field name made lowercase.
    reactionextraction = models.BooleanField(db_column='ReactionExtraction') # Field name made lowercase.
    prop65 = models.CharField(max_length=50, db_column='PROP 65') # Field renamed to remove spaces. Field name made lowercase.
    gmo = models.CharField(max_length=50, db_column='GMO') # Field name made lowercase.
    ccp1 = models.BooleanField(db_column='CCP1') # Field name made lowercase.
    ccp2 = models.BooleanField(db_column='CCP2') # Field name made lowercase.
    ccp3 = models.BooleanField(db_column='CCP3') # Field name made lowercase.
    ccp4 = models.BooleanField(db_column='CCP4') # Field name made lowercase.
    ccp5 = models.BooleanField(db_column='CCP5') # Field name made lowercase.
    ccp6 = models.BooleanField(db_column='CCP6') # Field name made lowercase.
    haccp = models.SmallIntegerField(db_column='HACCP') # Field name made lowercase.
    batfno = models.CharField(max_length=50, db_column='BATFNo') # Field name made lowercase.
    microtest = models.CharField(max_length=4, db_column='MicroTest') # Field name made lowercase.
    crustacean = models.BooleanField(db_column='Crustacean') # Field name made lowercase.
    eggs = models.BooleanField(db_column='Eggs') # Field name made lowercase.
    fish = models.BooleanField(db_column='Fish') # Field name made lowercase.
    milk = models.BooleanField(db_column='Milk') # Field name made lowercase.
    peanuts = models.BooleanField(db_column='Peanuts') # Field name made lowercase.
    soybeans = models.BooleanField(db_column='Soybeans') # Field name made lowercase.
    treenuts = models.BooleanField(db_column='TreeNuts') # Field name made lowercase.
    wheat = models.BooleanField(db_column='Wheat') # Field name made lowercase.
    sulfites = models.BooleanField(db_column='Sulfites') # Field name made lowercase.
    organic = models.BooleanField(db_column='Organic') # Field name made lowercase.
    diacetyl = models.BooleanField(db_column='Diacetyl') # Field name made lowercase.
    entered = models.DateTimeField(db_column='Entered') # Field name made lowercase.
    class Meta:
        db_table = u'Products - Special Information'

class LegacyPurchases(models.Model):
    poentry = models.IntegerField(primary_key=True, db_column='POEntry') # Field name made lowercase.
    shipperid = models.IntegerField(db_column='ShipperID') # Field name made lowercase.
    shiptoid = models.IntegerField(db_column='ShipToID') # Field name made lowercase.
    suppliercode = models.CharField(max_length=50, db_column='SupplierCode') # Field name made lowercase.
    orderid = models.IntegerField(db_column='OrderID') # Field name made lowercase.
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') # Field name made lowercase.
    dateordered = models.DateTimeField(db_column='DateOrdered') # Field name made lowercase.
    datereceived = models.DateTimeField(db_column='DateReceived') # Field name made lowercase.
    pomemo = models.TextField(db_column='POMemo') # Field name made lowercase.
    ponumber = models.IntegerField(db_column='PONumber') # Field name made lowercase.
    poquantity = models.DecimalField(decimal_places=2, max_digits=7, db_column='POQuantity') # Field name made lowercase.
    poduedate = models.DateTimeField(db_column='PODueDate') # Field name made lowercase.
    packagesize = models.DecimalField(decimal_places=3, max_digits=7, db_column='PackageSize') # Field name made lowercase.
    pomemo2 = models.TextField(db_column='POMEMO2') # Field name made lowercase.
    class Meta:
        db_table = u'Purchases'

class RawMaterials(models.Model):
    productid = models.IntegerField(db_column='ProductID') # Field name made lowercase.
    lstpricdat = models.DateTimeField(db_column='LSTPRICDAT') # Field name made lowercase.
    product_name = models.CharField(max_length=45, db_column='ProductName') # Field name made lowercase.
    part_name2 = models.CharField(max_length=45, db_column='PART_NAME2') # Field name made lowercase.
    descript = models.CharField(max_length=30, db_column='DESCRIPT') # Field name made lowercase.
    date_ordered = models.DateTimeField(db_column='Date_Ordered') # Field name made lowercase.
    lead_time = models.DecimalField(decimal_places=2, max_digits=6, db_column='LEAD_TIME') # Field name made lowercase.
    unitsonorder = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsOnOrder') # Field name made lowercase.
    unitsinstock = models.DecimalField(decimal_places=2, max_digits=6, db_column='UnitsInStock') # Field name made lowercase.
    discontinued = models.BooleanField(db_column='Discontinued') # Field name made lowercase.
    unitprice = models.DecimalField(decimal_places=3, max_digits=10, db_column='UnitPrice') # Field name made lowercase.
    prefix = models.CharField(max_length=20, db_column='PREFIX') # Field name made lowercase.
    comments = models.CharField(max_length=30, db_column='COMMENTS') # Field name made lowercase.
    committed = models.DecimalField(decimal_places=2, max_digits=6, db_column='COMMITTED') # Field name made lowercase.
    cas = models.CharField(max_length=15, db_column='CAS') # Field name made lowercase.
    fema = models.CharField(max_length=15, db_column='FEMA') # Field name made lowercase.
    art_nati = models.CharField(max_length=3, db_column='ART_NATI') # Field name made lowercase.
    kosher = models.CharField(max_length=15, db_column='KOSHER') # Field name made lowercase.
    reorderlevel = models.DecimalField(decimal_places=2, max_digits=6, db_column='ReorderLevel') # Field name made lowercase.
    lastkoshdt = models.DateTimeField(db_column='LASTKOSHDT') # Field name made lowercase.
    prodnum = models.CharField(max_length=10, db_column='PRODNUM') # Field name made lowercase.
    solution = models.DecimalField(decimal_places=3, max_digits=5, db_column='SOLUTION') # Field name made lowercase.
    solvent = models.CharField(max_length=10, db_column='SOLVENT') # Field name made lowercase.
    suppliercode = models.CharField(max_length=50, db_column='SupplierCode') # Field name made lowercase.
    supplierid = models.IntegerField(db_column='SupplierID') # Field name made lowercase.
    gmo = models.CharField(max_length=50, db_column='GMO') # Field name made lowercase.
    natural_document_on_file = models.BooleanField(db_column='Natural_Document_On_File') # Field name made lowercase.
    allergen = models.CharField(max_length=50, db_column='Allergen') # Field name made lowercase.
    sprayed = models.BooleanField(db_column='Sprayed') # Field name made lowercase.
    inventoryng = models.BooleanField(db_column='InventoryNG') # Field name made lowercase.
    kencheck = models.BooleanField(db_column='Kencheck') # Field name made lowercase.
    kosher_code = models.CharField(max_length=50, db_column='Kosher Code') # Field renamed to remove spaces. Field name made lowercase.
    fldr = models.CharField(max_length=50, db_column='FLDR') # Field name made lowercase.
    microsensitive = models.CharField(max_length=20, db_column='Microsensitive') # Field name made lowercase.
    prop65 = models.BooleanField(db_column='Prop65') # Field name made lowercase.
    nutri = models.BooleanField(db_column='Nutri') # Field name made lowercase.
    transfat = models.BooleanField(db_column='TransFat') # Field name made lowercase.
    rawmaterialcode = models.IntegerField(primary_key=True, db_column='RawMaterialCode') # Field name made lowercase.
    class Meta:
        db_table = u'Raw Materials'

class FlavorsFormulae(models.Model):
    id = models.IntegerField(primary_key=True)
    flavornumber = models.IntegerField(db_column='FlavorNumber') # Field name made lowercase.
    productid = models.IntegerField(db_column='ProductID') # Field name made lowercase.
    flavor = models.ForeignKey(Products)
    ingredient = models.ForeignKey(RawMaterials)
    flavoramount = models.DecimalField(decimal_places=3, max_digits=7, db_column='FlavorAmount') # Field name made lowercase.
    totalweight = models.DecimalField(decimal_places=3, max_digits=7, db_column='TotalWeight') # Field name made lowercase.
    flavorextendedprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='FlavorExtendedPrice') # Field name made lowercase.
    price = models.DecimalField(decimal_places=3, max_digits=7, db_column='Price') # Field name made lowercase.
    discontinued = models.BooleanField(db_column='Discontinued') # Field name made lowercase.
    batchamount = models.IntegerField(db_column='BatchAmount') # Field name made lowercase.
    machinebatch = models.IntegerField(db_column='MachineBatch') # Field name made lowercase.
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') # Field name made lowercase.
    class Meta:
        db_table = u'Flavors - Formulae'

class Products(models.Model):
    productid = models.IntegerField(primary_key=True, db_column='ProductID') # Field name made lowercase.
    flavornumber = models.IntegerField(db_column='FlavorNumber') # Field name made lowercase.
    solvent = models.CharField(max_length=50, db_column='Solvent') # Field name made lowercase.
    product_name = models.CharField(max_length=40, db_column='ProductName') # Field name made lowercase.
    productprefix = models.CharField(max_length=2, db_column='ProductPrefix') # Field name made lowercase.
    flavorcode = models.CharField(max_length=3, db_column='FlavorCode') # Field name made lowercase.
    flavornatart = models.CharField(max_length=3, db_column='FlavorNatArt') # Field name made lowercase.
    flavortype = models.CharField(max_length=25, db_column='FlavorType') # Field name made lowercase.
    categoryid = models.IntegerField(db_column='CategoryID') # Field name made lowercase.
    unitprice = models.DecimalField(decimal_places=2, max_digits=7, db_column='UnitPrice') # Field name made lowercase.
    quantityperunit = models.IntegerField(db_column='QuantityPerUnit') # Field name made lowercase.
    supplierid = models.IntegerField(db_column='SupplierID') # Field name made lowercase.
    unitsinstock = models.IntegerField(db_column='UnitsInStock') # Field name made lowercase.
    unitsonorder = models.IntegerField(db_column='UnitsOnOrder') # Field name made lowercase.
    reorderlevel = models.IntegerField(db_column='ReorderLevel') # Field name made lowercase.
    discontinued = models.BooleanField(db_column='Discontinued') # Field name made lowercase.
    approved = models.BooleanField(db_column='Approved') # Field name made lowercase.
    productmemo = models.TextField(db_column='ProductMemo') # Field name made lowercase.
    sold = models.BooleanField(db_column='Sold') # Field name made lowercase.
    spraydried = models.BooleanField(db_column='SprayDried') # Field name made lowercase.
    lastprice = models.DecimalField(decimal_places=3, max_digits=7, db_column='LastPrice') # Field name made lowercase.
    experimental = models.CharField(max_length=50, db_column='Experimental') # Field name made lowercase.
    lastspdate = models.DateTimeField(db_column='LastSPDate') # Field name made lowercase.
    class Meta:
        db_table = u'Products'

class Shipto(models.Model):
    shiptoid = models.IntegerField(primary_key=True, db_column='ShipToID') # Field name made lowercase.
    shiptoaddress = models.CharField(max_length=50, db_column='ShipToAddress') # Field name made lowercase.
    shiptocontact = models.CharField(max_length=50, db_column='ShipToContact') # Field name made lowercase.
    shiptocity = models.CharField(max_length=50, db_column='ShipToCity') # Field name made lowercase.
    shiptoregion = models.CharField(max_length=50, db_column='ShipToRegion') # Field name made lowercase.
    shiptopostalcode = models.CharField(max_length=50, db_column='ShipToPostalCode') # Field name made lowercase.
    shiptocountry = models.CharField(max_length=50, db_column='ShipToCountry') # Field name made lowercase.
    shiptophone = models.CharField(max_length=50, db_column='ShipToPhone') # Field name made lowercase.
    shiptofax = models.CharField(max_length=50, db_column='ShipToFax') # Field name made lowercase.
    shiptocontacttitle = models.CharField(max_length=50, db_column='ShipToContactTitle') # Field name made lowercase.
    shiptoname = models.CharField(max_length=50, db_column='ShipToName') # Field name made lowercase.
    class Meta:
        db_table = u'ShipTo'

class Shippers(models.Model):
    shipperid = models.IntegerField(primary_key=True, db_column='ShipperID') # Field name made lowercase.
    shipper_name = models.CharField(max_length=40, db_column='Shipper Name') # Field renamed to remove spaces. Field name made lowercase.
    phone = models.CharField(max_length=24, db_column='Phone') # Field name made lowercase.
    class Meta:
        db_table = u'Shippers'

class Suppliers(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID') # Field name made lowercase.
    suppliercode = models.CharField(unique=True, max_length=255, db_column='SupplierCode') # Field name made lowercase.
    suppliername = models.CharField(max_length=255, db_column='SupplierName') # Field name made lowercase.
    contactname = models.CharField(max_length=255, db_column='ContactName') # Field name made lowercase.
    contacttitle = models.CharField(max_length=255, db_column='ContactTitle') # Field name made lowercase.
    address = models.CharField(max_length=255, db_column='Address') # Field name made lowercase.
    city = models.CharField(max_length=255, db_column='City') # Field name made lowercase.
    region = models.CharField(max_length=255, db_column='Region') # Field name made lowercase.
    postalcode = models.CharField(max_length=255, db_column='PostalCode') # Field name made lowercase.
    country = models.CharField(max_length=255, db_column='Country') # Field name made lowercase.
    phone = models.CharField(max_length=255, db_column='Phone') # Field name made lowercase.
    fax = models.CharField(max_length=255, db_column='Fax') # Field name made lowercase.
    supplierid = models.IntegerField(unique=True, db_column='SupplierID') # Field name made lowercase.
    rawmaterialcode = models.IntegerField(db_column='RawMaterialCode') # Field name made lowercase.
    homepage = models.CharField(max_length=255, db_column='HomePage') # Field name made lowercase.
    email = models.CharField(max_length=255, db_column='EMail') # Field name made lowercase.
    class Meta:
        db_table = u'Suppliers'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    password = models.CharField(max_length=128)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    is_superuser = models.BooleanField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = u'auth_user'

class ReversionRevision(models.Model):
    id = models.IntegerField(primary_key=True)
    date_created = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    comment = models.TextField()
    class Meta:
        db_table = u'reversion_revision'

class ReversionVersion(models.Model):
    id = models.IntegerField(primary_key=True)
    revision = models.ForeignKey(ReversionRevision)
    object_id = models.TextField()
    content_type = models.ForeignKey(DjangoContentType)
    format = models.CharField(max_length=255)
    serialized_data = models.TextField()
    object_repr = models.TextField()
    class Meta:
        db_table = u'reversion_version'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    class Meta:
        db_table = u'django_content_type'

class HaccpWatertest(models.Model):
    id = models.IntegerField(primary_key=True)
    test_date = models.DateField()
    zone = models.SmallIntegerField()
    test_result = models.DecimalField(max_digits=2, decimal_places=1)
    class Meta:
        db_table = u'haccp_watertest'

class HaccpReceivinglog(models.Model):
    id = models.IntegerField(primary_key=True)
    entry_date = models.DateTimeField()
    receiving_number = models.IntegerField()
    pin_number = models.IntegerField()
    supplier_id = models.ForeignKey(Supplier)
    description_of_goods = models.CharField(max_length=50)
    package_quantity = models.IntegerField()
    supplier_lot_number = models.CharField(max_length=25)
    po_number = models.IntegerField()
    truck = models.CharField(max_length=25)
    kosher_group = models.ForeignKey(HaccpKoshergroup)
    notes = models.TextField()
    class Meta:
        db_table = u'haccp_receivinglog'

class HaccpKoshergroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=2)
    class Meta:
        db_table = u'haccp_koshergroup'

class HaccpTobaccobeetletest(models.Model):
    qualitytest_ptr = models.ForeignKey(HaccpQualitytest)
    test_result = models.SmallIntegerField()
    class Meta:
        db_table = u'haccp_tobaccobeetletest'

class SouthMigrationhistory(models.Model):
    id = models.IntegerField(primary_key=True)
    app_name = models.CharField(max_length=255)
    migration = models.CharField(max_length=255)
    applied = models.DateTimeField()
    class Meta:
        db_table = u'south_migrationhistory'

class HaccpThermometertest(models.Model):
    qualitytest_ptr = models.ForeignKey(HaccpQualitytest)
    test_result = models.SmallIntegerField()
    class Meta:
        db_table = u'haccp_thermometertest'

class HaccpQualitytest(models.Model):
    id = models.IntegerField(primary_key=True)
    test_date = models.DateField()
    zone = models.SmallIntegerField()
    class Meta:
        db_table = u'haccp_qualitytest'

