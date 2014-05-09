from django.core.exceptions import ValidationError

from access.models import *
from reversion import revision


#RECONCILING FLAVOR SPECS

@revision.create_on_success
def reconcile_flavor(flavor, user, scraped_data_json):
    rf = ReconciledFlavor(
                          flavor = flavor,
                          reconciled = True,
                          scraped_data = scraped_data_json,
                          reconciled_by = user
                          )
    rf.save()
    
def reconcile_update(flavor, user, scraped_data_json):
    rf = ReconciledFlavor.objects.get(flavor = flavor)
    rf.reconciled_by = user
    rf.scraped_data = scraped_data_json
    rf.save()


#ACTIVATING/DISCONTINUING RAW MATERIALS

def discontinue_ingredient(ingredient):
    ingredient.discontinued = True
    ingredient.save()
    
def activate_ingredient(ingredient):
    ingredient.discontinued = False
    ingredient.save()
    
def replace_ingredient_foreignkeys(new_ingredient):
    
    for lw in LeafWeight.objects.filter(ingredient__id=new_ingredient.id):
        lw.ingredient = new_ingredient
        lw.save()
        
    for formula in Formula.objects.filter(ingredient__id=new_ingredient.id):
        formula.ingredient=new_ingredient
        formula.save()
        
    for ft in FormulaTree.objects.filter(node_ingredient__id=new_ingredient.id):
        ft.node_ingredient=new_ingredient
        ft.save()  


def update_prices_and_get_updated_flavors(old_ingredient, new_ingredient): 
    
    
    #find all flavors that contain the raw material
    updated_flavors = []
    for lw in LeafWeight.objects.filter(ingredient=new_ingredient):
        
        
        root_flavor = lw.root_flavor
        old_total = root_flavor.rawmaterialcost
        
        
        #new_total = old_total - old_unit_price * weight/1000 + new_unit_price * weight/1000
        new_total = old_total + lw.weight/1000 * (new_ingredient.unitprice - old_ingredient.unitprice)
        root_flavor.rawmaterialcost = new_total  #overwrite and save the new total rawmaterialcost
        root_flavor.save()
        
        price_change = new_total - old_total
        
               
        updated_flavors.append((root_flavor, lw.weight, old_total, new_total, price_change))

    return updated_flavors

def experimental_approve_from_form(approve_form, experimental):
    approve_form.save()
    new_flavor = approve_form.instance
    experimental.product_number = new_flavor.number
    experimental.save()
    gazintas = Ingredient.objects.filter(sub_flavor=new_flavor)
    if gazintas.count() > 1:
        # hack job. this will raise exception because get() expects 1
        Ingredient.objects.get(sub_flavor=new_flavor)
    if gazintas.count() == 1:
        gazinta = gazintas[0]
        gazinta.prefix = "%s-%s" % (new_flavor.prefix, new_flavor.number)
        gazinta.flavornum = new_flavor.number
        gazinta.save()
    for ft in FormulaTree.objects.filter(root_flavor=new_flavor).exclude(node_flavor=None).exclude(node_flavor=new_flavor).filter(node_flavor__prefix="EX"):
        ft.node_flavor.prefix="GZ"
        ft.node_flavor.save()
        