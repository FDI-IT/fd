from django import template

from decimal import Decimal

from batchsheet.forms import BatchSheetForm
from batchsheet.views import weighted_formula_set
from newqc.models import Lot
from access.models import FormulaTree

register = template.Library()

@register.inclusion_tag('batchsheet/explosion_print_component.html')
def explosion_print_component(lot, component, weight):
    weight_factor = lot.amount / Decimal("1000")

    flavor = lot.flavor
                

    dci =  flavor.discontinued_ingredients
    qv = flavor.quick_validate()
    if qv != True:
        flavor = u"%s -- NOT APPROVED -- %s" % (flavor.__unicode__(), qv)
        #c = Context({'flavor':u"%s -- NOT APPROVED -- %s" % (flavor.__unicode__(), qv)})
        #json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)
    elif len(dci) != 0:
        flavor = u"%s -- NOT APPROVED -- Contains discontinued ingredients: %s" % (flavor.__unicode__(), ", ".join(dci))
        #c = Context({'flavor':u"%s -- NOT APPROVED -- Contains discontinued ingredients: %s" % (flavor.__unicode__(), ", ".join(dci))})
        #json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)            
    elif flavor.approved == False:
        flavor = u"%s -- NOT APPROVED" % flavor.__unicode__()
        #c = Context({'flavor':u"%s -- NOT APPROVED" % flavor.__unicode__()})
        #json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)
    else:
#         formula_tree_node = FormulaTree.objects.get(pk=ftpk)
#         batch_amount = formula_tree_node.batch_adjusted_weight(lot.amount)
#         flavor = formula_tree_node.node_flavor
# 
# 
#         component_formula_amount = formula_tree_node.weight
        
                
        batch_amount = weight*lot.amount/1000
        flavor = component
        
        component_formula_amount = weight

        if flavor.yield_field and flavor.yield_field != 100:
            yield_adjusted_amount = component_formula_amount/(flavor.yield_field/Decimal("100"))
        else:
            yield_adjusted_amount = component_formula_amount
        
        
        weight_factor = yield_adjusted_amount * weight_factor / Decimal("1000")
                
    return {
            #'formula_tree_node':formula_tree_node,
            'lot':lot,
            'flavor': flavor,
            'weighted_formula_set': weighted_formula_set(flavor, weight_factor),
            'lot_number': lot.number,
            'batch_amount':batch_amount,
            'yield_adjusted_amount':yield_adjusted_amount
            }
        
@register.inclusion_tag('batchsheet/explosion_print_lot.html')
def explosion_print_lot(lot):
    weight_factor = lot.amount / Decimal("1000")
    return {
            'lot':lot,
            'flavor': lot.flavor,
            'weighted_formula_set': weighted_formula_set(lot.flavor, weight_factor),
            'lot_number': lot.number,
            'batch_amount': lot.amount
            }