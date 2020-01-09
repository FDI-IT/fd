from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from itertools import chain

from django.db.models import Q, F

from access.models import *

flavor_fields_to_migrate = [
        'id',
        'number',
        'solvent',
        'name',
        'prefix',
        'code',
        'natart',
        'label_type',
        'categoryid',
        'unitprice',
        'quantityperunit',
        'supplierid',
        'unitsinstock',
        'unitsonorder',
        'reorderlevel',
        'discontinued',
        'approved',
        'no_pg',
        'productmemo',
        'sold',
        'spraydried',
        'lastprice',
        'experimental',
        'lastspdate',
        'rawmaterialcost',
        'valid',        
    ]

psi_fields_to_migrate = [
        'flashpoint',
        'kosher',
        'solubility',
        'stability',
        'nutri_on_file',
        'flammability',
        'allergen',
        'yield_field',
        'pinnumber',
        'kosher_id',
        'label_check',
        'vaporpressure',
        'reactionextraction',
        'prop_65',
        'gmo',
        'ccp1',
        'ccp2',
        'ccp3',
        'ccp4',
        'ccp5',
        'ccp6',
        'haccp',
        'batfno',
        'microtest',
        'crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sulfites',
        'organic',
        'diacetyl',
        'entered',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
    ]

formula_fields_to_migrate = [
        'acc_flavor',
        'acc_ingredient',
        'flavor__number',
        'ingredient_id',
        'amount',
        'totalweight',
        'flavorextendedprice',
        'price',
        'discontinued',
        'batchamount',
        'machinebatch',
        'rawmaterialcode',
    ]

#experimental_fields_to_migrate = [
#        'experimentalnum',
#        'datesent',
#        'customer',
#        'product_name',
#        'initials',
#        'memo',
#        'liquid',
#        'dry'
#    ]

def instantiate_psis():
    n = datetime.now()
    for f in Flavor.objects.all():
        try:
            psi = f.productspecialinformation
        except ProductSpecialInformation.DoesNotExist:
            f.productspecialinformation = ProductSpecialInformation(flavornumber=f.number,
                                                                    productid=f.pk,
                                                                    flavor=f, entered=n)
            f.productspecialinformation.save()
            f.save()

def instantiate_integrated_product_objects():
    IntegratedProduct.objects.all().delete()
    for f in Flavor.objects.all():
        
        ip = IntegratedProduct()
        for field in flavor_fields_to_migrate:
            setattr(ip, field, getattr(f, field))
            
        try:
            psi = f.productspecialinformation
            for field in psi_fields_to_migrate:
                setattr(ip, field, getattr(psi, field))
        except ProductSpecialInformation.DoesNotExist:
            print(f)
        ip.save()
        
def instantiate_formula_objects():
    IntegratedFormula.objects.all().delete()
    for f in Formula.objects.all().values(*formula_fields_to_migrate):
        int_for = IntegratedFormula()
        int_for.flavor = IntegratedProduct.objects.get(number=f['flavor__number'])
        del(f['flavor__number'])
        for field in list(f.keys()):
            setattr(int_for, field, f[field])
        int_for.save()


flavor_table_view = """
CREATE VIEW access_integratedflavor AS
SELECT
    ip.id as "ProductID",
    ip.number as "FlavorNumber",
    ip.solvent as "Solvent",
    ip.name as "ProductName",
    ip.prefix as "ProductPrefix",
    ip.code as "FlavorCode",
    ip.natart as "FlavorNatArt",
    ip.type as "FlavorType",
    ip.categoryid as "CategoryID",
    ip.unitprice as "UnitPrice",
    ip.quantityperunit as "QuantityPerUnit",
    ip.supplierid as "SupplierID",
    ip.unitsinstock as "UnitsInStock",
    ip.unitsonorder as "UnitsOnOrder",
    ip.reorderlevel as "ReorderLevel",
    ip.discontinued as "Discontinued",
    ip.approved as "Approved",
    ip.productmemo as "ProductMemo",
    ip.sold as "Sold",
    ip.spraydried as "SprayDried",
    ip.lastprice as "LastPrice",
    ip.experimental as "Experimental",
    ip.lastspdate as "LastSPDate"
FROM
    access_integratedproduct as ip;
"""

psi_table_select = """
CREATE VIEW access_integratedpsi AS
SELECT
    ip.number as "FlavorNumber",
    ip.id as "ProductID",
    ip.flashpoint as "FlashPoint",
    ip.kosher as "Kosher",
    ip.solubility as "Solubility",
    ip.stability as "Stability",
    ip.nutri_on_file as "Nutri On File",
    ip.flammability as "Flammability",
    ip.allergen as "Allergen",
    ip.yield_field as "Yield",
    ip.pinnumber as "PINNumber",
    ip.kosher_id as "Kosher_ID",
    ip.label_check as "Label_Check",
    ip.vaporpressure as "VaporPressure",
    ip.reactionextraction as "ReactionExtraction",
    ip.prop_65 as "PROP 65",
    ip.gmo as "GMO",
    ip.ccp1 as "CCP1",
    ip.ccp2 as "CCP2",
    ip.ccp3 as "CCP3",
    ip.ccp4 as "CCP4",
    ip.ccp5 as "CCP5",
    ip.ccp6 as "CCP6",
    ip.haccp as "HACCP",
    ip.batfno as "BATFNo",
    ip.microtest as "MicroTest",
    ip.crustacean as "Crustacean",
    ip.eggs as "Eggs",
    ip.fish as "Fish",
    ip.milk as "Milk",
    ip.peanuts as "Peanuts",
    ip.soybeans as "Soybeans",
    ip.treenuts as "TreeNuts",
    ip.wheat as "Wheat",
    ip.sulfites as "Sulfites",
    ip.organic as "Organic",
    ip.diacetyl as "Diacetyl",
    ip.entered as "Entered"
FROM
    access_integratedproduct as ip;
"""

formula_table_select = """
CREATE VIEW access_integratedformula AS
SELECT
    ip.acc_flavor as "FlavorNumber",
    ip.acc_ingredient as "ProductID",
    ip.amount as "FlavorAmount",
    ip.totalweight as "TotalWeight",
    ip.flavorextendedprice as "FlavorExtendedPrice",
    ip.price as "Price",
    ip.discontinued as "Discontinued",
    ip.batchamount as "BatchAmount",
    ip.machinebatch as "MachineBatch",
    ip.rawmaterialcode as "RawMaterialCode"
FROM
    access_integratedformula as ip;
"""

change_owners = """
ALTER VIEW access_integratedflavor OWNER TO "www-data";
ALTER VIEW access_integratedpsi OWNER TO "www-data";
ALTER VIEW access_integratedformula OWNER TO "www-data";
"""

flavor_numbers = list(set(LeafWeight.objects.all().values_list('root_flavor__number',flat=True)))
formula_numbers = list(set(Formula.objects.all().values_list('flavor__number',flat=True)))



def dictify_my_formula(f):
    d = {}
    for element in list(f.formula_set.all().values()):
        d[element['id']] = element
    return d

def dictify_formulae_by_number(flavor_qs = Flavor.objects.all()):
    formula_dict = {}
    for fn in formula_numbers:
        f = flavor_qs.get(number=fn)
        formula_dict[fn] = dictify_my_formula(f)
    return formula_dict
        

def dictify_my_flavor(f):
    """Takes a list of two tuples and returns a defaultdict with
    the zeroth element as as key and first as value.
    """
    d = {}
    for element in f.leaf_weights.all().values_list('ingredient__id','quant_weight'):
        d[element[0]] = element[1] 
    return d

def dictify_flavors_by_number(flavor_qs = Flavor.objects.all()):
    flavor_dict = {}
    for fn in flavor_numbers:
        f = flavor_qs.get(number=fn)
        flavor_dict[fn] = dictify_my_flavor(f)
    return flavor_dict
        
def get_gazinta_index():
    gazintas = {}
    for i in Ingredient.objects.exclude(sub_flavor=None):
        gazintas[i.pk] = i.sub_flavor
    return gazintas

formulae = dictify_formulae_by_number()
gazinta_index = get_gazinta_index()
    
def jaccard_index(a,b):
    intersection_cardinality = 0
    union_cardinality = 0
    for k in a:
        if k not in b:
            union_cardinality += a[k]
        else:
            a_amt = a[k]
            b_amt = b[k]
            if a_amt == b_amt:
                intersection_cardinality += b_amt
                union_cardinality += b_amt
            elif a_amt > b_amt:
                intersection_cardinality += b_amt
                union_cardinality += a_amt
            else:
                intersection_cardinality += a_amt
                union_cardinality += b_amt
    for k in b:
        if k not in a:
            union_cardinality += b[k]
    return float(intersection_cardinality)/union_cardinality

def test_ji_batch(flavor_dict, batch_size=100000,threshold=0.9, ji_func=jaccard_index):
    count=0    
    for x in range(0,len(flavor_numbers)):
        print(x)
        for y in range(x+1,len(flavor_numbers)):
            if count > batch_size:
                return
            else:
                count+=1
            ji = ji_func(flavor_dict[flavor_numbers[x]],flavor_dict[flavor_numbers[y]])
            if ji > threshold:
                print("%s, %s" % (flavor_numbers[x],flavor_numbers[y]))


def test_ji_all(flavor_dict,threshold=0.9):
    for x in range(0,len(flavor_numbers)):
        print(x)
        for y in range(x+1,len(flavor_numbers)):
            ji = jaccard_index(flavor_dict[flavor_numbers[x]],flavor_dict[flavor_numbers[y]])
            if ji > threshold:
                print("%s, %s" % (flavor_numbers[x],flavor_numbers[y]))
                jil = JIList(a=flavor_numbers[x],
                             b=flavor_numbers[y],
                             score=ji)
                jil.save()
                
def fix_jil_order():
    for jil in JIList.objects.all():
        if jil.a >= 20000 and jil.a < 30000:
            if jil.b < 20000 or jil.b > 30000:
                new_b = jil.a
                jil.a = jil.b
                jil.b = new_b
                jil.save()
                
def jil_dictify():
    jil_dict = defaultdict(list)
    for jil in JIList.objects.filter(score=1):
        jil_dict[jil.a].append(jil.b)
    return jil_dict

def jil_key_order(jil_dict):
    key_list = sorted(jil_dict.keys())
    a=[];b=[];c=[];
    for k in key_list:
        if k < 20000:
            a.append(k)
        elif k < 30000:
            c.append(k)
        else:
            b.append(k)

    return a+b+c

def jil_master_select(key_order,jil_dict):
    master_dict = {}
    for k in key_order:
        this_master = master_dict.get(k,k)
        for flavor_number in jil_dict[k]:
            if flavor_number not in master_dict:
                master_dict[flavor_number] = this_master
    return master_dict

#use frozen sets
def jil_setify():
    jild = {}
    for jil in JIList.objects.filter(score=1):
        a = jil.a; b = jil.b;
        if a in jild:
            s = set()
            jild[a] = frozenset(chain(set(jild[a]),[b]))
            jild[b] = jild[a]
        else:
            jild[a] = frozenset([a,b])
            jild[b] = jild[a]        
    return jild

def analyze_jild(jils=jil_setify()):
    weird_combos = []
    unique_combos = set(jils.values())
    for s in unique_combos:
        x_test = False
        for elem in s:
            if elem < 20000 or elem >= 30000:
                x_test = True
                break
        if not x_test:
            weird_combos.append(s)
            
    return weird_combos
