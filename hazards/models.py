import collections
import json

from django.db import models
from decimal import Decimal

from hazards.initial_data import HazardClassDict, HCodeDict


'''
class GHSProduct(models.Model):
    """
    This model is used whenever a user generates a formula manually using hazard calculator form.
    It contains any data relevant to the given formula which needs to be rendered in the SDS.
    """
    name = models.CharField(max_length=255, blank=True)
    formula_list = models.TextField() #JSON-serialized text version of formula_list

    #hazard_set = models.ManyToManyField('HazardCategory', through='IngredientCategoryInfo')

    def get_hazard_formula_list(self):
        formula_list = []
        for fli_dict in json.loads(self.formula_list, use_decimal=True):
            formula_list.append(FormulaLineItem(
                                    cas = fli_dict['cas'],
                                    weight = fli_dict['weight'],
                                    source_name = fli_dict['source_name'],
                                    source_url = fli_dict['source_url'],
                                ))

        return formula_list

    def get_sds_url(self):
        return reverse('hazards.views.safety_data_sheet', kwargs={'product_id': self.id})

    def get_hazards_url(self):
        return reverse('hazards.views.hazard_calculator', kwargs={'product_id': self.id})
'''
# class EllipsisInfo(models.Model):
#     #flavor = models.ForeignKey('Flavor')
#     pcode = models.CharField(max_length=55)
#     index = models.PositiveIntegerField()
#     info = models.CharField(max_length=255, blank=True)
#
#     content_type = models.ForeignKey(ContentType)
#     object_id = models.PositiveIntegerField()
#     content_object = generic.GenericForeignKey()

class HazardClass(models.Model):
    python_class_name = models.CharField(max_length=100)
    human_readable_name = models.CharField(max_length=100)

    def __str__(self):
        return "%s" % self.python_class_name

    @property
    def python_hazard_class(self):
        from hazards import hazard_classes
        return hazard_classes.__dict__[self.python_class_name]


class HazardCategory(models.Model):
    hazard_class = models.ForeignKey('HazardClass', on_delete=models.CASCADE)
    category = models.CharField(max_length=15)

    def __str__(self):
        return "%s: %s" % (self.hazard_class.python_class_name, self.category)

    @property
    def app_dictionary_key(self):
        return '%s_%s' % (self.hazard_class.python_class_name, self.category)

    @property
    def hcode(self):
        try:
            return HazardClassDict[self.hazard_class.python_class_name][self.category].hcode
        except:
            category= self.category[:1]
            return HazardClassDict[self.hazard_class.python_class_name][category].hcode

    def get_hcode_info(self):
        hcode_data = HCodeDict[self.hcode]
        return hcode_data

    @property
    def acute(self):
        return "Acute" in self.hazard_class.python_class_name

class IngredientCategoryInfo(models.Model):
    #this contains information specific to an ingredient+category pair (ld50)
    ingredient = models.ForeignKey('GHSIngredient', on_delete=models.CASCADE)
    category = models.ForeignKey('HazardCategory' ,on_delete=models.CASCADE)
    ld50 = models.DecimalField(decimal_places = 3, max_digits = 10, null=True, blank=True)



class GHSIngredient(models.Model):

    def __str__(self):
        return "%s: %s" % (self.cas, self.name)

    cas = models.CharField(
        max_length=20,
        unique=True)

    hazard_set = models.ManyToManyField('HazardCategory', through='IngredientCategoryInfo')

    #raw data fields parsed straight from the document
    reach = models.CharField(max_length=20, blank=True)
    name = models.TextField(blank=True)
    ghs_hazard_category = models.TextField(blank=True)
    ghs_change_indicators = models.TextField(blank=True)
    ghs_signal_words = models.TextField(blank=True)
    ghs_codes = models.TextField(blank=True)
    ghs_pictogram_codes = models.TextField(blank=True)
    synonyms = models.TextField(blank=True)



# class FormulaLineItem(models.Model):
#     """
#     This model pretty much represents a consolidated leaf weight of a flavor.
#     Each instance of this model will contain a cas number and a weight.
#     A list of a FormulaLineItem objects will be passed into the main function of this app.
#     """
#
#     def __str__(self):
#         if self.source_name:
#             return u"%s-%s-%s" % (self.cas, self.weight, self.source_name)
#         else:
#             return u"%s-%s" % (self.cas, self.weight)
#
#     cas = models.CharField(max_length=15)
#     weight = models.DecimalField(decimal_places=3, max_digits=7)
#     source_name = models.CharField(max_length=150, blank=True)
#     source_url = models.CharField(max_length=150, blank=True)
#     mismatch = models.BooleanField(default=False)
#     fdi_ingredient = models.ForeignKey(Ingredient)
#
#     def as_json(self):
#         return dict(
#                     cas = self.cas,
#                     weight = self.weight,
#                     source_name = self.source_name,
#                     source_url = self.source_url,
#                     )

# class PrecautionaryStatement(models.Model):


class AccumulatorRules():
    def __init__(self, rules):
        self.rules = rules #rules should be a list of all relevant hazards needed to calculate a certain hazard


class HazardAccumulator(dict):

    def __init__(self, formula_list):

        self.total_weight = Decimal(sum([fli.weight for fli in formula_list]))
        self.subhazard_dict = create_subhazard_dict(formula_list)
#         self.accumulation_dict = base_accumulate_weights(self.subhazard_dict, self.total_weight)
        self.ld50_dict = self.calculate_unknown_ld50_weights(formula_list)
        self.calculate_ld50s()

#         self.update(self.get_consolidated_dict())
#         self.update(self.ld50_dict)



    def set_accumulation_dict(self, my_accumulator_function):

        self.accumulation_dict = my_accumulator_function(self.subhazard_dict, self.total_weight)
        self.update(self.get_consolidated_dict())
        self.update(self.ld50_dict)

    def calculate_unknown_ld50_weights(self, formula_list):

        unknown_weight_dict = collections.defaultdict(Decimal)

        for fli in formula_list:
            '''
            if fli.mismatch:
                ingredient = GHSIngredient.objects.get(cas='00-00-1')
            else:
                ingredient = GHSIngredient.objects.get(cas=fli.cas)
            '''
            ingredient = fli.ingredient
            weight = fli.weight

            from hazards import hazard_classes
            from access.models import FDIIngredientCategoryInfo
            for acute_hazard_class in hazard_classes.acute_toxicity_class_list:
                try:
                    hazard_category = ingredient.hazard_set.get(hazard_class__python_class_name = acute_hazard_class.__name__)
                    ld50 = FDIIngredientCategoryInfo.objects.get(ingredient = ingredient, category = hazard_category).ld50
                except:
                    ld50 = None

                if ld50 == None:
                    if weight/self.total_weight * 100 > 10:
                        unknown_weight_dict[acute_hazard_class.unknown_weight_key] += weight
                elif ld50 < acute_hazard_class.max_ld50:
                    unknown_weight_dict[acute_hazard_class.__name__] += weight/ld50

        return unknown_weight_dict

    def calculate_ld50s(self):
        """
        Use formula information and unknown ld50 weights to calculate the
        ld50 for each acute hazard.
        """

        from hazards.hazard_classes import acute_toxicity_class_list
        for acute_toxicity_class in acute_toxicity_class_list:
            try:
                ld50 = (self.total_weight - self.ld50_dict[acute_toxicity_class.unknown_weight_key])/(self.ld50_dict[acute_toxicity_class.__name__])
            except:
                ld50 = None

            self.ld50_dict[acute_toxicity_class.ld50_field] = ld50


    def get_consolidated_accumulation(self, hazard_cat_key):
        """
        Returns the sum of a hazard's accumulated weights for a given category

        Example:
        Input: 'SkinCorrosion_1'
        Output: SkinCorrosion_1A + SkinCorrosion_1B + SkinCorrosion_1C

        """
        #
        # consolidated_sum = 0
        #
        # for hazard_category in self.accumulation_dict:
        #     if hazard_cat_key in hazard_category:
        #         consolidated_sum += self.accumulation_dict[hazard_category]
        #
        # return consolidated_sum



        consolidated_sum = 0
        hazard, cat = hazard_cat_key.split('_')

        hazard_category_info = HazardClassDict[hazard][cat]

        for subcategory in hazard_category_info.subcategories:
            consolidated_sum += self.accumulation_dict.copy()[hazard_cat_key + subcategory]

        return consolidated_sum


    def get_consolidated_dict(self):

        consolidated_dict = {}

        for hazard_class in HazardClassDict:
            for consolidated_cat in HazardClassDict[hazard_class]:

                class_cat_str = '%s_%s' % (hazard_class, consolidated_cat)
                consolidated_weight = self.get_consolidated_accumulation(class_cat_str)

                consolidated_dict[class_cat_str] = consolidated_weight

        return consolidated_dict



def create_subhazard_dict(formula_list):

    """
    Given the consolidated leaf weights of a flavor (in the form of FormulaLineItem objects),
    create a dictionary which contains the total hazard accumulation for each subhazard.

    A 'subhazard' is a hazard + category combination; eg. 'skin_corrosion_hazard_1A'.

    Input: A list of leafweight objects, corresponding to ingredients and weights for a single flavor
    Output: A dictionary which contains the total 'accumulation' for each subhazard

    The output of this function is passed to the HazardAccumulator class, which uses these
    'accumulations' to calculate the final product's hazards.

    """
    #create a copy of an empty subhazard dict
    #this allows us to avoid the process of creating the empty dict every time
    hazard_dict = collections.defaultdict(list)
    '''
    CALCULATING ACUTE TOXICITY HAZARDS (NOT THE SAME AS CALCULATING OTHER HAZARDS)

    A BUNCH OF ALGEBRA TO GET THE FINAL FORMULA BELOW

    The formula to obtain the ld50 of a flavor is:
        (100 - unknown_concentration)/flavor_ld50 = Sigma(ingredient_concentration/ingredient_ld50)

    To calculate the final sum of the Sigma operation, I would originally do something like:

        for ingredient in ingredients_under_the_ld50_threshold:
            sigma += (weight/total_weight * 100) / ingredient.ld50

    However, since I'm calculating the total_weight in the same loop, I do not yet have access
        to the total weight.  To work around this, I factor our the 100/total_weight from the sigma
        equation since these remain constant.  I end up with:

        for ingredient in ingredients_under_the_ld50_threshold:
            sigma += weight / ingredient.ld50

    The value 'sigma' above is what I store in the hazard_dict for each acute hazard.

    We know that:

        LD50_flavor = (100 - unknown_concentration) / (100 * sigma/total_weight),

        unknown_concentration = (weight_unknown/total_weight) * 100

    Substitute everything in:

        LD50_flavor = (100 - 100 * (weight_unknown/total_weight)) / 100 * (sigma/total_weight)

    Cancel out the 100's:

        LD50_flavor = (1 - weight_unknown/total_weight) / (sigma/total_weight),

    Replace the 1 on the left side with total_weight/total_weight, then cancel the total_weights:

    FINAL FORMULA ------------------------------------------------------------------------

        LD50_flavor = (total_weight - weight_unknown) / sigma

            where sigma = sum(create_subhazard_dictingredient_weights/ingredient_ld50s)

    --------------------------------------------------------------------------------------

    Steps to calculate ld50 of a flavor:
    1. Store weight_unknown and sigma in the hazard_dictionary
        -Note: Each acute subhazard (oral, dermal, etc.) needs its own weight_unknown
    2. In the controller, use the total_weight and the final formula above to find LD50_flavor

        weight = fli.weight

        show_details_logger = logging.getLogger(__name__)


    '''

    #for each base ingredient in the flavor, find any hazards it has and add its weight to each of those
    for fli in formula_list:

#         if fli.source_name:

        #USE FDI INGREDIENT INSTEAD OF GHS INGREDIENT

        ingredient = fli.ingredient

#         if fli.mismatch:
#             ingredient = GHSIngredient.objects.get(cas = '00-00-00')
#         else:
#             ingredient = GHSIngredient.objects.get(cas = fli.cas)

        for hazard_category in ingredient.hazard_set.all():
            hazard_dict[hazard_category.app_dictionary_key].append(fli)

#         #for ALL acute hazards (even hazards that the ingredient does not have)
#         for acute_hazard_class in hazards.acute_toxicity_class_list:
#
#             try:
#                 hazard_category = ingredient.hazard_set.get(hazard_class__python_class_name = acute_hazard_class.__name__)
#                 ld50 = IngredientCategoryInfo.objects.get(ingredient = ingredient, category = hazard_category).ld50
#             except:
#                 ld50 = None
#
#             hazard_dict[acute_hazard_class.__name__].append(fli)
#
#             if ld50 == None:
#                 if weight/total_weight * 100 > 10:
#                     hazard_dict[acute_hazard_class.unknown_weight_key] += weight
#             elif ld50 < acute_hazard_class.max_ld50:
#                 hazard_dict[acute_hazard_class.__name__] += weight/ld50

        #non acute hazards (only hazards that the ingredient has)

#             show_details_logger.info('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' \
#                         % (ingredient.cas, ingredient.name, weight, hazard_category.hazard_class.human_readable_name, hazard_category.category))

    return hazard_dict
