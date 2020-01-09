import re
import collections
import sys

from decimal import Decimal

HAZARD_CLASS_NO_SUM_LIST = ('TOSTSingleHazard', 'CarcinogenicityHazard')

def base_accumulate_weights(subhazard_dict, total_weight):
    accumulation_dict = collections.defaultdict(Decimal)

    for hazard_class_name in subhazard_dict:

        hazard_fli_list = subhazard_dict[hazard_class_name]

        if hazard_class_name.split('_')[0] in HAZARD_CLASS_NO_SUM_LIST:
            accumulation_dict[hazard_class_name] = max([fli.weight for fli in hazard_fli_list])
        else:
            accumulation_dict[hazard_class_name] = sum([fli.weight for fli in hazard_fli_list])

    for hazard in accumulation_dict:
        accumulation_dict[hazard] = accumulation_dict[hazard]/total_weight

    return accumulation_dict


def eye_damage_accumulate_weights(subhazard_dict, total_weight):
    accumulation_dict = collections.defaultdict(Decimal)
    
    eye_damage_fli_list = subhazard_dict['EyeDamageHazard_1'] + subhazard_dict['EyeDamageHazard_2A'] + subhazard_dict['EyeDamageHazard_2B']
    skin_corrosion_fli_list = subhazard_dict['SkinCorrosionHazard_1A'] + subhazard_dict['SkinCorrosionHazard_1B']
    
    #Find FLIs that are in both lists
    duplicate_fli_list = [fli for fli in eye_damage_fli_list if fli in skin_corrosion_fli_list]
    
    duplicates_accounted_for = []
    
    for hazard_class_name in ['EyeDamageHazard_1', 'EyeDamageHazard_2A', 'EyeDamageHazard_2B', 'SkinCorrosionHazard_1A', 'SkinCorrosionHazard_1B']:

        hazard_fli_list = subhazard_dict[hazard_class_name]
        
        #remove any duplicates from hazard_fli_list
        hazard_fli_list = [fli for fli in hazard_fli_list if not is_duplicate_fli(fli, duplicate_fli_list, duplicates_accounted_for)]
 
        accumulation_dict[hazard_class_name] = sum([fli.weight for fli in hazard_fli_list])
 
    for hazard in accumulation_dict:
        accumulation_dict[hazard] = accumulation_dict[hazard]/total_weight
 
    return accumulation_dict

#if fli is in duplicate_fli_list and already accounted for, return True.  otherwise, append it to duplicates accounted for
def is_duplicate_fli(fli, duplicate_fli_list, duplicates_accounted_for):
    if fli in duplicate_fli_list:
        if fli in duplicates_accounted_for:
            return True
        else:
            duplicates_accounted_for.append(fli)
    return False

'''
BASE HAZARD PROCESSOR
'''

#raise multiplephase error in here if there are multiple hazards of the same class
def basehazard_process_re(cell_contents, hazard_field, my_re):
    
    hazards_found = []
    
    if my_re.search(cell_contents):
        re_results = my_re.findall(cell_contents)
        
        for category in re_results: #if there's more than one, then there's a duplicate
            hazards_found.append((hazard_field, {'category': category, 'ld50': None}))



    return hazards_found


'''
ACUTE TOXICITY HAZARD PROCESSOR
'''


def acutehazard_process_re(cell_contents, hazard_class_name, ld50_field, re):
    hazards_found = []
    
    if re.search(cell_contents):
        re_results = re.findall(cell_contents)
        for category, ld50 in re_results: #if there's more than one, then there's a duplicate

            #this covers a typo in the document where someone wrote 0,9 instead of 0.9
            #ld50 = ld50.replace(',','.')

            if category in ['1', '2', '3', '4', '5']: #including category 5
                hazards_found.append((hazard_class_name, {'category': category, 'ld50': ld50}))
            
    return hazards_found    


def acutehazard_add_weight_to_subhazard_dict(ingredient, weight, total_weight, acute_hazard, ld50_property,
                                 unknown_weight_key, max_ld50):

    weights_to_add = {}

    from hazards.models import IngredientCategoryInfo
    ingredient_ld50 = IngredientCategoryInfo.objects.get(ingredient = ingredient, category=ingredient)
    #ingredient_ld50 = getattr(ingredient, ld50_property)

    if ingredient_ld50 == None:
        #for each ingredient, only add its weight to the unknown key for each acute hazard
        # if that ingredients concentration is >10%
        if (weight/total_weight) * 100 > 10:
            weights_to_add[unknown_weight_key] = weight #don't modify dict just return values
    elif ingredient_ld50 < max_ld50:
        weights_to_add[acute_hazard] = weight/getattr(ingredient, ld50_property)

    return weights_to_add


'''
ACUTE HAZARDS
'''


class AcuteToxicityOral():
    #put hazard specific parameters in these classes and pass them into the base functions
    human_readable_field = 'Acute Toxicity Hazard: Oral'
    human_readable_ld50 = 'Acute Toxicity Oral LD50'

    hazard_field = 'acute_hazard_oral'
    ld50_field = 'oral_ld50'
    unknown_weight_key = 'oral_unknown'
    max_ld50 = 2000
    
    acute_oral_re = re.compile('ATO[^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*')

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return acutehazard_process_re(cell_contents, AcuteToxicityOral.__name__,
                                                AcuteToxicityOral.ld50_field, AcuteToxicityOral.acute_oral_re)
    @staticmethod
    def add_weight_to_subhazard_dict(ingredient, weight, total_weight):
        return acutehazard_add_weight_to_subhazard_dict(ingredient, weight, total_weight,
                                                                         AcuteToxicityOral.hazard_field,
                                                                         AcuteToxicityOral.ld50_field,
                                                                         AcuteToxicityOral.unknown_weight_key,
                                                                         AcuteToxicityOral.max_ld50)

class AcuteToxicityDermal():
    human_readable_field = 'Acute Toxicity Hazard: Dermal'
    human_readable_ld50 = 'Acute Toxicity Dermal LD50'

    hazard_field = 'acute_hazard_dermal'
    ld50_field = 'dermal_ld50'
    unknown_weight_key = 'dermal_unknown'
    max_ld50 = 2000
    
    acute_dermal_re = re.compile('ATD[^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*')

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return acutehazard_process_re(cell_contents, AcuteToxicityDermal.__name__, 
                                                AcuteToxicityDermal.ld50_field, AcuteToxicityDermal.acute_dermal_re)

    @staticmethod
    def add_weight_to_subhazard_dict(ingredient, weight, total_weight):
        return acutehazard_add_weight_to_subhazard_dict(ingredient, weight, total_weight,
                                                                         AcuteToxicityDermal.hazard_field,
                                                                         AcuteToxicityDermal.ld50_field,
                                                                         AcuteToxicityDermal.unknown_weight_key,
                                                                         AcuteToxicityDermal.max_ld50)

class AcuteToxicityInhalation():
    human_readable_field = 'Acute Toxicity Hazard: Vapors/Inhalation'
    human_readable_ld50 = 'Acute Toxicity Vapors/Inhalation LD50'

    hazard_field = 'acute_hazard_inhalation'
    ld50_field = 'vapors_ld50'
    unknown_weight_key = 'inhalation_unknown'
    max_ld50 = 20.0

    #this one did not account for decimals '0.5
    #acute_inhalation_re = re.compile('ATI[^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*')


    acute_inhalation_re = re.compile('ATI[^\d]*(\d)[^(\d]*\([^\d]*([\d]+(?:[.,]?[\d]+)?)[^)]*')

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return acutehazard_process_re(cell_contents, AcuteToxicityInhalation.__name__, 
                                                AcuteToxicityInhalation.ld50_field, AcuteToxicityInhalation.acute_inhalation_re)

    @staticmethod
    def add_weight_to_subhazard_dict(ingredient, weight, total_weight):
        return acutehazard_add_weight_to_subhazard_dict(ingredient, weight, total_weight,
                                                                         AcuteToxicityInhalation.hazard_field,
                                                                         AcuteToxicityInhalation.ld50_field,
                                                                         AcuteToxicityInhalation.unknown_weight_key,
                                                                         AcuteToxicityInhalation.max_ld50)
 
'''
NON ACUTE HAZARDS
'''


def simple_cat_list(cat_list):
    seen_set = set()

    for cat in cat_list:
        number = cat[0]
        if number not in seen_set:
            seen_set.add(number)
            yield number



class SummationRow():
    def __init__(self, calculate_sum_func, calculate_sum_str, threshold_dict):
        self.calculate_sum_func = calculate_sum_func
        self.calculate_sum_str = calculate_sum_str
        self.threshold_dict = threshold_dict

    def my_percentage(self, hazard_accumulator):
        if not hasattr(self, '_sum'):
            sum = self.calculate_sum_func(hazard_accumulator)
            self._percentage = sum/hazard_accumulator.total_weight * 100

        return self._percentage

    def test(self, cat, hazard_accumulator):
        return self.my_percentage(hazard_accumulator) >= self.threshold_dict[cat]



class SkinCorrosionHazard():
    human_readable_field = 'Skin Corrosion Hazard'
    hazard_field = 'skin_corrosion_hazard'
    sci_re = re.compile('SCI[^\d]*(\d[ABC]?)')
    potential_tokens = ['1A', '1B', '1C', '2', '3']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def get_summation_row_list(subhazard_dict):
        sr1 = SummationRow(subhazard_dict)

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, SkinCorrosionHazard.__name__, SkinCorrosionHazard.sci_re)


class EyeDamageHazard():

    human_readable_field = 'Eye Damage Hazard'
    hazard_field = 'eye_damage_hazard'
    edi_re = re.compile('EDI[^\d]*(\d[ABC]?)')
    potential_tokens = ['1, 2A, 2B']
    relevant_hazards=['SkinCorrosionHazard_1',]
    
    @staticmethod
    def get_my_accumulator():
        return eye_damage_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, EyeDamageHazard.__name__, EyeDamageHazard.edi_re)


class CarcinogenicityHazard():

    human_readable_field = 'Carcinogenicity Hazard'
    hazard_field = 'carcinogenicity_hazard'
    car_re = re.compile('CAR[^\d]*(\d[ABC]?)')
    potential_tokens = ['1A', '1B', '2']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, CarcinogenicityHazard.__name__, CarcinogenicityHazard.car_re)

  
class TOSTSingleHazard():

    human_readable_field = 'Target Organ System Toxicity: Single Exposure Hazard'
    hazard_field = 'tost_single_hazard'
    tost_single_re = re.compile('STO[^-]*-[^S]*SE[^\d]*(\d(?:(?:-?\s?RI)?(?:-?\s?NE)?)?)')
    potential_tokens = ['1', '2', '3NE', '3RI', '3-NE', '3-RI']
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        
        re = TOSTSingleHazard.tost_single_re
        hazard_field = TOSTSingleHazard.__name__
        
        hazards_found = []
        
        if re.search(cell_contents):
            re_results = re.findall(cell_contents)
            
            #print re_results
            
            for category in re_results:

                #this converts all 3-NE to 3NE, as well as 3 NE into 3NE (that happpens once 65-85-0 74-89-5)
                category = category.replace('3-NE', '3NE').replace('3-RI', '3RI').replace(' ','')

                if category in ['3', '3NE', '3RI'] and ('3RI' and '3NE') in re_results:
                    if ('TOSTSingleHazard', {'category': '3NE', 'ld50': None}) and \
                                    ('TOSTSingleHazard', {'category': '3RI', 'ld50': None}) not in hazards_found:
                        hazards_found.append((hazard_field, {'category': '3NE', 'ld50': None}))
                        hazards_found.append((hazard_field, {'category': '3RI', 'ld50': None}))

                    
                else:
                    hazards_found.append((hazard_field, {'category': category, 'ld50': None}))

        return hazards_found


class TOSTRepeatHazard():

    human_readable_field = 'Target Organ System Toxicity: Repeated Exposure Hazard'
    hazard_field = 'tost_repeat_hazard'
    tost_repeat_re = re.compile('STO[^-]*-[^R]*RE[^\d]*(\d)')
    potential_tokens = ['1', '2']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, TOSTRepeatHazard.__name__, TOSTRepeatHazard.tost_repeat_re)


class SkinSensitizationHazard():

    human_readable_field = 'Skin Sensitization Hazard'
    hazard_field = 'skin_sensitization_hazard'
    ss_re = re.compile('SS[^\d]*(\d[ABC]?)')
    potential_tokens = ['1', '1A', '1B']
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
        
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, SkinSensitizationHazard.__name__, SkinSensitizationHazard.ss_re)


class GermCellMutagenicityHazard():

    human_readable_field = 'Germ Cell Mutagenicity Hazard'
    hazard_field = 'germ_cell_mutagenicity_hazard'
    mut_re = re.compile('MUT[^\d]*(\d[AB]?)')
    potential_tokens = ['1A', '1B', '2']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, GermCellMutagenicityHazard.__name__, GermCellMutagenicityHazard.mut_re)

class ReproductiveToxicityHazard():

    human_readable_field = 'Reproductive Toxicity Hazard'
    hazard_field = 'reproductive_toxicity_hazard'
    rep_re = re.compile('REP[^\d]*(\d[AB]?)')
    potential_tokens = ['1A', '1B', '2']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, ReproductiveToxicityHazard.__name__, ReproductiveToxicityHazard.rep_re)

class AspirationHazard():

    human_readable_field = 'Aspiration Hazard'
    hazard_field = 'aspiration_hazard'
    ah_re = re.compile('AH[^\d]*(\d?)')
    potential_tokens = ['1']

    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights

    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, AspirationHazard.__name__, AspirationHazard.ah_re)


'''
The hazards below can be found on some ingredients in the document.  They will be saved to the GHSIngredient objects
during import.  HOWEVER, they are NOT calculated for final products, and do not need any subhazard_dict related functions.
'''


class ChronicAquaticHazard():
    human_readable_field = 'Chronic Aquatic Toxicity Hazard'
    hazard_field = 'chronic_aquatic_toxicity_hazard'
    ca_re = re.compile('EH C(\d)')
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, ChronicAquaticHazard.__name__, ChronicAquaticHazard.ca_re)    


class AcuteAquaticHazard():
    human_readable_field = 'Acute Aquatic Toxicity Hazard'
    hazard_field = 'acute_aquatic_toxicity_hazard'
    aa_re = re.compile('EH A(\d)')
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, AcuteAquaticHazard.__name__, AcuteAquaticHazard.aa_re)    


class FlammableSolidHazard():
    human_readable_field = 'Flammable Solid Hazard'
    hazard_field = 'flammable_solid_hazard'
    fs_re = re.compile('FS[^\d]*(\d)')
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, FlammableSolidHazard.__name__, FlammableSolidHazard.fs_re)    

class FlammableLiquidHazard():
    human_readable_field = 'Flammable Liquid Hazard'
    hazard_field = 'flammable_liquid_hazard'
    fl_re = re.compile('FL[^\d]*(\d)')
    potential_tokens = ['1', '2', '3', '4',]
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, FlammableLiquidHazard.__name__, FlammableLiquidHazard.fl_re)    

class FlammableGasHazard():
    human_readable_field = 'Flammable Gas Hazard'
    hazard_field = 'emit_flammable_hazard'
    fg_re = re.compile('FG[^\d]*(\d)')
    
    @staticmethod
    def get_my_accumulator():
        return base_accumulate_weights
    
    @staticmethod
    def process_re(cell_contents):
        return basehazard_process_re(cell_contents, FlammableGasHazard.__name__, FlammableGasHazard.fg_re)    


#  #these hazards do not appear in the hazard document
#  class AcuteToxicityVapors():
#      pass
#      
#  class AcuteToxicityDustsMists():
#      pass
#  
#  class AcuteToxicityGases():
#      pass
#  
#  class GermCellMutagenicityHazard():
#      pass
#  
#  class ReproductiveHazard():
#      pass
#  
#  class RespiratoryHazard():
#      pass

acute_toxicity_class_list = [AcuteToxicityOral, AcuteToxicityDermal, AcuteToxicityInhalation]


class CategoryTest():

    def __init__(self, eval_str):
        self.eval_str = eval_str
        try:
            self.summation, self.threshold = eval_str.split(' >= ')
        except:
            pass

    def test(self, accumulator):
        return eval(self.eval_str, accumulator)

    def render_test(self):

        rendered_string = self.summation.replace('_', ' ') + ' >= ' + str(Decimal(self.threshold) * 100) + '%'
        return rendered_string

    def value(self, accumulator):
        value = round(eval(self.summation, accumulator) * 100, 4)
        return str(value) + '%'
    
    def value_int(self, accumulator):
        return round(eval(self.summation, accumulator), 4)

class LD50Test():

    def __init__(self, eval_str):
        self.eval_str = eval_str
        try:
            self.ld50_field, self.threshold = eval_str.split(' <= ')
        except:
            pass
            #self.ld50_field, self.limit = eval_str.split(' > ')

    def test(self, accumulator):
        if accumulator[self.ld50_field] == None:
            return False
        else:
            return eval(self.eval_str, accumulator)

    def render_test(self):
        from hazards.models import HazardClass
        for hc in HazardClass.objects.all():
            python_class = hc.python_hazard_class
            if getattr(python_class, 'ld50_field', None) == self.ld50_field:
                human_readable_ld50 = python_class.human_readable_ld50

        rendered_string = human_readable_ld50 + ' <= ' + self.threshold
        return rendered_string

    def value(self, accumulator):
        eval_str = self.eval_str
        value = accumulator[self.ld50_field]

        if value:
           return str(round(float(value), 4))
        else:
            return 'N/A'

