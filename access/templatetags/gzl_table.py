from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.core.urlresolvers import reverse

from access.models import Flavor, FormulaException, FormulaCycleException
from access.utils import coster_headers

register = template.Library()

@register.inclusion_tag('access/gzl_table.html')
def gzl_table(product): 
    try:
        explode_dict = explode_gzl(product.gzl_traversal())
        explode_dict['flavor'] = product
    except FormulaCycleException as e:
        raise
    except FormulaException as e:
        raise
    except TypeError as e:
        raise
    
    return explode_dict

def explode_gzl(formula_rows):
    """
    {% comment %}
    The exploded tag needs to be provided with a table object. table 
    must have table.headers and table.rows. Each row must have: 
        row.row_id, 
        row.parent_id, 
        row.cells 
    ordered to correspond with table.headers.
    {% endcomment %}
    <table id="exploded">
    """
    table = {}
    table['headers'] = coster_headers
    #f = open('/tmp/django.dbg', 'w') #debug
    table['rows'] = []
    for row in formula_rows:
        #yield (flavor, weight_factor, row_id, parent_id)
        #print >>f, row #debug
        row_dict = {}
        row_dict['row_id'] = row[2]
        if(row[3] != None):
            row_dict['parent_id'] = row[3]
        flavor = row[0]
        row_dict['cells'] = coster_cells_gzl(flavor, row[1])
        row_dict['ing_type'] = "flavor"
        row_dict['obj_id'] = flavor.id
        table['rows'].append(row_dict)        
    #f.close()

    return {'headers':table['headers'],
            'rows':table['rows'],}
 
def coster_cells_gzl(flavor, weight_factor):

    rel_weight = weight_factor.quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    try:
        rel_cost = (flavor.rawmaterialcost*weight_factor).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    except:
        rel_cost = 1
    
    ingredient_pref = flavor.prefix
    try:
        ingredient_number = flavor.number
        ingredient_natart = flavor.natart
        ingredient_name = '<span class="ingredient-name">%s</span><span class="ingredient-name-2"></span><span class="sensitive"></span>' % (flavor.name)
        ingredient_type = flavor.label_type
        last_price_update = flavor.lastspdate.date().strftime("%m-%d-%y")
        unit_cost = flavor.rawmaterialcost
        ingredient_long_title = "%s - %s %s %s" % (ingredient_number,
                                                   ingredient_natart,
                                                   flavor.name,
                                                   ingredient_type)
        ingredient_link = "<a href=\"%s\" title=\"%s\" target=\"_blank\">%s</a>" % (
                              reverse('flavor_review', args=[flavor.number]),
                              ingredient_long_title,
                              ingredient_number)
    except Exception as e:
        ingredient_number = flavor.id
        ingredient_natart = flavor.art_nati
        ingredient_name = '<span class="ingredient-name">%s %s</span> <span class="ingredient-name-2">%s</span><span class="sensitive">%s</span>' % (flavor.prefix,
                                                                                                                                                    flavor.product_name,
                                                                                                                                                    flavor.part_name2,
                                                                                                                                                    flavor.microsensitive)
        ingredient_type = "Raw Material"  
        last_price_update = flavor.purchase_price_update.date().strftime("%m-%d-%y")
        unit_cost = flavor.unitprice
        ingredient_long_title = "%s - %s %s %s" % (flavor.id,
                                                flavor.art_nati,
                                                flavor.prefix,
                                                flavor.product_name)
        ingredient_link = "<a href=\"%s\" title=\"%s\">%s</a>" % (
                                                      flavor.get_review_url(),
                                                      ingredient_long_title,
                                                      ingredient_number)
    
    ing_num_link = "%s%s%s" % ("<span class=\"flavor_long_name\">", 
                               ingredient_link, 
                               "</span>")
    cell_array=[
                ingredient_pref,
                ing_num_link,
                ingredient_natart,
                ingredient_name,
                ingredient_type,
                last_price_update,
                unit_cost,
                rel_weight,
                rel_cost,
                ]

    return cell_array