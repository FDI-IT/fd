from django.core.exceptions import ValidationError

# import reversion
import reversion
from django.db import connection
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal

from datetime import datetime
from dateutil.relativedelta import relativedelta

from access.models import Flavor, Company, Supplier, Manufacturer, ReconciledFlavor, LeafWeight, Formula, FormulaTree
from access.scratch import recalculate_guts

def update_sold_field():
    threeyearsago = datetime.now().date() - relativedelta(years=3)

    false_to_true = 0
    true_to_false = 0
    unchanged = 0

    for fl in Flavor.objects.all():
        if fl.lot_set.exists() and fl.lot_set.all()[0].date >= threeyearsago:
            if fl.sold == False:
                fl.sold = True
                fl.save()
                false_to_true += 1
            else:
                unchanged += 1
        else:
            if fl.sold == True:
                fl.sold = False
                fl.save()
                true_to_false += 1
            else:
                unchanged += 1

        print "False to True: %s" % false_to_true
        print "True to False: %s" % true_to_false
        print "Unchanged: %s" % unchanged

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
        'DELETE FROM access_jilist WHERE a=$1;
        INSERT INTO access_jilist(a, b, score) SELECT $1, "access_integratedproduct"."number", jaccard_index($1, "access_integratedproduct"."number") FROM "access_integratedproduct" WHERE NOT ("access_integratedproduct"."number" = $1);
        DELETE FROM access_jilist WHERE a=$1 and id NOT IN (SELECT id FROM access_jilist WHERE a=$1 ORDER BY -score LIMIT 100);'

        LANGUAGE SQL
        RETURNS NULL ON NULL INPUT;

        """
        )


    cursor.execute('COMMIT')

#    Using UPDATE slows down execution time exponentially as each flavor is processed
#
#         CREATE FUNCTION jilist_update(integer) RETURNS VOID AS
#         'UPDATE access_jilist SET score = jaccard_index($1, "access_integratedproduct"."number") FROM "access_integratedproduct" WHERE a = $1 AND b = "access_integratedproduct"."number" OR a = "access_integratedproduct"."number" AND b = $1;
#         INSERT INTO access_jilist(a, b, score) SELECT $1, "access_integratedproduct"."number", jaccard_index($1, "access_integratedproduct"."number") FROM "access_integratedproduct" WHERE NOT ("access_integratedproduct"."number" = $1) AND NOT EXISTS (SELECT 1 FROM access_jilist WHERE a = $1 AND b = "access_integratedproduct"."number" OR a = "access_integratedproduct"."number" AND b = $1);'
#         LANGUAGE SQL
#         RETURNS NULL ON NULL INPUT;


def ji_update(flavor_num):
    cursor = connection.cursor()
    cursor.execute('select jilist_update(%s)' % flavor_num)  #doesn't actually save the objects
    cursor.execute('COMMIT')
#     #have to go through all the 'temporary' objects and save them
#    for ji in JIList.objects.filter(Q(a=10481) | Q(b=10481)):
#        ji.save()



#RECONCILING FLAVOR SPECS

@reversion.create_revision()
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

#use this when replacing a raw material with one with a different id (a totally different raw material)
def replace_raw_material(old_ingredient, new_ingredient):

    changed_flavor_list = []

    for lw in LeafWeight.objects.filter(ingredient=old_ingredient):
        lw.ingredient = new_ingredient
        lw.save()
        changed_flavor_list.append(lw.root_flavor)

    for formula in Formula.objects.filter(ingredient=old_ingredient):
        formula.ingredient=new_ingredient
        formula.save()

    for ft in FormulaTree.objects.filter(node_ingredient=old_ingredient):
        ft.node_ingredient=new_ingredient
        ft.save()

    with reversion.create_revision():
        for fl in changed_flavor_list:
            fl.save()

        reversion.set_comment("RM Replacement: %s => %s" % (old_ingredient, new_ingredient))
        reversion.set_user(User.objects.get(username='matta'))


#replace a raw material in a certain flavor
def replace_raw_material_in_flavor(old_ingredient,new_ingredient,flavor):
    for fl in flavor.gazintas():
        replace_raw_material_in_flavor(old_ingredient,new_ingredient,fl)

    if Formula.objects.filter(flavor=flavor,ingredient=old_ingredient).exists():
        print "Replacing %s in flavor %s" % (old_ingredient, flavor)

        try:
            formula = Formula.objects.get(flavor=flavor,ingredient=old_ingredient)
        except:
            flavor.consolidate_formula()
            formula = Formula.objects.get(flavor=flavor, ingredient=old_ingredient)

        formula.ingredient = new_ingredient
        formula.save()

    recalculate_guts(flavor)


def recalculate_ingredient_gzl(ingredient):
    for gzl_product in ingredient.gzl_traversal():
        try:
            recalculate_guts(gzl_product[0])
            print "Flavor %s - Recalculated" % gzl_product[0]
        except:
            print "Could not recalculate flavor %s." % gzl_product[0]


# def replace_ingredient_foreignkeys(new_ingredient):
#
#     for lw in LeafWeight.objects.filter(ingredient__id=new_ingredient.id):
#         lw.ingredient = new_ingredient
#         lw.save()
#
#     for formula in Formula.objects.filter(ingredient__id=new_ingredient.id):
#         formula.ingredient=new_ingredient
#         formula.save()
#
#     for ft in FormulaTree.objects.filter(node_ingredient__id=new_ingredient.id):
#         ft.node_ingredient=new_ingredient
#         ft.save()
#
#
# def update_prices_and_get_updated_flavors(old_ingredient, new_ingredient):
#
#
#     #find all flavors that contain the raw material
#     updated_flavors = []
#     for lw in LeafWeight.objects.filter(ingredient=new_ingredient):
#
#
#         root_flavor = lw.root_flavor
#         old_total = root_flavor.rawmaterialcost
#
#
#         #new_total = old_total - old_unit_price * weight/1000 + new_unit_price * weight/1000
#         new_total = old_total + lw.weight/1000 * (new_ingredient.unitprice - old_ingredient.unitprice)
#         root_flavor.rawmaterialcost = new_total  #overwrite and save the new total rawmaterialcost
#         root_flavor.save()
#
#         price_change = new_total - old_total
#
#
#         updated_flavors.append((root_flavor, lw.weight, old_total, new_total, price_change))
#
#     return updated_flavors

def replace_oc_with_organic_compliant():
    changed_flavors = []
    for fl in Flavor.objects.filter(label_type__contains='OC').exclude(label_type__contains='OCERT').exclude(label_type__contains='OCOMP'):
        fl.label_type = fl.label_type.replace('OC','OCOMP')
        fl.save()
        changed_flavors.append(fl)
        return changed_flavors

def replace_ocert_with_ocomp():
    changed_flavors = []
    for fl in Flavor.objects.filter(label_type__contains='OCERT'):
        fl.label_type = fl.label_type.replace('OCERT','OCOMP')
        fl.save()
        changed_flavors.append(fl)
        return changed_flavors

# dictionary of suppliers and possible manufacturers
# value == 1 means the manufacturer is the same as the supplier
supplier_to_manufacturer = {
    'ABT' : 1,
    'Brenntag Northeast' : ['ADM', 'Dow', 'IOI Oleo'],
    'Ajinomoto' : 1,
    'Aldrich' : 1,
    'Alfrebro' : 1,
    'Todd' : 1,
    'Ariake' : 1,
    'Balchem' : 1,
    'Bedoukian' : 1,
    'Bell' : 1,
    'Berje' : 1,
    'BioSpringer' : 1,
    'C and A' : 1,
    'Cargill' : 1,
    'Diana Vegetal' : 1,
    'Atla' : ['Domino', 'Royal', 'United', 'Ingredion', 'T&L', 'Wego'],
    'Dempsey': ['DSM'],
    'Elan' : 1,
    'FLE' : 1,
    'Frutarom' : 1,
    'Del Val' : ['IIS'],
    'Penta' : 1,
    'Phoenix' : 1,
    'Brenntag Specialties' : ['PPG Silica'],
    'Schiff' : 1,
    'Sethness' : 1,
    'Axel' : ['Tongliao Meihua'],
    'Tril' : 1,
    'Vigon' : 1,
    'Welch Holme and Clarke' : 1,
    'Essex Grain' : ['Ingredion', 'T&L', 'Cargill', 'ADM', 'GPC',
                     'Domino', 'Morton', 'Lall', 'Citrique'],
    'Franklin Farms' : ['Franklin Farms', 'Leprino'],
    'Golden Peanut' : 1,
    'Henn' : 1,
    'Horner': 1,
    'Hunt' : ["Land O'Lakes"],
    'IFF' : 1,
    'Importer Services Corp.' : 1,
    'Ingredient Connections' : ['Agusa'],
    'International' : ['Greenwood'],
    'Jedwards' : 1,
    'Kalsec' : 1,
    'KER' : 1,
    'Lall' : 1,
    'Mafco' : 1,
    'Malt' : ["Int'l Molasses",],
    'MAST': ['KER'],
    'Mayer' : 1,
    'Mitsui' : ['FruitSmart'],
    'Natural Adv' : 1,
    #'Natural' : 1,
    'Nikken': 1,
    'PridSol' : ['PridSol', 'Oleon', 'Sasma'],
    'Prime' : 1,
    'Prinova' : ['Prinova', 'Emerald', 'Fujian Renhong',],
    'Red Arrow' : ['KER'],
    'Robertet' : 1,
    'Ryan' : ['Hengtong', 'Bayas del Sur', 'Grundewald'],
    'Savory Systems' : ['Brookside',],
    'ScanAmerican' : 1,
    'Sensient' : 1,
    'Sparrow' : ['Cargill'],
    'SunOpta' : ['J Rettenmaier',],
    'Tilley' : ['Dow', 'ADM', 'T&L', 'Emerald', 'Eastman', 'Niacet'],
    'YOST' : ['Bluegrass'],
}


manufacturer_code_to_name_dict = {
    'ADM':'ADM',
    'Dow':'Dow',
    'IOI Oleo': 'IOI Oleochemical',
    'Domino': 'Domino Foods',
    'Royal': 'Royal Sugar',
    'United': 'United Sugars Corporation',
    'Ingredion': 'Ingredion Incorporated',
    'T&L': 'Tate & Lyle Sugars',
    'Wego': 'Wego Chemical & Mineral Corporation',
    'DSM': 'DSM',
    'IIS': 'International Ingredient Solutions',
    'PPG Silica': 'PPG Silica',
    'Tongliao Meihua': 'Tongliao Meihua Biological Sci-tech',
    'GPC': 'Grain Processing Corporation',
    'Morton': 'Morton Salt',
    #'Lallemand': 'Lallemand Inc',
    'Citrique': 'Citrique Belge',
    #'Cargill': 'Cargill Flavor Systems US, LLC',
    'Leprino' : 'Leprino Foods',
    "Land O'Lakes" : "Land O'Lakes",
    'Agusa' : 'Agusa',
    'FruitSmart' : 'FruitSmart',
    'Oleon' : 'Oleon',
    'Sasma' : 'Sasma',
    'Emerald' : 'Emerald',
    'Fujian Renhong' : 'Fujian Renhong Medicine Chemical Industry Co.',
    'Hengtong' : 'Hengtong Juice USA',
    'Bayas del Sur' : 'Bayas del Sur',
    'Grundewald' : 'Grunewald International',
    'Brookside' : 'Brookside Poultry Company',
    'J Rettenmaier' : 'J Rettenmaier',
    'Eastman' : 'Eastman Chemical Company',
    'Niacet' : 'Niacet',
    'Bluegrass' : 'Bluegrass Ingredients',
}

def instantiate_manufacturers():
    # Iterate through the supplier_to_manufacturer dict and create manufacturers
    for supplier_code, manufacturers in supplier_to_manufacturer.iteritems():
        print supplier_code
        if manufacturers == 1:
            company = Company.objects.get(code=supplier_code)

            # create a manufacturer with the same code/name as the supplier
            manufacturer = Manufacturer()
            manufacturer.__dict__.update(company.__dict__) # copy info from company because when you save a manufacturer object, it overwrites company data
            manufacturer.company_ptr = company
            manufacturer.save()
            manufacturer.suppliers.add(company.supplier) # add the supplier (same company) as a supplier for the manufacturer
            manufacturer.save()

            print "%s is a manufacturer for itself" % supplier_code

        else:
            supplier = Supplier.objects.get(code=supplier_code)

            for manufacturer_code in manufacturers:
                print "%s is a manufacturer for %s" % (manufacturer_code, supplier.code)

                if Manufacturer.objects.filter(code=manufacturer_code).exists():
                    manufacturer = Manufacturer.objects.get(code=manufacturer_code)

                # if the company exists but a manufacturer object hasn't been created yet, create one
                elif Company.objects.filter(code=manufacturer_code).exists():
                    company = Company.objects.get(code=manufacturer_code)
                    manufacturer = Manufacturer()
                    manufacturer.__dict__.update(company.__dict__)
                    manufacturer.company_ptr = company
                    manufacturer.save()

                # if no company exists, create a manufacturer
                else:
                    manufacturer = Manufacturer(
                        code = manufacturer_code,
                        name = manufacturer_code_to_name_dict[manufacturer_code],
                    )
                    manufacturer.save() # save to create company_ptr

                # add the supplier to the manufacturer
                manufacturer.suppliers.add(supplier)
                manufacturer.save()

                print 'manufacturer: %s , supplier: %s' % (manufacturer, supplier)

def create_supplier_from_company(company):
    s = Supplier()
    s.__dict__.update(company.__dict__)
    s.company_ptr = company
    s.save()