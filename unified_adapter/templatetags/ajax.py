from decimal import Decimal, ROUND_HALF_UP

from django import template

from newqc.models import *
from access.models import Flavor

register = template.Library()

@register.inclusion_tag('batchsheet/batchsheet_print.html')
def batchsheet_print(flavor):
    retains = flavor.combed_sorted_retain_superset()
    
    remaining_weight = 0
    remaining_lots = set()
    for r in retains[40:]:
        remaining_lots.add(r.lot)
        
    for l in remaining_lots:
        try:
            remaining_weight += l.amount
        except:
            pass
        
    return {
        'flavor': flavor,
        'retains': retains[:40],
        'remaining_retains': len(retains)-40,
        'remaining_weight': remaining_weight,
        'last_date': retains[-1].date,
            }
