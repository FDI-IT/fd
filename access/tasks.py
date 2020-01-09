import reversion

from access.models import Ingredient, Formula, LeafWeight
from access.scratch import recalculate_flavor

from celery.task import task, Task
import reversion
#@task()



@reversion.create_revision()
def ingredient_replacer_formula(formula_row, new_ingredient):
    reversion.set_comment("Replaced PIN# %s with PIN# %s" % (formula_row.ingredient.id, new_ingredient.id)) 
    formula_row.acc_ingredient = new_ingredient.id
    formula_row.ingredient = new_ingredient    
    formula_row.save()
    formula_row.flavor.save()

@task()
def ingredient_replacer_guts(old_ingredient, new_ingredient):
    for formula_row in Formula.objects.filter(ingredient=old_ingredient):
        ingredient_replacer_formula(formula_row, new_ingredient)
        
    seen_set = set()
    for lw in LeafWeight.objects.filter(ingredient=old_ingredient):
        if lw.root_flavor not in seen_set:
            recalculate_flavor(lw.root_flavor)
            seen_set.add(lw.root_flavor)
    
    return