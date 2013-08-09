from decimal import Decimal, ROUND_HALF_UP

from django import template

from access.models import Flavor, Ingredient, PurchaseOrder, ExperimentalLog
from unified_adapter.models import ProductInfo
register = template.Library()

ignore_attrs = [
        'diacetyl',
        'crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sulfites',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
        'valid',
        'sold',
        'approved',
        'vaporpressure',
        'supplierid',
        'solvent',
        'flammability',
        'label_type',
        'name',
        'reorderlevel',
        'natart',
        'id',
        'entered',
        'pinnumber',
        'productmemo',
        '_state',
        'code',
        'stability',
        'prefix',
        'reactionextraction',
        'categoryid',
        'lastprice',
        'unitsinstock',
        'discontinued',
        'experimental',
        'quantityperunity',
        'yield_field',
        'no_pg',
        'number',
        'ccp1',
        'ccp2',
        'ccp3',
        'ccp4',
        'ccp5',
        'ccp6',
        'unitprice',
        'solubility',
        'lastspdate',
        'rawmaterialcost',
    ]

def flavor_blades(flavor):
    try:
        flavor.upi = ProductInfo.objects.filter(production_number=flavor.number)[0]
    except:
        flavor.upi = None
    amount = flavor.get_formula_weight()
    try:
        profit_ratio = (flavor.unitprice/flavor.rawmaterialcost).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    except:
        profit_ratio = "Undefined"
    approved = ""
    crit_list = []
    crit_list.append(("Selling Price",flavor.unitprice))
    if flavor.approved == False:
        approved = " Not approved"
    if profit_ratio < Decimal('2.5'):
        approved = "%s profit ratio." % approved
    if Decimal('1000').compare(amount) != 0:
        approved = "%s amount." % approved
    measured_weight = 0
    for fr in flavor.formula_set.all():
        measured_weight += fr.amount
    crit_list.append(("Formula Weight",measured_weight))
    if flavor.pinnumber:
        crit_list.append(("PIN",'<a href="/django/access/ingredient/pin_review/%s/">%s</a>'% (flavor.pinnumber, flavor.pinnumber)))
    if approved != "":
#            if not (flavor.approved == False):
#                flavor.approved = False
#                approved = "%s record." % approved
#                flavor.save()
        crit_list.append(('',"Flagged - %s" % approved,''))
    crit_list.append(("Last Updated",flavor.lastspdate.date().strftime("%m-%d-%y"),''))
    try:
        crit_list.append(("Raw Material Cost", flavor.rawmaterialcost.quantize(Decimal('.001'), rounding=ROUND_HALF_UP),''))
    except:
        crit_list.append(("Raw Material Cost", 0,''))
    crit_list.append(("Profit Ratio", profit_ratio,''))
    
    try:
        lc = flavor.location_code
        if lc != None and lc != "":
            crit_list.append(("Location Code",flavor.location_code))
        else:
            crit_list.append(("Location Code",None))
    except:
        pass
    
    if flavor.number < 60000 and flavor.number > 50000:
        experimentals = flavor.experimental_log.all().order_by('experimentalnum')
        if experimentals.count() != 0:
            experimental_num = experimentals[0].experimentalnum
            label_link = '<a href="/django/lab/experimental_labels/?experimental_number=%s&inventory_slot=">Click here</a>' % (experimental_num)
        else:
            label_link = '<a href="/django/lab/finished_product_labels/?production_number=%s&inventory_slot=">Click here</a>' % (flavor.number)
    else:
        label_link = '<a href="/django/lab/finished_product_labels/?production_number=%s&inventory_slot=">Click here</a>' % (flavor.number)
    crit_list.append((("Get label"),label_link))

    # TODO fix retain / qc stuff
    try:
        qc_card_info = flavor.qc_card_info
    except:
        qc_card_info = False
    if qc_card_info:
        if qc_card_info.appearance != '':
            crit_list.append(("Appearance",qc_card_info.appearance,''))
        if qc_card_info.organoleptic_properties != '':
            crit_list.append(("Organoleptic Properties",qc_card_info.organoleptic_properties,''))
        if qc_card_info.specific_gravity != '' and qc_card_info.specific_gravity != 0:
            crit_list.append(("Specific Gravity",qc_card_info.specific_gravity,''))   
        
    flavor_info_list = []
    try:
        if flavor.keywords != '':
            flavor_info_list.append(("Keywords", flavor.keywords))
        if flavor.solvent != '':
            flavor_info_list.append(("Solvent",flavor.solvent))
        if flavor.flashpoint != 0:
            flavor_info_list.append(('Flash Point', flavor.flashpoint))
        if flavor.kosher != '':
            flavor_info_list.append(('Kosher', flavor.kosher))
        if flavor.allergen != '':
            flavor_info_list.append(('Allergen', flavor.allergen))
        if flavor.sulfites == True:
            flavor_info_list.append(("Sulfites PPM", "%s" % flavor.sulfites_ppm))
            flavor_info_list.append(("Sulfites Usage Threshold", "%s%%" % (flavor.sulfites_usage_threshold)))
        else:
            flavor_info_list.append(("Has no sulfites",''))
                                    
        if flavor.yield_field != 100:
            flavor_info_list.append(('Yield', flavor.yield_field))
            
        if flavor.diacetyl == True:
            flavor_info_list.append(('Has no diacetyl', ''))
        else:
            flavor_info_list.append(('Has diacetyl', ''))
        if flavor.no_pg == True:
            flavor_info_list.append(('Has no PG', ''))
        else:
            flavor_info_list.append(('Has PG', ''))
        for attr in flavor.__dict__:
            value = flavor.__getattribute__(attr)
            if attr in ignore_attrs:
                continue
            if value and type(value) is bool:
                flavor_info_list.append((attr,''))
                
        
    except:
        pass

    ex_link = ''
    try:
        ex = flavor.experimentallog
        ex_link = "<a href=\"%s\">" % (ex.get_admin_url())
        if ex.spg != 0:
            flavor_info_list.append(('Specific Gravity', ex.spg))
        for attr in ex.__dict__:
            value = ex.__getattribute__(attr)
            if value and type(value) is bool:
                flavor_info_list.append((flavor._meta.get_field_by_name(attr)[0].verbose_name,''))
    except:
        pass
    
    flavor_info_list.append(('', '<a href="/django/flavor_usage/%s/new_usage/">New Usage</a>' % flavor.number))
    
    appl_list = []
    for appl in flavor.application_set.all():
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
        flavor_info_list.append((
                          'Usage ',
                          joined_appls
                        ))
    return {
        'flavor':flavor,
        'crit_list': crit_list,
        'flavor_info_list':flavor_info_list,
        'profit_ratio':profit_ratio,
        'experimental_link':ex_link,
            }

@register.inclusion_tag('access/blades.html')
def blades(product):
    if type(product) == ExperimentalLog:
        blade_dict = flavor_blades(product.flavor)
        crit_list = blade_dict['crit_list']
        if product.retain_present:
            crit_list.append(('Retain',product.retain_number))
        else:
            crit_list.append(('Retain','Not present'))
        crit_list.append(('Customer',product.customer))
        crit_list.append(('Specific Gravity',product.spg))
        crit_list.append(('Flash Point',product.flash))
        
        type_list =  ('liquid','dry','spray_dried','concentrate','oilsoluble')
        my_types = []
        for flavor_type in type_list:
            if getattr(product,flavor_type) is True:
                my_types.append(product._meta.get_field_by_name(flavor_type)[0].verbose_name)
        if len(my_types) > 0:
            crit_list.append(('Type',', '.join(my_types)))
        
        marketing_list = ('duplication','promotable','holiday','chef_assist','flavor_coat')
        my_markets = []
        for market_type in marketing_list:
            if getattr(product,market_type) is True:
                my_markets.append(product._meta.get_field_by_name(market_type)[0].verbose_name)
        if len(my_markets) > 0:
            crit_list.append(('Marketing',', '.join(my_markets)))
        
        blade_dict['crit_list'] = crit_list
        return blade_dict
    
    if type(product) == Flavor:
        blade_dict = flavor_blades(product)
        
        experimentals = product.experimental_log.all()
        if experimentals.count() != 0:
            vl = experimentals.values_list('experimentalnum',flat=True)
            experimentals_list = []
            for x in vl:
                experimentals_list.append('<a href="/django/access/experimental/%s/">%s</a>' % (str(x),str(x)))
            crit_list = blade_dict['crit_list']
            crit_list.append(("Experimentals",", ".join(experimentals_list)))
            blade_dict['crit_list'] = crit_list
        return blade_dict
        
    elif type(product) == PurchaseOrder: 
        po = product
        crit_list = []
        crit_list.append(('Date Ordered', po.date_ordered))
        crit_list.append(('Due Date', po.due_date))
        crit_list.append(('Supplier', po.supplier))
        crit_list.append(('Shipper', po.shipper))
        return { 'crit_list': crit_list }
    else:
        ingredient = product
        crit_list = []
        if ingredient.comments != '':
            crit_list.append(('Comments',ingredient.comments))
        if ingredient.cas != '':
            crit_list.append(('CAS',ingredient.cas))
        if ingredient.fema != '':
            crit_list.append(('FEMA',ingredient.fema))
        if ingredient.kosher != '':
            crit_list.append(('Kosher',ingredient.kosher))
            crit_list.append(('Last Kosher Date',ingredient.lastkoshdt))        
        if ingredient.gmo != '':
            crit_list.append(('GMO',ingredient.gmo))
        if ingredient.natural_document_on_file:
            crit_list.append(('Natural Document On File',ingredient.natural_document_on_file))
        if ingredient.allergen != '':
            crit_list.append(('Allergen',ingredient.allergen))
        if ingredient.sprayed:
            crit_list.append(('Spray Dried',ingredient.sprayed))
        if ingredient.microsensitive != '':
            crit_list.append(('Microsensitive',ingredient.microsensitive))
        if ingredient.prop65:
            crit_list.append(('Prop 65',ingredient.prop65))
        if ingredient.nutri:
            crit_list.append(('Nutri',ingredient.nutri))
        if ingredient.transfat:
            crit_list.append(('Transfat',ingredient.transfat))
        return {
            'crit_list': crit_list,
                }
        
        
        
@register.inclusion_tag('access/blades.html')
def print_blades(flavor):      
    blade_list = []
      
    amount = flavor.get_formula_weight()
    try:
        profit_ratio = (flavor.unitprice/flavor.rawmaterialcost).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    except:
        profit_ratio = "Undefined"
    
    approved_reasons = []
    if flavor.approved == False:
        approved_reasons.append("Not approved.")
    if profit_ratio < Decimal('2.5'):
        approved_reasons.append("Profit Ratio.")
    if Decimal('1000').compare(amount) != 0:
        approved_reasons.append("Amount.")
    approved = " ".join(approved_reasons)
    if approved != "":
        blade_list.append(('Not Approved',approved,))
    else:
        blade_list.append(("Approved",''))
        
    blade_list.append(("Selling Price",flavor.unitprice))
    blade_list.append(("Last Updated",flavor.lastspdate.date().strftime("%m-%d-%y"),''))
    try:
        blade_list.append(("Raw Material Cost", flavor.rawmaterialcost.quantize(Decimal('.001'), rounding=ROUND_HALF_UP),''))
    except:
        blade_list.append(("Raw Material Cost", 0,''))
    blade_list.append(("Profit Ratio", profit_ratio,''))
    
    if flavor.pinnumber:
        blade_list.append(("PIN", flavor.pinnumber))
    
    measured_weight = 0
    for fr in flavor.formula_set.all():
        measured_weight += fr.amount
    blade_list.append(("Formula Weight",measured_weight))
    try:
        blade_list.append(("Location Code", flavor.location_code))
    except:
        flavor.upi = None
    
    
#    appl_list = []
#    for appl in flavor.application_set.all():
#        blade_list.append(("Usage","%s %s: %s" % (appl.application_type, appl.memo, appl.usage_level)))

    return {
        'flavor':flavor,
        'crit_list': blade_list,
            }