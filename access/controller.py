from django.core.exceptions import ValidationError

from access.models import *
from reversion import revision
from django.db import connection
from django.db.models import Q


def ji_function_initialize():
    cursor = connection.cursor()
    cursor.execute(
        """
        DROP FUNCTION IF EXISTS jaccard_index(integer, integer);
        
        CREATE FUNCTION jaccard_index(integer, integer) RETURNS numeric AS
        'SELECT sum("intersection")/sum("union") AS "jaccard_index" FROM (SELECT leafa.ingredient_id, COALESCE(weighta, 0) AS weighta, COALESCE(weightb, 0) AS weightb, LEAST(COALESCE(weighta, 0), COALESCE(weightb, 0)) AS intersection, GREATEST(weighta, weightb) AS union FROM (SELECT "access_leafweight"."ingredient_id", "access_leafweight"."weight" AS weighta FROM "access_leafweight", "access_integratedproduct" WHERE "access_integratedproduct"."number" = $1 AND "access_leafweight"."root_flavor_id" = "access_integratedproduct"."id") AS leafa full outer join (SELECT "access_leafweight"."ingredient_id", "access_leafweight"."weight" AS weightb FROM "access_leafweight", "access_integratedproduct" WHERE "access_integratedproduct"."number" = $2 AND "access_leafweight"."root_flavor_id" = "access_integratedproduct"."id") AS leafb on ("leafa"."ingredient_id" = "leafb"."ingredient_id")) AS fulljoin;'
        LANGUAGE SQL
        STABLE
        RETURNS NULL ON NULL INPUT;                       
  
        DROP FUNCTION IF EXISTS jilist_update(integer);
        
        CREATE FUNCTION jilist_update(integer) RETURNS VOID AS
        'UPDATE access_jilist SET score = jaccard_index($1, "access_integratedproduct"."number") FROM "access_integratedproduct" WHERE a = $1 AND b = "access_integratedproduct"."number" OR a = "access_integratedproduct"."number" AND b = $1;
        INSERT INTO access_jilist(a, b, score) SELECT $1, "access_integratedproduct"."number", jaccard_index($1, "access_integratedproduct"."number") FROM "access_integratedproduct" WHERE NOT ("access_integratedproduct"."number" = $1) AND NOT EXISTS (SELECT 1 FROM access_jilist WHERE a = $1 AND b = "access_integratedproduct"."number" OR a = "access_integratedproduct"."number" AND b = $1);'
        LANGUAGE SQL
        RETURNS NULL ON NULL INPUT;
        
        """                   
        )

        
    cursor.execute('COMMIT')    





def ji_update(flavor_num):
    cursor = connection.cursor()
    cursor.execute('select jilist_update(%s)' % flavor_num)  #doesn't actually save the objects
    cursor.execute('COMMIT')
#     #have to go through all the 'temporary' objects and save them 
#    for ji in JIList.objects.filter(Q(a=10481) | Q(b=10481)):
#        ji.save()



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

