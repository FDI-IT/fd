from decimal import Decimal, ROUND_HALF_UP

from django import template

from newqc.models import *
from access.models import Ingredient
register = template.Library()

@register.inclusion_tag('qc/ingredient/rm_history.html')
def rm_history(ingredient__id):
    i = Ingredient.get_obj_from_softkey(ingredient__id)
    rm_retains = RMRetain.objects.filter(pin=i.id)
    rm_info,created = RMInfo.objects.get_or_create(pin=i.id)
    try:
        last_date = rm_retains.reverse()[0].date
    except IndexError:
        last_date = None
    return {
            'rm_info':rm_info,
            'ingredient':i,
            'rm_retains':rm_retains[:40],
            'remaining_retains': len(rm_retains)-40,
            'last_date': last_date,
            }
    
    
#        'retain_pk':retain_pk,
#        'flavor': flavor,
#        'retains': retains[:40],
#        'remaining_retains': len(retains)-40,
#        'remaining_weight': remaining_weight,
#        'last_date': retains[-1].date,