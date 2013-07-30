from reversion import revision

from access.models import Ingredient, Formula, LeafWeight
from access.scratch import recalculate_guts

from celery.task import task, Task
from reversion import revision
#@task()



@revision.create_on_success
def ingredient_replacer_formula(formula_row, new_ingredient):
    revision.comment = "Replaced PIN# %s with PIN# %s" % (formula_row.ingredient.id, new_ingredient.id) 
    formula_row.acc_ingredient = new_ingredient.id
    formula_row.ingredient = new_ingredient    
    formula_row.save()
    formula_row.flavor.save()

@task()
def ingredient_replacer_guts(old_ingredient, new_ingredient):
    for formula_row in Formula.objects.filter(ingredient=old_ingredient):
        ingredient_replacer_formula(formula_row, new_ingredient)
        
    for lw in LeafWeight.objects.filter(ingredient=old_ingredient):
        recalculate_guts(lw.root_flavor)
    
    return