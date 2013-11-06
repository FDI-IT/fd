from access.models import *
from newqc.models import *
from solutionfixer.models import *
from django.db.models import Avg, Max, Min, Count

complex_flavors = set(
        [110379 , 90366, 50055, 10495, 90272, 10520, 11134, 10491, 8857, 10512, 20134, 9038, 8851, 81027, 10481, 1732, 111232, 9556] 
    )


def get_complete_flavors_and_ingredients(save_flavors):
    complete_flavor_numbers = set()
    complete_ingredient_ids = set()
    for f in save_flavors:
        print f
        flavor = Flavor.objects.get(number=f)
        complete_flavor_numbers.add(flavor.number)
        
        for ft in FormulaTree.objects.filter(root_flavor=flavor):
            if ft.node_flavor is not None:
                complete_flavor_numbers.add(ft.node_flavor.number)
            if ft.node_ingredient is not None:
                complete_ingredient_ids.add(ft.node_ingredient.id)
    
    for s in Solution.objects.all():
        if s.my_solvent is not None:
            complete_ingredient_ids.add(s.my_solvent.id)
            
    complete_ingredient_ids.update(SOLVENT_NAMES)
            
    for i in AntisepticIngredient.objects.all():
        complete_ingredient_ids.add(i.pin)
                
    return (complete_flavor_numbers, complete_ingredient_ids)

def delete_other_ingredients(complete_ingredients):
    for i in Ingredient.objects.exclude(id__in=complete_ingredients):
        print i
        for formula in i.formula_set.all():
            formula.delete()
        i.delete()
        
def delete_other_flavors(complete_flavor_numbers):
    for f in Flavor.objects.exclude(number__in=complete_flavor_numbers):
        print f
        f.delete()

def find_most_made_flavors():
    most_made_flavors = set()
    for f in Flavor.objects.annotate(Count('lot')).order_by('-lot__count')[:10]:
        most_made_flavors.add(f.number)
    return most_made_flavors

def add_some_invalid_flavors(save_flavors):
    for f in Flavor.objects.filter(valid=False).order_by('?')[:20]:
        save_flavors.add(f.number)
    return save_flavors

def trim_experimental_logs():
    c = ExperimentalLog.objects.all().count()
    
    for e in ExperimentalLog.objects.annotate(Count('digitizedformula')).order_by('digitizedformula__count')[:c-9]:
        print e
        e.delete()
        
    for e in ExperimentalLog.objects.all():
        if e.digitizedformula_set.count() > 1000:
            e.delete()

# DIGITIZED FORMULAS ARE AUTOMATICALLY DELETED
# def trim_digitized_formulas(): #run after trimming experimental logs
#     digitized_formula_ids = set()
#     
#     for e in ExperimentalLog.objects.all():
#         for d in e.digitizedformula_set.all():
#             digitized_formula_ids.add(d.id)
#             
#     for d in DigitizedFormula.objects.exclude(id__in=digitized_formula_ids):
#         print d
#         d.delete()
    

def trim_purchase_orders():
    
    c = PurchaseOrder.objects.count()
    
    for po in PurchaseOrder.objects.annotate(Count('purchaseorderlineitem')).order_by('purchaseorderlineitem__count')[:c-9]:
        print po
        po.delete()
        
def delete_jilist():
    for j in JIList.objects.all():
        print j
        j.delete()
        
def trim_database():
    most_made_flavors = find_most_made_flavors()
    save_flavors = add_some_invalid_flavors(most_made_flavors)
    complete_flavor_numbers, complete_ingredient_ids = get_complete_flavors_and_ingredients(save_flavors)
    
    delete_other_ingredients(complete_ingredient_ids)
    delete_other_flavors(complete_flavor_numbers)
        
    trim_experimental_logs()
    trim_purchase_orders()

    JIList.objects.all().delete()

if __name__ == "__main__":
    trim_database()
