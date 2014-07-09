from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from itertools import chain

from django.db import transaction
from django.db.models import Q, F

from access.models import *
from newqc.models import *

flavor_fields_to_migrate = [
        'id',
        'number',
        'solvent',
        'name',
        'prefix',
        'code',
        'natart',
        'type',
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
            print f
        ip.save()
        
def instantiate_formula_objects():
    IntegratedFormula.objects.all().delete()
    for f in Formula.objects.all().values(*formula_fields_to_migrate):
        int_for = IntegratedFormula()
        int_for.flavor = IntegratedProduct.objects.get(number=f['flavor__number'])
        del(f['flavor__number'])
        for field in f.keys():
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

def dictify_my_flavor(f):
    """Takes a list of two tuples and returns a defaultdict with
    the zeroth element as as key and first as value.
    """
    d = {}
    for element in f.leaf_weights.all().values_list('ingredient__id','weight'):
        d[element[0]] = element[1] 
    return d

def dictify_flavors_by_number():
    flavor_dict = {}
    for f in Flavor.objects.all():
        flavor_dict[f.number] = dictify_my_flavor(f)
    return flavor_dict
        
def jaccard_index(a,b):
    intersection_cardinality = Decimal('0')
    union_cardinality = Decimal('0')
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
    print intersection_cardinality
    return intersection_cardinality/union_cardinality

def test_ji_batch(flavor_dict, batch_size=100000,threshold=0.9, ji_func=jaccard_index):
    count=0    
    for x in range(0,len(flavor_numbers)):
        print x
        for y in range(x+1,len(flavor_numbers)):
            if count > batch_size:
                return
            else:
                count+=1
            ji = ji_func(flavor_dict[flavor_numbers[x]],flavor_dict[flavor_numbers[y]])
            if ji > threshold:
                print "%s, %s" % (flavor_numbers[x],flavor_numbers[y])


def test_ji_all(flavor_dict,threshold=Decimal('0.9')):
    JIList.objects.all().delete()
    for x in range(0,len(flavor_numbers)):
        for y in range(x+1,len(flavor_numbers)):
            print "ji = jaccard_index(flavor_dict[flavor_numbers[x]],flavor_dict[flavor_numbers[y]])"
            print flavor_dict[flavor_numbers[x]]
            print flavor_numbers[y]
            print flavor_dict[flavor_numbers[y]]
            print
            ji = jaccard_index(flavor_dict[flavor_numbers[x]],flavor_dict[flavor_numbers[y]])
            if ji > threshold:
                print "%s, %s" % (flavor_numbers[x],flavor_numbers[y])
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
    
    for k,v in jild.iteritems():
        c = len(v);biggest_set=v
        for x in v:
            if c < len(jild[x]):
                c= len(jild[x])
                biggest_set=jild[x]
        for x in v:
            jild[x]=biggest_set
            
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

def populate_renumbers(jils=jil_setify()):
    Renumber.objects.all().delete()
    for k,v in jils.iteritems():
        a = Flavor.objects.get(number=k)
        for num in v:
            if v == k:
                continue
            b = Flavor.objects.get(number=num)
            r = Renumber(a=a,b=b)
            r.save()
    for r in Renumber.objects.all():
        if r.a == r.b:
            r.delete()
            
def lotted_flavors():
    return set(Lot.objects.all().order_by('pk').values_list('flavor',flat=True))
            
def sold_gazintas(lotted_flavors):
    return set(FormulaTree.objects.filter(
                root_flavor__in=lotted_flavors).exclude(
                node_flavor=None).values_list(
                'node_flavor',flat=True))

@transaction.commit_manually
def unapprove_unsell_flavors():
    for f in Flavor.objects.filter(approved=True):
        print f
        f.approved = False
        f.sold = False
        f.save()
    for f in Flavor.objects.filter(sold=True):
        print f
        f.approved=False
        f.sold=False
        f.save()
    transaction.commit()

def expand_search_area():
    sgs = sold_gazintas(lotted_flavors())
    sold_plus_renumbers = set()
    for sg in sgs:
        f= Flavor.objects.get(pk=sg)
        sold_plus_renumbers = sold_plus_renumbers.union(set(f.loaded_renumber_list))
    sold_plus_renumbers = sold_plus_renumbers.union(lotted_flavors())
    return sold_plus_renumbers    

@transaction.commit_manually
def approve_sold_flavors(sold_plus_renumbers):
    for fpk in sold_plus_renumbers:
        f = Flavor.objects.get(pk=fpk)
        f.approved=True
        f.sold = True
        f.save()
    transaction.commit()
    
def reset_approved_flavors():
    unapprove_unsell_flavors()
    sold_plus_renumbers = expand_search_area()
    approve_sold_flavors(sold_plus_renumbers)
    
@transaction.commit_manually
def fix_microsensitive():
    sensitive_set = set([
         u'Senstive',
         u'Sensitive',
         u'True',
         u'Yes',])
    for i in Ingredient.objects.all():
        if i.microsensitive in sensitive_set:
            i.microsensitive = "MICROSENSITIVE"
            i.save()
        else:
            i.microsensitive = "Not sensitive"
            i.save()
    transaction.commit()

@transaction.commit_manually
def set_rag_pending():
    for f in Flavor.objects.all():
        print f
        f.risk_assessment_group = 7
        f.risk_assessment_memo = "Reset for audit"
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_antimicrobial():
    #vanilla
    for lw in LeafWeight.objects.filter(ingredient__id__in=[852,853]).filter(weight__gte=357).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group=0
        f.risk_assessment_memo = "Contains 35.7% Vanilla Extract (12.5% ETOH)"
        f.save()
    
    print 'pg'
    # PG
    for lw in LeafWeight.objects.filter(ingredient__id=703).filter(weight__gte=200).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group=0
        f.risk_assessment_memo = "Contains 20% PG"
        f.save()
        
    print 'ethyl'
    #ethyl
    for lw in LeafWeight.objects.filter(ingredient__id=321).filter(weight__gte=125).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group=0
        f.risk_assessment_memo = "Contains 12.5% ETOH"
        f.save()
        
    print 'denatured'
    #denatured
    for lw in LeafWeight.objects.filter(ingredient__id=5121).filter(weight__gte='131.25').select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group=0
        f.risk_assessment_memo = "Contains 12.5% ETOH"
        f.save()
    
    print 'triacetin'
    #triacetin
    for lw in LeafWeight.objects.filter(ingredient__id=829).filter(weight__gte=750).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group=0
        f.risk_assessment_memo = "Contains 75% Triacetin"
        f.save()
        
    transaction.commit()
    
@transaction.commit_manually
def set_coa_monitored():
    for lw in LeafWeight.objects.filter(ingredient__microsensitive='MICROSENSITIVE').select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group = 5
        f.risk_assessment_memo = "Contains microsensitive ingredients."
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_bacteriostatic():
    
    for lw in LeafWeight.objects.filter(ingredient__id=750).filter(weight__gte=1).select_related():
        f= lw.root_flavor
        print f
        f.risk_assessment_group = 2
        f.risk_assessment_memo = "Contains 0.1% Sodium Benzoate."
        f.save()
        
    for lw in LeafWeight.objects.filter(ingredient__id=898).filter(weight__gte=4).select_related():
        f= lw.root_flavor
        print f
        f.risk_assessment_group = 2
        f.risk_assessment_memo = "Contains 0.1% Sodium Benzoate."
        f.save()
        
    for lw in LeafWeight.objects.filter(ingredient__id=1003).filter(weight__gte=10).select_related():
        f= lw.root_flavor
        print f
        f.risk_assessment_group = 2
        f.risk_assessment_memo = "Contains 0.1% Sodium Benzoate."
        f.save()
    
    low_water_activity_list = [
        758,6403,5928,1983,829,743,639,134,25,315,316,325,326,23,24,643,1031,
        353,352,1937,82,83,582,1835,214,641,90
    ]    
    for lw in LeafWeight.objects.filter(ingredient__id__in=low_water_activity_list).filter(weight__gte=160).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group = 2
        f.risk_assessment_memo = "Contains Oil Soluble chemicals--low water activity."
        f.save()
        
    sugar_list = [
        1432,1478,782              
    ]
    for lw in LeafWeight.objects.filter(ingredient__id__in=sugar_list).filter(weight__gte=667).select_related():
        f = lw.root_flavor
        print f
        f.risk_assessment_group = 2
        f.risk_assessment_memo = "Contains concentrated dissolved solids--low water activity."
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_hot_packed():
    for f in Flavor.objects.filter(number__in=[111232,]):
        print f
        f.risk_assessment_group = 3
        f.risk_assessment_memo = "Heated to 212F for extended period."
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_spraydried():
    for f in Flavor.objects.filter(spraydried=True):
        print f
        f.risk_assessment_group = 6
        f.risk_assessment_memo = "Spray dried."
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_regularly_monitored_list():
    for f in Flavor.objects.filter(number__in=[2739,80983,7574,90273,1732,7650,2826,170606,60749]):
        print f
        f.risk_assessment_group = 1
        f.risk_assessment_memo = "On the list of regularly monitored flavors, per customer request."
        f.save()
    transaction.commit()
    
@transaction.commit_manually
def set_intermediate_only():
    lf = lotted_flavors()
    for f in Flavor.objects.filter(risk_assessment_group=7).filter(approved=True):
        if f.pk not in lf:
            f.risk_assessment_group=8
            f.save()
    transaction.commit()

def reset_risk_assessment_group():
    set_rag_pending()
    set_coa_monitored()
    set_bacteriostatic()
    set_antimicrobial()
    set_hot_packed()
    set_spraydried()
    set_regularly_monitored_list()
    set_intermediate_only()