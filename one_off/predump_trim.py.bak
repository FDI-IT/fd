from access.models import *
from newqc.models import *
from solutionfixer.models import *
from unified_adapter.models import *
from reversion.models import *
from haccp.models import *
from salesorders.models import *
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
     
def delete_unified_adapter_models():
    for pi in ProductInfo.objects.all():
        pi.delete()     


#keep only the most recent 10 lots per flavor
def trim_lots():
    for fl in Flavor.objects.all():
        for lot in fl.lot_set.all()[10:]:
            print "Deleting lot %s" % lot
            lot.delete()

#only keep 10 digitized formula per experimental log
def trim_digitizedformulas():
    for el in ExperimentalLog.objects.all():
        for df in el.digitizedformula_set.all()[10:]:
            df.delete()
            
#delete all salesordernumbers with no line items
def trim_salesordernumbers():
    for son in SalesOrderNumber.objects.all():
        if son.lineitem_set.count() == 0:
            son.delete()
            
#delete all customers who don't have any salesorders
def trim_customers():
    for c in Customer.objects.all():
        if c.salesordernumber_set.count() == 0:
            c.delete()

#this deletes all retains that have foreign keys to importretains as well
def delete_importretains():
    ImportRetain.objects.all().delete()
    
#this deletes all rmretains that have foreign keys to rmimportretains
def delete_rmimportretains():
    RMImportRetain.objects.all().delete()
    
def delete_revisions():
    Revision.objects.all().delete()
    
def delete_legacypurchases():
    LegacyPurchase.objects.all().delete()
    
def delete_receivinglogs():
    ReceivingLog.objects.all().delete()

def delete_watertests():
    WaterTest.objects.all().delete()

def trim_database():
    most_made_flavors = find_most_made_flavors()
    save_flavors = add_some_invalid_flavors(most_made_flavors)
    complete_flavor_numbers, complete_ingredient_ids = get_complete_flavors_and_ingredients(save_flavors)
    
    delete_other_ingredients(complete_ingredient_ids)
    delete_other_flavors(complete_flavor_numbers)
        
    trim_experimental_logs()
    trim_purchase_orders()

    JIList.objects.all().delete()
    
    #if you want to keep any of the stuff below (for testing purposes) just comment them out
    delete_importretains()
    delete_rmimportretains()
    delete_legacypurchases()
    delete_revisions()
    delete_receivinglogs()
    delete_watertests()

    trim_lots()
    trim_digitizedformulas()
    trim_salesordernumbers()
    trim_customers()
    
if __name__ == "__main__":
    trim_database()
