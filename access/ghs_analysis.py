from access.models import Ingredient, Flavor, Formula
from hazard_calculator.models import GHSIngredient
from hazard_calculator.utils import hazard_list
from access.scratch import recalculate_guts
from random import randint

from pluggable.csv_unicode_wrappers import UnicodeWriter

from collections import defaultdict
from decimal import Decimal
from itertools import product

import pickle


def dump_pickle_sds_list():
    
    sds_list = []
    for fl in Flavor.objects.all():
        sds_list.append(fl.get_hazards)
        
    pickle.dump(sds_list, open("sds_list.p", "wb"))
    


def get_ghs_only_ingredients(path_to_destination=None):
    ghs_only = []
    
    for ghsing in GHSIngredient.objects.all():
        try:
            Ingredient.objects.filter(cas = ghsing.cas)[0]
        except:
            ghs_only.append((ghsing.cas, ghsing.name))    

    if path_to_destination == None:
        return ghs_only

    else:
        with open(path_to_destination + 'ghs_exclusive_report.csv', 'w+') as ghs_exclusive_report:
            csv_writer = UnicodeWriter(ghs_exclusive_report)
            
            write_ghs_report(csv_writer, ghs_only)
                    
                    
def get_fdi_only_ingredients(path_to_destination=None):
    fdi_only = []
    
    for ing in Ingredient.objects.all():
        try:
            GHSIngredient.objects.get(cas = ing.cas)
        except:
            fdi_only.append((ing.cas, ing.id, ing.product_name))
            
    fdi_only_with_cas = []
    for cas, pin, name in fdi_only:
        if cas != u'':
            fdi_only_with_cas.append((cas, pin, name))
                
    if path_to_destination == None:
        return fdi_only_with_cas   

    else:
        with open(path_to_destination + 'fdi_exclusive.csv', 'w+') as fdi_exclusive_report:
            csv_writer = UnicodeWriter(fdi_exclusive_report)
            
            write_fdi_report(csv_writer, fdi_only_with_cas)
            


def write_ghs_report(csv_writer, ghs_only):
    
    csv_writer.writerow([u'GHS Exclusive Ingredients'])
    csv_writer.writerow([u'CAS Number', u'Ingredient Name'])
    
    for cas, name in ghs_only:
        csv_writer.writerow([cas, name])
                
def write_fdi_report(csv_writer, fdi_only):
    
    csv_writer.writerow([u'FDI Exclusive Ingredients'])
    csv_writer.writerow([u'CAS Number', u'Ingredient PIN', u'Ingredient Name'])

    for cas, pin, name in fdi_only:
        csv_writer.writerow([cas, pin, name])
        
def flavors_by_hazard_count(flavor_list = Flavor.objects.filter(valid=True)):
    
    flavordict = defaultdict(list)
        
    for f in flavor_list:
        flavordict[f.get_hazard_amount()].append(f)
    
    return flavordict
    


def get_most_hazardous_flavors(amount):
    
    flavors_by_hazard_count = flavors_by_hazard_count()

    most_hazardous_flavors = []
    
    max_hazard_count = max(flavors_by_hazard_count.keys())
    
    current_hazard_count = max_hazard_count

    amount_left = amount
    
    while len(most_hazardous_flavors) < amount:
        
        #the current list of flavors being taken from
        current = flavors_by_hazard_count[current_hazard_count]
        
        if len(current) > amount_left:
            for fl in current[:amount_left]:
                most_hazardous_flavors.append(fl)
        
        else:
            amount_left = amount_left - len(current)
            for fl in current:
                most_hazardous_flavors.append(fl)
                
            current_hazard_count -= 1
                
    return most_hazardous_flavors
            
            
            
            
def show_flavor_hazards(flavor_list = Flavor.objects.filter(valid=True)):
    for fl in flavor_list:
        
        print "%s\n" % fl.name
        
        for key, val in fl.get_hazards().iteritems():
            if val != 'No':
                print "%s: %s" % (key, val)
    
        print "\n"
        


def create_hazardous_flavors(flavornum_list, min_hazards = 4, failed_dict=defaultdict(int)):
    
#     failed_dict = {0:0, 1:0, 2:0, 3:0, 4:0}
    
#     Flavor.objects.filter(name__icontains='Hazardous Flavor').delete()
#     Ingredient.objects.filter(product_name__icontains='Hazardous Ingredient').delete()
    
    Flavor.objects.filter(number__in=flavornum_list).delete()
    
    for x in flavornum_list:
        
        hazard_count = 0
        
        while True:
       
            try:
                #first iteration; flavor does not exist yet so will jump to except
                Flavor.objects.get(number=x).ingredients.all().delete() #dont really have to do this
                Flavor.objects.get(number=x).delete() 
            except:
                pass
        
            fl = Flavor(number = x,
                        name = "Hazardous Flavor %s" % x,
                        prefix = "TF",
                        natart = "N/A",
                        spg = 0,
                        risk_assessment_group = 1,
                        kosher = "Not Assigned",
                        yield_field = 100,
                        )
            
            fl.save()
            
            print "Creating %s\n" % fl.name
        
            total = 0
            used_ingredients = []
        
            while total != 1000:
                
                if total <= 900:
                    weight = 1000 - randint(total, 1000)
                else:
                    weight = 1000 - total 
                
                total = total + weight
                
                remaining_ings = GHSIngredient.objects.exclude(pk__in=used_ingredients)
                
                ghs_index = randint(0, remaining_ings.count() - 1) 
                
                ghs_ingredient = remaining_ings[ghs_index]
                
                used_ingredients.append(ghs_ingredient.pk)
                
                try:
                    ing = Ingredient.objects.get(cas = ghs_ingredient.cas)
                    
#                     print "Using ingredient %s" % ing.product_name
                    
                except:
                    ing = Ingredient(cas = ghs_ingredient.cas,
                                     product_name = "Hazardous Ingredient %s" % ghs_index,
                                     unitprice = Decimal('10.00'),
                                     sulfites_ppm = 0,
                                     package_size = Decimal('0.00'),
                                     minimum_quantity = Decimal('0.00')
                                     )
                    ing.save()
                    
#                     print "Created ingredient %s" % ing.product_name
                    
                formula = Formula(flavor = fl,
                                  ingredient = ing,
                                  amount = weight
                                  )
                
                formula.save()
                
#                 print "Created formula object, Ingredient: %s, Weight: %s\n" % (ing.product_name, weight)
        
            fl.save()
            recalculate_guts(fl)
            
            hcount = 0
            for val in fl.get_hazards().values():
                if val != 'No':
                    hcount = hcount + 1
                
            hazard_count = hcount
            
            if hazard_count < min_hazards:
                print "Hazards: %s  Recreating flavor.\n" % hazard_count
                failed_dict[hazard_count] += 1
                
            else:
                break
                
        
        print "Flavor %s complete\n" % fl.name
        
test_hazard_list = ['acute_hazard_oral', 'respiratory_hazard']
    
def create_sds_identifier_dictionary(test_hazard_list = test_hazard_list):
    
    
    
    #get a list of all combination of hazard categories
    #this list only contains all possible category combinations, but does not contain hazard names
    sds_list = []
    
    #if you replace the two hazards with all hazards, it will create a list of length 105 million and take forever    
    for i in product(*[zip(*GHSIngredient._meta.get_field(h).choices)[0] for h in test_hazard_list]):
        sds_list.append(i)

    
    #to turn that list into a dictionary where the key is a unique identifier and the value is an actual sds dict with hazard names
    
    sds_identifier_dict = {}
    index = 1
    
    for sds in sds_list:
        sds_identifier_dict[index] = dict((test_hazard_list[index], sds[index]) for index in range(0, len(test_hazard_list)))
        index += 1
        
    return sds_identifier_dict
    
            
                
def create_small_sds_identifier_dictionary(flavor_list, test_hazard_list):
    '''
    Attempt to create an sds identifier dict that only contains SDS's that match flavors exactly.
    Each Flavor in the flavor_list will have exactly one SDS that matches it exactly.
    Each SDS in the resulting list will have at least one flavor that matches it exactly
        (more than one if two flavors have the same hazards).
        
    This dictionary depends mostly on existing flavors.
    '''
    #list of sds's with hazard names, but no identifier
    sds_list = []
    
    for fl in flavor_list:
        flavor_hazards = fl.get_hazards()
        
        sds_list.append(dict((hazard, )))
        
    
    
    
    
    
    
    

            
        
        