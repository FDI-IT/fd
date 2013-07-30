from decimal import Decimal, ROUND_HALF_UP

from django import template

from newqc.models import *
from access.models import Flavor
register = template.Library()

@register.inclusion_tag('qc/flavors/flavor_history_print.html')
def flavor_history_print(retain_pk):
    r = Retain.objects.get(pk=retain_pk)
    flavor = r.lot.flavor
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
        'retain_pk':retain_pk,
        'flavor': flavor,
        'retains': retains[:40],
        'remaining_retains': len(retains)-40,
        'remaining_weight': remaining_weight,
        'last_date': retains[-1].date,
            }
