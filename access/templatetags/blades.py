# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_HALF_UP
from datetime import date

from django import template
from django.contrib.auth.models import Group
from access.models import Flavor, Ingredient, PurchaseOrder, ExperimentalLog, field_status_dict
register = template.Library()

default_flavor_blade_list = (
    'phase', 'product_category', 'solubility',
    'selling_price', 'raw_material_cost', 'profit_ratio', 'ocert', 'batfno', 'flagged', 'formula_weight', 'pin', 'experimental_link',
    'flavor_yield', 'kosher', 'allergen', 'sulfites', 'new_gmo', 'organic_compliant', 'microsensitive', 'vegan', 'prop65', 'spraydried',
    'flashpoint', 'specific_gravity', 'organoleptics', 'color',
    'solvent', 'diacetyl', 'pg',
    'last_updated', 'oldest_price_date',
    'customer_list', 'location_code', 'keywords', 'new_usage', 'application_list',)



    # 'phase', 'selling_price', 'formula_weight', 'pin', 'experimental_link', 'profit_ratio', 'flagged', 'last_updated', 'oldest_price_date', 'raw_material_cost', 'flavor_yield', 'spraydried',
    # 'allergen', 'kosher', 'sulfites','prop65',
    # 'flashpoint', 'specific_gravity', 'organoleptics', 'color',
    # 'solvent',  'diacetyl', 'pg', 'new_gmo', 'organic_compliant', 'microsensitive',
    # 'customer_list', 'batfno', 'location_code','keywords',
    # 'new_usage', 'application_list',)

#This is the list that shows up when an experimetal has already been approved
#Only show a limited amount of fields, since changing these fields will not affect the flavor
default_approved_experimental_blade_list = (
    'flavor_yield', 'spraydried', 'specific_gravity', 'organoleptics', 'color',
    )

print_flavor_blade_list = (
        'flagged',
        'selling_price',
        'last_updated',
        'raw_material_cost',
        'profit_ratio',
        'formula_weight',
        'location_code',
        'oldest_price_date',
    )


class ObjectBlades():
    def get_blade_list(self, property_list):
        for blade_property in property_list:
            val = getattr(self, blade_property)
            if val != None:
                field_color = 'blue'
                if hasattr(self, 'ingredient'):
                    field_color = field_status_dict[self.ingredient.get_field_status(blade_property)]
                elif hasattr(self, 'flavor'):
                    if type(self.flavor) == Flavor:
                        if blade_property == 'ocert':
                            field_color = 'red'
                        else:
                            field_color = field_status_dict[self.flavor.get_field_status(blade_property)]
                yield val + (field_color,)


class FlavorBlades(ObjectBlades):
    def __init__(self, flavor):
        self.flavor = flavor

    @property
    def phase(self):
        return ("Phase", self.flavor.phase)

    @property
    def product_category(self):
        if self.flavor.product_category != None:
            return ("Product Category", self.flavor.product_category)

    @property
    def solubility(self):
        return ("Solubility", self.flavor.solubility)

    @property
    def selling_price(self):
        return ("Selling Price", self.flavor.unitprice)

    @property
    def formula_weight(self):
        total_weight = 0
        for fr in self.flavor.formula_set.all():
            total_weight += fr.amount
        if total_weight != 1000:
            return ("Formula Weight", total_weight)

    @property
    def pin(self):
        if self.flavor.pinnumber != None:
            return ("PIN", '<a href="/access/ingredient/pin_review/%s/">%s</a>'% (self.flavor.pinnumber, self.flavor.pinnumber))

    @property
    def prop65(self):
        prop65 = self.flavor.prop65
        if self.flavor.prop65 != False:
            return ("Prop 65", prop65)

    @property
    def profit_ratio(self):
        try:
            pr = (self.flavor.unitprice/self.flavor.rawmaterialcost).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
        except:
            pr = "Undefined"
        return ("Profit ratio", pr)

    @property
    def ocert(self):
        if self.flavor.organic_certified_required == True:
            if self.flavor.organic_certification_number:
                return ("OCERT Number", self.flavor.organic_certification_number)
            else:
                return ("OCERT Number", "PENDING")
        elif self.flavor.organic_compliant_required == True:
            return ("OCERT Number", "Will not be certified")


    @property
    def spraydried(self):
        sd = self.flavor.spraydried
        if self.flavor.spraydried != False:
            return ("Spray dried", sd)

    @property
    def organoleptics(self):
        organoleptics = self.flavor.organoleptics
        if organoleptics == "":
            organoleptics = "None"
        return ("Organoleptics", organoleptics)

    @property
    def color(self):
        color = self.flavor.color
        if color == "":
            color = "None"
        return ("Color/Appearance", color)

    @property
    def flagged(self):
        allFlags = []
        flagApproved, flagRatio, flagAmount = "", "", ""
        f = FlavorBlades(self.flavor)
        pr = f.profit_ratio[1]
        try:
            amount = self.flavor.get_formula_weight()
        except:
            amount = 0
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
    def customer_list(self):
        customer_list = []
        for experimental in self.flavor.experimental_log.all():
            customer_list.append(u'<a href="%s">%s</a><br>' % (experimental.get_absolute_url(), experimental.customer))
        if len(customer_list) > 0:
            joined_cusomters = ''.join(customer_list)
            return ("Customers", joined_cusomters)
#
#                ex_list = []
#        for experimental in self.flavor.experimental_log.all():
#            ex_list.append(u'<a href="%s">%s-%s</a><br>' % (experimental.get_absolute_url(), experimental.initials, experimental.experimentalnum))
#        if len(ex_list) > 0:
#            joined_exs = ''.join(ex_list)
#            return ("Experimentals", joined_exs)
#        else:
#            return ("Experimentals", "None")

    @property
    def batfno(self):
        batfno = 'None' if self.flavor.batfno == '' else self.flavor.batfno
        if batfno != 'None':
            return ("TTB No.", batfno)

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
            return("Flash Point", "%s°F" % self.flavor.flashpoint)
        else:
            return ("Flash Point", "None")

    @property
    def specific_gravity(self):
        if self.flavor.spg not in (0,"",None):
            return ("Specific Gravity", self.flavor.spg)
        else:
            return ("Specific Gravity", "None")

    @property
    def kosher(self):
        kosher_list = []
        if self.flavor.kosher != "":
            kosher_list.append(self.flavor.kosher)
        if self.flavor.kosher_id != "":
            kosher_list.append(self.flavor.kosher_id)
        if len(kosher_list)>0:
            return("Kosher", " - ".join(kosher_list))
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
        if self.flavor.yield_field != 100:
            return("Yield", self.flavor.yield_field)

    @property
    def diacetyl(self):
        if self.flavor.diacetyl == True:
            dia = "No"
        else:
            dia = "Yes"
        return("Contains Diacetyl", dia)

    @property
    def pg(self):
        if self.flavor.no_pg == True:
            pg = "No"
        else:
            pg = "Yes"
        return("Contains PG", pg)

    @property
    def experimental_link(self):
        ex_list = []
        for experimental in self.flavor.experimental_log.all():
            ex_list.append(u'<a href="%s">%s-%s</a><br>' % (experimental.get_absolute_url(), experimental.initials, experimental.experimentalnum))
        if len(ex_list) > 0:
            joined_exs = ''.join(ex_list)
            return ("Experimentals", joined_exs)

    @property
    def new_usage(self):
        return ("Add New Usage", '<a href="/flavor_usage/%s/new_usage/">Click Here</a>' % self.flavor.number)

    @property
    def application_list(self):
        appl_list = []
        for appl in self.flavor.applications.all():
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

    @property
    def new_gmo(self):
        return ("GMO", self.flavor.new_gmo_string)

        # if self.flavor.gmo == '':
        #     return ("GMO", "No Data")
        # else:
        #     percentage = 0 if self.flavor.gmo_percentage == 0 else self.flavor.gmo_percentage
        #     gmo = "Yes" if percentage > 0 else "No"
        #     return ("GMO", "%s - %.2f%%" % (gmo, percentage))

    @property
    def organic_compliant(self):
        #return ("Organic Compliant", self.flavor.organic_compliant_string)
        if self.flavor.natart == "Nat":
            return ("Organic Compliant", self.flavor.organic_compliant_string)
            # if self.flavor.missing_organic_compliant_data:
            #     #return ("Organic Compliant", "%s - %s" % (self.flavor.calculated_organic_compliant, self.flavor.missing_organic_compliant_data))
            #     #don't show true/false if missing any data
            #     return ("Organic Compliant", self.flavor.missing_organic_compliant_data)
            # else:
            #     return ("Organic Compliant", self.flavor.calculated_organic_compliant)

    @property
    def microsensitive(self):
        return ("Microsensitive", self.flavor.microsensitive)

    @property
    def vegan(self):
        return ("Vegan", self.flavor.calculated_vegan)

class ExperimentalBlades(ObjectBlades):
    def __init__(self, exlog):
        self.exlog = exlog

    @property
    def organoleptics(self):
        organoleptics = self.exlog.organoleptics
        if organoleptics == "":
            organoleptics = "None"
        return ("Organoleptics", organoleptics)

    @property
    def color(self):
        color = self.exlog.color
        if color == "":
            color = "None"
        return ("Color/Appearance", color)

    @property
    def flavor_yield(self):
        yield_field = self.exlog.yield_field
        if yield_field != 100:
            return("Yield", self.exlog.yield_field)

    @property
    def flashpoint(self):
        if self.exlog.flash != 0:
            return("Flash Point", "%s°F" % self.exlog.flash)
        else:
            return ("Flash Point", "None")

    @property
    def specific_gravity(self):
        if self.exlog.spg not in (0,"",None):
            return ("Specific Gravity", self.exlog.spg)
        else:
            return ("Specific Gravity", "None")

    @property
    def spraydried(self):
        sd = self.exlog.spraydried
        return ("Spray dried", sd)

default_ingredient_blade_list = (
    'sub_flavor', 'comments', 'cas', 'fema', 'kosher', 'last_kosher_date', 'new_gmo', 'allergen', 'sprayed', 'microsensitive',
    'prop65', 'nutri', 'organic_compliant', 'gluten_ppm', 'transfat', 'vegan',)

class IngredientBlades(ObjectBlades):
    def __init__(self, ingredient):
        self.ingredient = ingredient

    @property
    def sub_flavor(self):
        if self.ingredient.sub_flavor != None:
            return ("FD Formula", u'<a href="%s">%s</a>' % (self.ingredient.sub_flavor.get_absolute_url(), self.ingredient.sub_flavor))

    @property
    def comments(self):
        if self.ingredient.comments != '':
            return ("Comments", self.ingredient.comments)

    @property
    def inventory(self):
        return ("Amount in Stock", "%0.2f lbs " % self.ingredient.inventory)

    @property
    def cas(self):
        # if self.ingredient.cas != '':
        return ("CAS", self.ingredient.cas)

    @property
    def fema(self):
        # if self.ingredient.fema != '':
        return ("FEMA", self.ingredient.fema)

    @property
    def kosher(self):
        if self.ingredient.kosher != '':
            return ("Kosher", self.ingredient.kosher)
        #else
        #show

    @property
    def last_kosher_date(self):
        if self.ingredient.kosher != '':
            return ("Last Kosher Date", self.ingredient.lastkoshdt.strftime("%m-%d-%y"))

    # @property
    # def gmo(self):
    #     if self.ingredient.gmo != '':
    #         return ("GMO", self.ingredient.gmo)

    @property
    def new_gmo(self):
        if self.ingredient.sub_flavor != None:
            return ("New GMO", self.ingredient.sub_flavor.new_gmo_string)
        if self.ingredient.new_gmo != '':
            return ("New GMO", self.ingredient.new_gmo)
        else:
            return ("New GMO", "NO DATA")

    # @property
    # def natural_document_on_file(self):
    #     # if self.ingredient.natural_document_on_file:
    #     return ("Natural Document On File", self.ingredient.natural_document_on_file)

    @property
    def allergen(self):
        # if self.ingredient.allergen != '':
        return ("Allergen", self.ingredient.allergen)

    @property
    def sprayed(self):
        # if self.ingredient.sprayed:
        return("Spray Dried", self.ingredient.sprayed)

    @property
    def microsensitive(self):
        # if self.ingredient.microsensitive != '':
        return ("Microsensitive", self.ingredient.microsensitive)

    @property
    def prop65(self):
        # if self.ingredient.prop65:
        return ("Prop 65", self.ingredient.prop65)

    @property
    def nutri(self):
        # if self.ingredient.nutri:
        return ("Nutri", self.ingredient.nutri)

    @property
    def organic_compliant(self):
        # if self.ingredient.organic_compliant:
        return ("Organic Compliant", self.ingredient.organic_compliant)

    @property
    def gluten_ppm(self):
        #if self.ingredient.gluten_ppm != 0:
        return ("Gluten PPM", self.ingredient.gluten_ppm)

    @property
    def transfat(self):
        #if self.ingredient.transfat:
        return ("Transfat", self.ingredient.transfat)

    @property
    def vegan(self):
        return ("Vegan", self.ingredient.vegan)

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
def blades(product, user):
    if type(product) == Flavor:
        fb = FlavorBlades(product)
        blade_list = fb.get_blade_list(default_flavor_blade_list)
        return {'blade_list': blade_list,
                'user':user,
        }

    if type(product) == ExperimentalLog:
        if product.flavor:
            if product.flavor.prefix == 'EX':
                fb = FlavorBlades(product.flavor)
                blade_list = fb.get_blade_list(default_flavor_blade_list)
            else:
                fb = FlavorBlades(product.flavor)
                blade_list = fb.get_blade_list(default_approved_experimental_blade_list)
        else:
            eb = ExperimentalBlades(product)
            blade_list = eb.get_blade_list(default_approved_experimental_blade_list)
        return {'blade_list': blade_list,
                'user':user,
        }

    if type(product) == Ingredient:
        ib = IngredientBlades(product)
        blade_list = ib.get_blade_list(default_ingredient_blade_list)
        return {'blade_list': blade_list,
                'user':user,
                'ingredient':product,
        }

    if type(product) == PurchaseOrder:
        pob = PurchaseOrderBlades(product)
        blade_list = pob.get_blade_list(default_purchase_order_blade_list)
        return {'blade_list': blade_list,
                'user':user,
                # 'labuser': permission,
                }

@register.inclusion_tag('access/print_blades.html')
def print_blades(product):
    if type(product) == Flavor:
        fb = FlavorBlades(product)
        blade_list = fb.get_blade_list(print_flavor_blade_list)
        return {'flavor': product, 'blade_list': blade_list}
    elif type(product) == ExperimentalLog:
        eb = ExperimentalBlades(product)
        blade_list = eb.get_blade_list(default_approved_experimental_blade_list)
        return {'flavor': product, 'blade_list': blade_list}



@register.inclusion_tag('access/print_blades.html')
def print_blades_side(flavor):
    fb = FlavorBlades(flavor)
    blade_list = fb.get_blade_list(['pin','experimental_link'])
    return {'flavor':flavor, 'blade_list':blade_list}

# @register.simple_tag
# def get_field_color(product, field):
#     field_status = product.get_field_status(field)
#     if field_status == 'Verified':
#         return 'green'
#     else:
#         return 'red'
