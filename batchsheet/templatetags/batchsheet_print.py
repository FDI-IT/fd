from django import template

from decimal import Decimal

from batchsheet.forms import BatchSheetForm
from batchsheet.views import weighted_formula_set
from newqc.models import Lot

register = template.Library()

@register.inclusion_tag('batchsheet/batchsheet_print.html')
def batchsheet_print(lot_pk):

    lot = Lot.objects.get(pk = lot_pk)
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
        flavor = lot.flavor
        '''
        try:
            batch_amount = Decimal(batch_sheet_form.cleaned_data['batch_amount'])
        except:
            batch_amount = Decimal("0")
        if 'get_next_lot' in request.GET:
            lot_number = get_next_lot_number()
            json_dict['lot_number'] = lot_number
        else:
            lot_number = batch_sheet_form.cleaned_data['lot_number']
        '''
        if flavor.yield_field and flavor.yield_field != 100:
            batch_amount = lot.amount/(flavor.yield_field/Decimal("100"))
        else:
            batch_amount = lot.amount
        
        weight_factor = batch_amount / Decimal("1000")
        
                
        return {
            'flavor': flavor,
            'weighted_formula_set': weighted_formula_set(flavor, weight_factor),
            'lot_number': lot.number,
            'batch_amount': batch_amount
            }
