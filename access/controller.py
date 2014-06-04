from django.core.exceptions import ValidationError

from reversion import revision
from django.db import connection
from django.db.models import Q
from decimal import Decimal

#from collections import namedtuple

acute_toxicity_list = [('acute_hazard_oral', 2000),
                       ('acute_hazard_dermal', 2000),
                       ('acute_hazard_gases', 20000),
                       ('acute_hazard_vapors', 20.0),
                       ('acute_hazard_dusts_mists', 5.0)]


hazard_list = ['acute_hazard_oral',
               'acute_hazard_dermal',
               'acute_hazard_gases',
               'acute_hazard_vapors',
               'acute_hazard_dusts_mists',               
               'skin_corrosion_hazard', 
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
                
        self.total_weight = self.subhazard_dict['total_weight']
        
        self.calculate_ld50s()
        
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
    
    @property
    def aspiration_hazard(self):
        if self.subhazard_dict['aspiration_hazard_1']/self.total_weight * 100 >= Decimal('10.0'):
            return '1'
    
    #the function 'calculate_ld50s' should be run before these
    #calculate_ld50s is now in 'init' so they're calculated when the instance is made
    @property
    def acute_hazard_oral(self):

        #oral_ld50 = self.flavor.oral_ld50
        oral_ld50 = self.subhazard_dict['oral_ld50']
        
        if 0 < oral_ld50 <= 5:
            return '1'
        elif 5 < oral_ld50 <= 50:
            return '2'
        elif 50 < oral_ld50 <= 300:
            return '3'
        elif 300 < oral_ld50 <= 2000:
            return '4'
        else:
            return 'No'
        
    @property
    def acute_hazard_dermal(self):
        
        #dermal_ld50 = self.flavor.dermal_ld50
        dermal_ld50 = self.subhazard_dict['dermal_ld50']
        
        save_ld50(self.flavor, 'dermal_ld50', dermal_ld50)
        
        if 0 < dermal_ld50 <= 50:
            return '1'
        elif 50 < dermal_ld50 <= 200:
            return '2'
        elif 200 < dermal_ld50 <= 1000:
            return '3'
        elif 1000 < dermal_ld50 <= 2000:
            return '4'
        else:
            return 'No'
        
    @property
    def acute_hazard_gases(self):
                
        #gases_ld50 = self.flavor.gases_ld50
        gases_ld50 = self.subhazard_dict['gases_ld50']
        
        if 0 < gases_ld50 <= 100:
            return '1'
        elif 100 < gases_ld50 <= 500:
            return '2'
        elif 500 < gases_ld50 <= 2500:
            return '3'
        elif 2500 < gases_ld50 <= 20000:
            return '4'
        else:
            return 'No'
        
    @property
    def acute_hazard_vapors(self):
        
        #vapors_ld50 = self.flavor.vapors_ld50
        vapors_ld50 = self.subhazard_dict['vapors_ld50']
        
        if 0 < vapors_ld50 <= 0.5:
            return '1'
        elif 0.5 < vapors_ld50 <= 2.0:
            return '2'
        elif 2.0 < vapors_ld50 <= 10.0:
            return '3'
        elif 10.0 < vapors_ld50 <= 20.0:
            return '4'
        else:
            return 'No'
        
    @property
    def acute_hazard_dusts_mists(self):
        
        #dusts_mists_ld50 = self.flavor.dusts_mists_ld50
        dusts_mists_ld50 = self.subhazard_dict['dusts_mists_ld50']
        
        if 0 < dusts_mists_ld50 <= 0.05:
            return '1'
        elif 0.05 < dusts_mists_ld50 <= 0.5:
            return '2'
        elif 0.5 < dusts_mists_ld50 <= 1.0:
            return '3'
        elif 1.0 < dusts_mists_ld50 <= 5.0:
            return '4'
        else:
            return 'No'

       

    def calculate_ld50s(self):
        for acute_hazard, max_ld50 in acute_toxicity_list:
            try:
                ld50 = 1/(self.subhazard_dict[acute_hazard]/self.total_weight)
            except ZeroDivisionError:
                ld50 = max_ld50 + 1
            
            self.subhazard_dict[acute_hazard.split('acute_hazard_')[1] + '_ld50'] = ld50
    
    def save_ld50s(self):
        for acute_hazard, max_ld50 in acute_toxicity_list:
            
            ld50_property = acute_hazard.split('acute_hazard_')[1] + '_ld50'
            
            save_ld50(self.flavor, ld50_property, Decimal(str(self.subhazard_dict[ld50_property])))
    
#     def calculate_and_save_ld50s(self):
#         for acute_hazard, max_ld50 in acute_toxicity_list:
#         
#             try:
#                 ld50 = 1/(self.subhazard_dict[acute_hazard]/self.total_weight)
#             except ZeroDivisionError:
#                 ld50 = max_ld50 + 1
#             
#             save_ld50(self.flavor, acute_hazard.split('acute_hazard_')[1] + '_ld50', Decimal(str(ld50)))
        
    
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
        
        self.save_ld50s()
        
    def recalculate_hazards(self):
        self.subhazard_dict = self.flavor.accumulate_hazards()
        self.calculate_ld50s()
        
        

def save_ld50(flavor, ld50_attr, ld50):
    setattr(flavor, ld50_attr, ld50)
    
    flavor.save()



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
        