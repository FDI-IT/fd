from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.urls import reverse

from access.models import Flavor, FormulaException, FormulaCycleException
from access.utils import coster_headers
register = template.Library()

INGREDIENT = 0
WEIGHT_FACTOR = 1
ROW_ID = 2
PARENT_ID = 3

def explode(flavor, formula_rows):
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
        #yield (ingredient.ingredient, weight_factor, row_id, parent_id)
        #print >>f, row #debug
        row_dict = {}
        row_dict['row_id'] = row[ROW_ID]
        if(row[PARENT_ID] != None):
            row_dict['parent_id'] = row[PARENT_ID]
        ingredient = row[INGREDIENT]
        row_dict['cells'] = coster_cells(ingredient, row[WEIGHT_FACTOR])
        if ingredient.ingredient.is_gazinta:
            row_dict['ing_type'] = "flavor"
        else:
            row_dict['ing_type'] = "raw_material"
        row_dict['obj_id'] = ingredient.ingredient.id
            
        
        table['rows'].append(row_dict)        
    #f.close()

    return {'headers':table['headers'],
            'rows':table['rows'],
            'flavor':flavor}
    
def coster_cells(ingredient, weight_factor):

    rel_weight = ingredient.get_exploded_weight(
                                    weight_factor).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    rel_cost = ingredient.get_exploded_cost(
                                    weight_factor).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
    
    if ingredient.ingredient.is_gazinta:
        flavor = ingredient.gazinta()
        ingredient_pref = flavor.prefix
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
        ingredient_link = "<a href=\"%s\" title=\"%s\">%s</a>" % (
                              reverse('flavor_review', args=[flavor.number]),
                              ingredient_long_title,
                              ingredient_number)
    else:
        rm = ingredient.ingredient
        last_price_update = rm.purchase_price_update.date().strftime("%m-%d-%y")
        name = "%s %s %s" % (rm.art_nati, rm.prefix, rm.product_name)
        number = rm.id
        ingredient_pref = "RM"
        ingredient_number = rm.id
        ingredient_natart = rm.art_nati
        if(rm.microsensitive.lower() != "sensitive"):
            rm.microsensitive = ""
        ingredient_name = '<span class="ingredient-name">%s %s</span> <span class="ingredient-name-2">%s</span><span class="sensitive">%s</span>' % (rm.prefix,
                                                                                                                                                    rm.product_name,
                                                                                                                                                    rm.part_name2,
                                                                                                                                                    rm.microsensitive)
        ingredient_type = "Raw Material"  
        ingredient_long_title = "%s - %s %s %s" % (rm.id,
                                            rm.art_nati,
                                            rm.prefix,
                                            rm.product_name)
        ingredient_link = "<a href=\"%s\" title=\"%s\">%s</a>" % (
                                                      rm.get_review_url(),
                                                      ingredient_long_title,
                                                      ingredient_number)
        unit_cost = rm.unitprice
        
    ingredient_long_title = "%s-%s - %s %s %s" % (ingredient_pref,
                                                  ingredient_number,
                                                  ingredient_natart,
                                                  ingredient_name,
                                                  ingredient_type)
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

@register.inclusion_tag('access/flavor/review_table.html')
def review_table(flavor, weight_factor=1):
    
    try:
        explode_dict = explode(flavor, flavor.formula_traversal(weight_factor=weight_factor))
        explode_dict['flavor'] = flavor
    except FormulaCycleException as e:
        explode_dict['flavor'] = "RCE"
        explode_dict = explode(flavor, flavor.ingredients.all())
    except FormulaException as e:
        explode_dict = {}
        explode_dict['flavor'] = "RE"
    except TypeError as e:
        explode_dict = {}
        explode_dict['flavor'] = "Type Error"
    explode_dict['number'] = flavor.number
    return explode_dict