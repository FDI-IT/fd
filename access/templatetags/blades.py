from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from django import template

from access.models import Flavor, Ingredient, PurchaseOrder, ExperimentalLog
register = template.Library()

default_flavor_blade_list = (
    'selling_price', 'formula_weight', 'pin', 'profit_ratio', 'flagged', 'last_updated', 'oldest_price_date', 'raw_material_cost', 'location_code', 
    'keywords', 'solvent', 'flashpoint', 'kosher', 'allergen', 'sulfites', 'flavor_yield', 'diacetyl', 'pg', 'experimental_link',
    'new_usage', 'application_list')

print_flavor_blade_list = (
        'flagged',
        'selling_price',
        'last_updated',
        'raw_material_cost',
        'profit_ratio',
        'formula_weight',
        'location_code',
    )

class ObjectBlades():
    def get_blade_list(self, property_list):
        for blade_property in property_list:
            yield getattr(self, blade_property)

class FlavorBlades(ObjectBlades):
    def __init__(self, flavor):
        self.flavor = flavor
        
    @property
    def selling_price(self):
        return ("Selling Price", self.flavor.unitprice)
    
    @property
    def formula_weight(self):
        total_weight = 0
        for fr in self.flavor.formula_set.all():
            total_weight += fr.amount
        return ("Formula Weight", total_weight)
    
    @property
    def pin(self):
        return ("PIN", '<a href="/django/access/ingredient/pin_review/%s/">%s</a>'% (self.flavor.pinnumber, self.flavor.pinnumber))
    
    @property
    def profit_ratio(self):
        try:
            pr = (self.flavor.unitprice/self.flavor.rawmaterialcost).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
        except:
            pr = "Undefined"
        return ("Profit ratio", pr)
    
    @property
    def flagged(self):
        allFlags = []
        flagApproved, flagRatio, flagAmount = "", "", ""
        f = FlavorBlades(self.flavor)
        pr = f.profit_ratio[1]
        amount = self.flavor.get_formula_weight()
        if self.flavor.approved == False:
            flagApproved = "Not approved"
        if pr < Decimal('2.5'):
            flagRatio = "Profit Ratio: %s" % pr
        if Decimal('1000').compare(amount) != 0:
            flagAmount = "Amount: %s" % amount
        
        if flagApproved != "":
            allFlags.append(flagApproved)
        if flagRatio != "":
            allFlags.append(flagRatio)
        if flagAmount != "":
            allFlags.append(flagAmount)
        
        allFlags_string = "\n".join(allFlags)
        
        if allFlags != []:
            return ("Flagged", allFlags_string)
        else:
            return ("Approved","")

    
    @property
    def last_updated(self):
        return("Last Updated", self.flavor.lastspdate.date().strftime("%m-%d-%y"))  
    
    @property
    def oldest_price_date(self):
        oldest_date = date.today()
        oldest_rm_pin = 0
        for lw in self.flavor.leaf_weights.all():
            ppu_date = lw.ingredient.purchase_price_update.date()
            if ppu_date < oldest_date:
                oldest_date = ppu_date
                oldest_rm_pin = lw.ingredient.id
                
        return ("Oldest RM Price", "PIN: %s -- %s" % (oldest_rm_pin, oldest_date))
        
    @property
    def raw_material_cost(self):
        try:
            rmc = self.flavor.rawmaterialcost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except:
            rmc = 0
        return("Raw Material Cost", rmc)
    
    @property
    def location_code(self):
        try:
            lc = self.flavor.location_code
        except:
            lc = "None"
        return("Location Code", lc)
    
    @property
    def keywords(self):
        if self.flavor.keywords != '':
            kw = self.flavor.keywords
        else:
            kw = 'None'
        return("Keywords", kw)
    
    @property
    def solvent(self):
        if self.flavor.solvent != '':
            sv = self.flavor.solvent
        else:
            sv = 'None'
        return("Solvent", sv)
    
    @property
    def flashpoint(self):
        if self.flavor.flashpoint != 0:
            return("Flash Point", self.flavor.flashpoint)
        else:
            return ("Flash Point", "None")
    
    @property
    def kosher(self):
        if self.flavor.kosher != '':
            return("Kosher", self.flavor.kosher)
        else:
            return ("Kosher", "None")
    
    @property    
    def allergen(self):
        if self.flavor.allergen != '':
            return("Allergen", self.flavor.allergen)
        else:
            return ("Allergen", "None")
    
    @property
    def sulfites(self):
        if self.flavor.sulfites == True:
            sf = "Sulfites PPM: %s, Sulfites Usage Threshold: %s" % (self.flavor.sulfites_ppm, self.flavor.sulfites_usage_threshold)
        else:
            sf = "None"
        return("Sulfites", sf)
    
    @property
    def flavor_yield(self):
        return("Yield", self.flavor.yield_field)
    
    @property
    def diacetyl(self):
        if self.flavor.diacetyl == True:
            dia = "No"
        else:
            dia = "Yes"
        return("Contains Diacetyl?", dia)
    
    @property
    def pg(self):
        if self.flavor.no_pg == True:
            pg = "No"
        else:
            pg = "Yes"
        return("Contains PG?", pg)
    
    @property
    def experimental_link(self):
        ex_list = []
        for experimental in self.flavor.experimental_log.all():
            ex_list.append(u'<a href="%s">%s-%s</a><br>' % (experimental.get_absolute_url(), experimental.initials, experimental.experimentalnum))
        if len(ex_list) > 0:
            joined_exs = ''.join(ex_list)
            return ("Experimentals", joined_exs)
        else:
            return ("Experimentals", "None")
    
    @property
    def new_usage(self):
        return ("Add New Usage", '<a href="/django/flavor_usage/%s/new_usage/">Click Here</a>' % self.flavor.number)

    @property
    def application_list(self):
        appl_list = []
        for appl in self.flavor.application_set.all():
            if appl.top_usage_level:
                appl_list.append(u'<a href="%s" title="%s">%s: %s-%s%% %s</a><br>' % 
                          (appl.get_admin_url(), appl.memo, appl.application_type.name, appl.usage_level,appl.top_usage_level, appl.short_memo, )
                        )
            else:
                appl_list.append(u'<a href="%s" title="%s">%s: %s%% %s</a><br>' % 
                          (appl.get_admin_url(), appl.memo, appl.application_type.name, appl.usage_level, appl.short_memo, )
                        )
        
        if len(appl_list) > 0:
            joined_appls = ''.join(appl_list)
            return ("Usage", joined_appls)
        else:
            return ("Usage", "None")
        

default_ingredient_blade_list = (
    'comments', 'cas', 'fema', 'kosher', 'last_kosher_date', 'gmo', 'natural_document_on_file', 'allergen', 'sprayed', 'microsensitive', 
    'prop65', 'nutri', 'transfat'    )

class IngredientBlades(ObjectBlades):
    def __init__(self, ingredient):
        self.ingredient = ingredient    

    @property
    def comments(self):
        if self.ingredient.comments != '':
            return ("Comments", self.ingredient.comments)
        
    @property
    def cas(self):
        if self.ingredient.cas != '':
            return ("CAS", self.ingredient.cas)
   
    @property    
    def fema(self):
        if self.ingredient.fema != '':
            return ("FEMA", self.ingredient.fema)
    
    @property
    def kosher(self):
        if self.ingredient.kosher != '':
            return ("Kosher", self.ingredient.kosher)
    
    @property
    def last_kosher_date(self):
        if self.ingredient.kosher != '':
            return ("Last Kosher Date", self.ingredient.lastkoshdt.strftime("%m-%d-%y"))
  
    @property    
    def gmo(self):
        if self.ingredient.gmo != '':
            return ("GMO", self.ingredient.gmo)
 
    @property
    def natural_document_on_file(self):
        if self.ingredient.natural_document_on_file:
            return ("Natural Document On File", self.ingredient.natural_document_on_file)

    @property
    def allergen(self):
        if self.ingredient.allergen != '':
            return ("Allergen", self.ingredient.allergen)
   
    @property
    def sprayed(self):
        if self.ingredient.sprayed:
            return("Spray Dried", self.ingredient.sprayed)
   
    @property
    def microsensitive(self):
        if self.ingredient.microsensitive != '':
            return ("Microsensitive", self.ingredient.microsensitive)
 
    @property   
    def prop65(self):
        if self.ingredient.prop65:
            return ("Prop 65", self.ingredient.prop65)
   
    @property    
    def nutri(self):
        if self.ingredient.nutri:
            return ("Nutri", self.ingredient.nutri)
    
    @property
    def transfat(self):
        if self.ingredient.transfat:
            return ("Transfat", self.ingredient.transfat)


default_purchase_order_blade_list = (
    'date_ordered', 'due_date', 'supplier', 'shipper')

class PurchaseOrderBlades(ObjectBlades):
    def __init__(self, purchase_order):
        self.purchase_order = purchase_order

    @property
    def date_ordered(self):
        return ("Date Ordered", self.purchase_order.date_ordered)
    
    @property
    def due_date(self):
        return ("Due Date", self.purchase_order.due_date)
    
    @property
    def supplier(self):
        return ("Supplier", self.purchase_order.supplier)
    
    @property
    def shipper(self):
        return ("Shipper", self.purchase_order.shipper)
    
    @property
    def all_blades(self):
        blade_list = []
        po = self.purchase_order
        blade_list.append(('Date Ordered', po.date_ordered))
        blade_list.append(('Due Date', po.due_date))
        blade_list.append(('Supplier', po.supplier))
        blade_list.append(('Shipper', po.shipper))
        return blade_list
    
@register.inclusion_tag('access/blades.html')
def blades(product):
    if type(product) == Flavor:
        fb = FlavorBlades(product)
        blade_list = fb.get_blade_list(default_flavor_blade_list)
        return {'blade_list': blade_list}
    
    if type(product) == ExperimentalLog:
        fb = FlavorBlades(product.flavor)
        blade_list = fb.get_blade_list(default_flavor_blade_list)
        return {'blade_list': blade_list}
        
    
    if type(product) == Ingredient:
        ib = IngredientBlades(product)
        blade_list = ib.get_blade_list(default_ingredient_blade_list)
        return {'blade_list': blade_list}
    
    if type(product) == PurchaseOrder:
        pob = PurchaseOrderBlades(product)
        blade_list = pob.get_blade_list(default_purchase_order_blade_list)
        return {'blade_list': blade_list}    
    
@register.inclusion_tag('access/blades.html')
def print_blades(flavor):
    fb = FlavorBlades(flavor)
    blade_list = fb.get_blade_list(print_flavor_blade_list)
    return {'flavor':flavor, 'blade_list':blade_list}
    
    