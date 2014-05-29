from django.core.exceptions import ValidationError

from reversion import revision
from django.db import connection
from django.db.models import Q
from decimal import Decimal

#from collections import namedtuple


hazard_list = ['skin_corrosion_hazard', 
               'eye_damage_hazard', 
               'germ_cell_mutagenicity_hazard', 
               'carcinogenicty_hazard', 
               'reproductive_hazard',
               'tost_single_hazard',
               'tost_repeat_hazard',
               'respiratory_hazard',
               'skin_sensitization_hazard']

"""
To add another hazard:
1. Make a function in the HazardAccumulator class below
2. Add the hazard property to the hazard list above
"""

class HazardAccumulator():
    def __init__(self, flavor):
        self.flavor = flavor
        
        self.subhazard_dict = self.flavor.accumulate_hazards()
        
    #Each hazard has a function below which describes the requirements/criteria the ingredients must meet in order for 
    #the flavor to be in a specific hazard category.  
    @property
    def skin_corrosion_hazard(self):
        skin_1 = self.subhazard_dict['skin_corrosion_hazard_1A'] + self.subhazard_dict['skin_corrosion_hazard_1B'] + self.subhazard_dict['skin_corrosion_hazard_1C']
        skin_2 = self.subhazard_dict['skin_corrosion_hazard_2']
        
        if skin_1/self.subhazard_dict['total_weight'] * 100 >= 5:
            if self.subhazard_dict['skin_corrosion_hazard_1A'] >= 0:
                return '1A'
            elif self.subhazard_dict['skin_corrosion_hazard_1B'] >= 0:
                return '1B'
            else:
                return '1C'
        elif (10 * skin_1 + skin_2)/self.subhazard_dict['total_weight'] * 100 >= 10:
            return '2'
        else:
            return 'No'

    @property    
    def eye_damage_hazard(self):
        skin_corrosion_1 = self.subhazard_dict['skin_corrosion_hazard_1A'] + self.subhazard_dict['skin_corrosion_hazard_1B'] + self.subhazard_dict['skin_corrosion_hazard_1C']
        eye_damage_1 = self.subhazard_dict['eye_damage_hazard_1']
        eye_damage_2 = self.subhazard_dict['eye_damage_hazard_2A'] + self.subhazard_dict['eye_damage_hazard_2B']
        
        if (skin_corrosion_1 + eye_damage_1)/self.subhazard_dict['total_weight'] * 100 >= 3:
            #test = (skin_corrosion_1 + eye_damage_1)/self.subhazard_dict['total_weight'] * 100
            return '1'# % test
        
        elif (10*(skin_corrosion_1 + eye_damage_1) + eye_damage_2)/self.subhazard_dict['total_weight'] * 100 >= 10:
            #if all the ingredients are in eye_damage_2, it is in category 2B
            if skin_corrosion_1 + eye_damage_1 + self.subhazard_dict['eye_damage_hazard_2A'] == 0:
                return '2B'
            else:
                return '2A' #if any ingredients are in 2A, it is  in category 2A
        
        else:
            return 'No'
        
    @property
    def germ_cell_mutagenicity_hazard(self):
        if (self.subhazard_dict['germ_cell_mutagenicity_hazard_1A'])/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            return '1A'
        elif (self.subhazard_dict['germ_cell_mutagenicity_hazard_1B'])/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            return '1B'
        elif (self.subhazard_dict['germ_cell_mutagenicity_hazard_2'])/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '2'
        else:
            return 'No'
        
    @property
    def carcinogenicty_hazard(self):
        if (self.subhazard_dict['carcinogenicty_hazard_1A'] + self.subhazard_dict['carcinogenicty_hazard_1B'])/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            if self.subhazard_dict['carcinogenicty_hazard_1A'] >= 0:
                return '1A'
            else:
                return '1B'
        elif (self.subhazard_dict['carcinogenicty_hazard_2'])/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '2'
        else:
            return 'No'
            
    @property
    def reproductive_hazard(self):
        reproductive_1 = self.subhazard_dict['reproductive_hazard_1A'] + self.subhazard_dict['reproductive_hazard_1B']
        
        if reproductive_1/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            if self.subhazard_dict['reproductive_hazard_1A'] >= 0:
                return '1A'
            else:
                return '1B'
            
        elif self.subhazard_dict['reproductive_hazard_2']/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            return '2'
        
        elif self.subhazard_dict['reproductive_hazard_3']/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            return '3'
        
        else:
            return 'No'
        
    @property
    def tost_single_hazard(self):
        if self.subhazard_dict['tost_single_hazard_1']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '1'
        elif self.subhazard_dict['tost_single_hazard_2']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '2'
        elif self.subhazard_dict['tost_single_hazard_3']/self.subhazard_dict['total_weight'] * 100 >= Decimal('20.0'):
            return '3'
        else:
            return 'No'
        
    @property
    def tost_repeat_hazard(self):
        if self.subhazard_dict['tost_repeat_hazard_1']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '1'
        elif self.subhazard_dict['tost_repeat_hazard_2']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
            return '2'

        else:
            return 'No'

    @property
    def respiratory_hazard(self):
        respiratory_1 = self.subhazard_dict['respiratory_hazard_1A'] + self.subhazard_dict['respiratory_hazard_1B']
                
        if respiratory_1/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            if self.subhazard_dict['respiratory_hazard_1A']/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
                return '1A'
            elif self.subhazard_dict['respiratory_hazard_1B']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
                return '1B'
            else:
                return '1'
        else:
            return 'No'
        
    @property
    def skin_sensitization_hazard(self):
        skin_1 = self.subhazard_dict['skin_sensitization_hazard_1A'] + self.subhazard_dict['skin_sensitization_hazard_1B']
                
        if skin_1/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
            if self.subhazard_dict['skin_sensitization_hazard_1A']/self.subhazard_dict['total_weight'] * 100 >= Decimal('0.1'):
                return '1A'
            elif self.subhazard_dict['skin_sensitization_hazard_1B']/self.subhazard_dict['total_weight'] * 100 >= Decimal('1.0'):
                return '1B'
            else:
                return '1'
        else:
            return 'No'
            
            
        
    def get_hazard_dict(self):
        
        hazard_dict = {}
        
        for hazard_property in hazard_list:
            
            hazard_dict[hazard_property] = getattr(self, hazard_property)
            
        return hazard_dict
        
    def save_hazards(self):
        hazard_dict = self.get_hazard_dict()
        
        for hazard_name, category in hazard_dict.iteritems():
            setattr(self.flavor, hazard_name, category)
            
        self.flavor.save()
        



#my previous implementation of the hazard calculator.  

# CategoryAndMultiplier = namedtuple('CategoryAndMultiplier', 'final_category multiplier')
# 
# def make_hazard_class(hazard_dict):
#     
#     """INSERT HIGH-LEVEL DOCUMENTATION HERE!!.
#     
#     #. Create a HazardAccumulator class with the dictionary as the argument.
#     #. Create a function that will accumulate the hazard totals based on the input dictionary.
#     #. Create a function that returns the final category of the flavor.
#     #. In the flavor model, create an instance of this class for each hazard and return the final categories for all hazards.
#             #Might want to change this later since these classes/instances will have to be created each time a flavor's hazards are calculated.
#     
#     """
#     
#     class HazardAccumulator():
#         hazard_vars = {}
#         
#         #the "categories" key in the input dictionary stores the possible final categories that the flavor might be in.
#         #hazard_vars is a dictionary where the keys are the possible final categories, and the value is the accumulation associated with each of those categories
#         #the loop below generates these keys, with a default value of 0 
#         for cat in hazard_dict["categories"]: 
#             hazard_vars[cat] = 0
# 
#         #this function goes through an ingredient and adds the correct weight to the total accumulation for each final category 
#         #this means adding to the values in the hazard_vars dictionary created above
#         def accumulate(self, ingredient, weight):
#             for ingredient_hazard_property in hazard_dict['requirements']:
#                 ingredient_hazard_categories = hazard_dict['requirements'][ingredient_hazard_property]
#                 for category in ingredient_hazard_categories:
#                     if getattr(ingredient, ingredient_hazard_property) == category:
#                         accumulate_list = ingredient_hazard_categories[category]
#                         for cat_and_mult in accumulate_list:
#                             self.hazard_vars[cat_and_mult.final_category] += weight * cat_and_mult.multiplier
#                             
#         #this function takes            
#         def get_category(self, total_weight):    
#             for var in self.hazard_vars: #gets variable names
#                 hazard_percentage = self.hazard_vars[var]/total_weight * 100
#                 
#                 if hazard_percentage >= hazard_dict["categories"][var]:
#                     return var + str(hazard_percentage)
#                 
#             return "No Hazard"
#         
#         def get_name(self):
#             return hazard_dict['name']
#         
#     return HazardAccumulator
# 
# 



        
        
    
    

# class BaseHazard():
# # eye_hazard_dict = {
# #                    'name': 'Eye Hazard',
# #                    'categories': {"Category 1": 3, "Category 2": 10},
# #                    'requirements':
# #                         {
# #                          'skin_corrosion_hazard':
# #                              {
# #                               "1A": [("Category 1", 1), ("Category 2", 10)],
# #                               "1B": [("Category 1", 1), ("Category 2", 10)],
# #                               "1C": [("Category 1", 1), ("Category 2", 10)],
# #                               },
# #                          'eye_damage_hazard':
# #                             {
# #                              "1": [("Category 1", 1), ("Category 2", 10)],
# #                              "2A": [("Category 2", 1)],
# #                              "2B": [("Category 2", 1)],
# #                              }
# #                          }
# #                    }
#     def accumulate(self, ingredient, weight):
#         pass
# 
#                 
#     def get_category(self, total_weight):    
#         for var in self.hazard_vars: #gets variable names
#             hazard_percentage = self.hazard_vars[var]/total_weight * 100
#             
#             if hazard_percentage >= hazard_dict["categories"][var]:
#                 return var
#             
#         return "No Hazard"
#     
#     def get_name(self):
#         return hazard_dict['name']
#     
# 
# class SkinHazard(BaseHazard):
#     name = "Skin Hazard"
    

# #SKIN HAZARD REQUIREMENTS AND DICTIONARY
# skin_reqs = dict.fromkeys(["1A", "1B", "1C"], [CategoryAndMultiplier("Category 1", 1), CategoryAndMultiplier("Category 2", 10)])
# skin_reqs.update(dict.fromkeys(["2"], [CategoryAndMultiplier("Category 2", 1)]))
# 
# skin_hazard_dict = {
#                     'name': 'Skin Hazard',
#                     'categories': {"Category 1": 5, "Category 2": 10},
#                     'requirements': 
#                         {
#                          'skin_corrosion_hazard': skin_reqs,
#                         }
#                     }
# 
# #EYE HAZARD REQUIREMENTS AND DICTIONARY
# eye_reqs_SKIN = dict.fromkeys(["1A", "1B", "1C"], [CategoryAndMultiplier("Category 1", 1), CategoryAndMultiplier("Category 2", 10)])
# 
# eye_reqs_EYE = dict.fromkeys(["1"], [CategoryAndMultiplier("Category 1", 1), CategoryAndMultiplier("Category 2", 10)])
# eye_reqs_EYE.update(dict.fromkeys(["2A", "2B"], [CategoryAndMultiplier("Category 2", 1)]))
# 
# eye_hazard_dict = {
#                    'name': 'Eye Hazard',
#                    'categories': {"Category 1": 3, "Category 2": 10},
#                    'requirements':
#                         {
#                          'skin_corrosion_hazard': eye_reqs_SKIN,
#                          'eye_damage_hazard': eye_reqs_EYE,
#                          }
#                    }
# 
# #RESPIRATORY/SENSITATION HAZARD REQUIREMENTS AND DICTIONARY
# respiratory_reqs = dict.fromkeys(["1", "1A", "1B"], [CategoryAndMultiplier("Category 1", 1)])
# 
# respiratory_hazard_dict = {
#                            'name': 'Respiratory Sensitation Hazard',
#                            'categories': {"Category 1": 0.1},
#                            'requirements':
#                                 {
#                                  'germ_cell_mutagenicity_hazard': respiratory_reqs,
#                                  }
#                            }
# 
# #GERM MUTAGENICITY HAZARD REQUIREMETNS AND DICTIONARY
# germ_mutagenicity_reqs = {
#                           "1A": [CategoryAndMultiplier("Category 1A", 1)],
#                           "1B": [CategoryAndMultiplier("Category 1B", 1)],
#                           "2": [CategoryAndMultiplier("Category 2", 1)],
#                           }
# 
# germ_mutagenicity_dict = {
#                            'name': 'Germ Mutagenicity Hazard',
#                            'categories': {"Category 1A": 0.1, "Category 1B": 0.1, "Category 2": 1},
#                            'requirements':
#                                 {
#                                  'germ_cell_mutagenicity_hazard': germ_mutagenicity_reqs,
#                                  }
#                            }

# Hazard dictionaries without using other dictionaries
# 
# skin_hazard_dict = {
#                     'name': 'Skin Hazard',
#                     'categories': {"Category 1": 5, "Category 2": 10},
#                     'requirements': 
#                         {
#                          'skin_corrosion_hazard':                      
#                             {
#                              #IS THERE A FASTER WAY TO ADD SAME VALUES TO DIFFERENT KEYS??
#                              #OR SOMEHOW HAVE "1A" or "1B" or "1C" AS A KEY
#                             "1A": [("Category 1", 1), ("Category 2", 10)],
#                             "1B": [("Category 1", 1), ("Category 2", 10)],
#                             "1C": [("Category 1", 1), ("Category 2", 10)],
#                             "2": [("Category 2", 1)]                             
#                              },
#                         }
#                     }
# 


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
        