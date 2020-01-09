from decimal import Decimal, ROUND_HALF_UP

from django import template

from newqc.models import *
from access.models import Ingredient
register = template.Library()

@register.inclusion_tag('qc/ingredient/rm_history_print.html')
def rm_history_print(retain_pk):
    r = RMRetain.objects.get(pk=retain_pk)
    ingredient = Ingredient.get_obj_from_softkey(r.pin)
    rm_retains = RMRetain.objects.filter(pin=r.pin)
    rm_info,created = RMInfo.objects.get_or_create(pin=r.pin)
    return {
            'rm_info':rm_info,
            'retain_pk':retain_pk,
            'ingredient':ingredient,
            'rm_retains':rm_retains[:40],
            'remaining_retains': len(rm_retains)-40,
            'last_date': rm_retains.reverse()[0].date,
            }
    
    
#        'retain_pk':retain_pk,
#        'flavor': flavor,
#        'retains': retains[:40],
#        'remaining_retains': len(retains)-40,
#        'remaining_weight': remaining_weight,
#        'last_date': retains[-1].date,