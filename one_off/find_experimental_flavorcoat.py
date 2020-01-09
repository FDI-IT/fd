"""find_experimental_flavorcoat

Find experimental flavorcoats and show what their names would be updated to.
"""
from access.models import *
import reversion

def search(apple_flakes_pin):
    
    a = Ingredient.get_obj_from_softkey(apple_flakes_pin)
    edict = {}
    for lw in a.leafweight_set.filter(root_flavor__prefix='EX').select_related():
        for e in lw.root_flavor.experimental_log.all():
            edict[e.experimentalnum] = ["%s %s %s" % (e.natart, e.product_name, e.label_type)]
            edict[e.experimentalnum].append(revalidate_flavorcoat_properties(e))
    return edict
            
#@reversion.create_revision()       
def revalidate_flavorcoat_properties(e):
    e.dry = False
    e.spraydried = False
    e.liquid = False
    e.oilsoluble = False
    e.concentrate = False
    e.flavorcoat = True
    e.label_type = e.get_label_type()
    e.natart = e.get_natart()
    #e.save()
    
    return "%s %s %s" % (e.natart, e.product_name, e.label_type)
    #reversion.set_comment("Flavorcoat detected.")
    #e.save()