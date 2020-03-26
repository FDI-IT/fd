import re, copy, collections, decimal, logging, ast
from xlrd import open_workbook

from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models import Sum

from hazards.models import GHSIngredient, IngredientCategoryInfo, HazardAccumulator, HazardCategory, HazardClass
from hazards.utils import acute_toxicity_list, hazard_list, cas_re, gas_re, solution_re
from hazards.mylogger import get_my_logger
from hazards.initial_data import HazardClassDict, get_hazard_class_dict_copy, CategoryTestRow, SubcategoryTestRow
from hazards.initial_data import HCodeDict, pcode_dict
from hazards import hazard_classes

#instantiate logger
my_logger = get_my_logger()

HazardClassDictCOPY = get_hazard_class_dict_copy()


def update_hazard_dict_with_flammable_hazards(hazard_dict, flashpoint):
    if flashpoint == 0:
        pass
    elif flashpoint <= 73.4:
        hazard_dict['FlammableLiquidHazard'] = '2'
    elif flashpoint <= 140:
        hazard_dict['FlammableLiquidHazard'] = '3'
    elif flashpoint < 199.4:
        hazard_dict['FlammableLiquidHazard'] = '4'
    
    return hazard_dict

def calculate_flavor_hazards(formula_list):

    accumulator = HazardAccumulator(formula_list)

    hazard_dict = {}

    #calculate categories
    for hazard_class in HazardClassDictCOPY:
        #create hazard specific accumulator before proceeding
        
        my_accumulator = hazard_classes.__dict__[hazard_class].get_my_accumulator()
        accumulator.set_accumulation_dict(my_accumulator)
        
        for category in HazardClassDictCOPY[hazard_class]:
                        
            hazard_category_info = HazardClassDictCOPY[hazard_class][category]
            if hazard_category_info.category_test.test(accumulator):
                hazard_dict[hazard_class] = category

                #ADD RELEVANT LD50S TO THE HAZARD_DICT
                ld50_field = getattr(hazard_category_info.category_test, 'ld50_field', None)
                if ld50_field:
                    hazard_dict[ld50_field] = accumulator[ld50_field]

                break
        if hazard_class not in hazard_dict:
            hazard_dict[hazard_class] = 'No'

    #calculate subcategories
    for hazard_class in hazard_dict:

        if 'ld50' not in hazard_class: #don't attempt to get categories of ld50s

            category = hazard_dict[hazard_class]

            subcategory = ''
            if category != 'No':

                subcategories = HazardClassDict[hazard_class][category].subcategories
                if subcategories != ('',):  #only calculate subcategory if there are subcategories...

                    for subcat in subcategories[1:]:
                        accumulation_dict_key = '%s_%s%s' % (hazard_class, category, subcat)

                        #Check the accumulation dict for each subcategory; subcategories are ordered from most to least hazardous,
                        # so the first subcategory found will be appended to the hazard's category
                        if accumulation_dict_key in accumulator.accumulation_dict:
                            subcategory = subcat
                            break

            hazard_dict[hazard_class] += subcategory


    return hazard_dict



#Todo: don't have two separate functions... this one does the same as above but more, and returns more stuff
def calculate_flavor_hazards_with_work(formula_list):

    accumulator = HazardAccumulator(formula_list)

    hazard_dict = {}

    #find categories

    for hazard_class in HazardClassDictCOPY:
        if hazard_class != 'FlammableLiquidHazard':
            my_accumulator = hazard_classes.__dict__[hazard_class].get_my_accumulator()
            accumulator.set_accumulation_dict(my_accumulator)        
    
            cat, category_calculation_rows = get_category_and_work(accumulator, hazard_class)
            relevant_component_rows = get_relevant_component_rows(accumulator, hazard_class)
            
            hazard_dict[hazard_class] = {'category': cat, 'show_work_rows': category_calculation_rows, 'relevant_components': relevant_component_rows}
            
    #find subcategories
    for hazard_class in hazard_dict:

#         my_accumulator = hazard_classes.__dict__[hazard_class].get_my_accumulator()
#         accumulator.set_accumulation_dict(my_accumulator)

        category = hazard_dict[hazard_class]['category']

        subcategory, subcategory_calculation_rows = get_subcategory_and_work(accumulator, hazard_class, category)

        hazard_dict[hazard_class]['category'] += subcategory
        hazard_dict[hazard_class]['subcategory_calculation_rows'] = subcategory_calculation_rows

    return hazard_dict

def get_category_and_work(accumulator, hazard_class):

    category_calculation_rows = []

    cat = 'No'
    category_found = False

    for category in HazardClassDictCOPY[hazard_class]:

        hazard_category_info = HazardClassDictCOPY[hazard_class][category]
        category_test = hazard_category_info.category_test

        result = 'Fail'
        if category_test.test(accumulator):
            result = 'Pass'

        category_calculation_rows.append(
            CategoryTestRow(
                test = category_test.render_test(),
                value = category_test.value(accumulator),
                category = category,
                result = result,
                category_found = category_found,
        ))

        if result == 'Pass' and category_found == False:
            cat = category
            category_found = True

    return cat, category_calculation_rows

def get_subcategory_and_work(accumulator, hazard_class, category):

    subcategory = ''
    subcategory_calculation_rows = []

    if category != 'No':

        subcategories = HazardClassDict[hazard_class][category].subcategories
        if subcategories != ('',):  #only calculate subcategory if there are subcategories...

            subcategory_found = False  #keeps track of when a subcategory is found, return first one found
            for subcat in subcategories[1:]:
                accumulation_dict_key = '%s_%s%s' % (hazard_class, category, subcat)

                result = 'No'
                if accumulation_dict_key in accumulator.accumulation_dict:
                    result = 'Yes'

                subcategory_calculation_rows.append(
                    SubcategoryTestRow(
                        hazard = accumulation_dict_key.replace('_',' '),
                        result = result,
                        subcategory = subcat,
                        subcategory_found = subcategory_found,
                    )
                )

                if result == 'Yes' and subcategory_found == False:
                    subcategory = subcat
                    subcategory_found = True

    return subcategory, subcategory_calculation_rows


def get_highest_weight_hazardous_component(accumulator, hazard_class):
    
    highest_weight = 0
    relevant_components = get_relevant_components(accumulator, hazard_class)
    
    for hazard, fli in relevant_components:
        if fli.weight > highest_weight:
            highest_weight = fli.weight
            most_prevalent_ingredient = GHSIngredient.objects.get(cas=fli.cas)
            
    return most_prevalent_ingredient.name, str(round(highest_weight/accumulator.total_weight * 100, 4)) + '%'
            
    
    #get weights of all relevant components and get the highest one

def get_relevant_component_rows(accumulator, hazard_class):
    
    relevant_component_rows = []

    #We need to make sure to 'remove' duplicate weights (just highlight them in red, the actual math is done in the accumulate_weights function
    #This should only occur in Eye Damage Hazard, since it's the only hazard which is based on multiple hazard accumulations
    #appended_fli_list will keep track of all rows, we need to look at (fli.cas, fli.source_name) pairings because multiple FD ingredients might have the same cas
    #and those should still all be accumulated
        
    appended_fli_list = []
    
    relevant_components = get_relevant_components(accumulator, hazard_class)
    
    for hazard, fli in relevant_components:

        hclass, category = hazard.split('_')
        
        ingredient = fli.ingredient
        
        try:
            ld50 = ingredient.fdiingredientcategoryinfo_set.filter(category__category=category).get(\
                category__hazard_class__python_class_name=hclass).ld50
            if ld50 == None:
                ld50 = 'N/A'
        except:
            ld50 = 'N/A'
        
        if ingredient in appended_fli_list and hclass != 'TOSTSingleHazard':
            duplicate = True
        else:
            duplicate = False
            appended_fli_list.append(ingredient)
            
        relevant_component_rows.append((
            hclass,
            category,
            ld50,
            ingredient.cas,
            ingredient.__unicode__(),
            fli.weight,
            str(fli.weight/accumulator.total_weight * 100) + '%',
            duplicate
        ))
    
    return relevant_component_rows
    
#new relevant_components function, use it in get_relevant_component_rows and get_most_prevalent_relevant_component functions
def get_relevant_components(accumulator, hazard_class):
    
    relevant_components = []
    subhazard_dict = accumulator.subhazard_dict
    
    for hazard in subhazard_dict:
        if (hazard_class in hazard) or ((hasattr(hazard_classes.__dict__[hazard_class], 'relevant_hazards')) and (any(rel_haz in hazard for rel_haz in hazard_classes.__dict__[hazard_class].relevant_hazards))):
             
             for fli in subhazard_dict[hazard]:
                 relevant_components.append((hazard, fli))
    
    return relevant_components
    
# def get_relevant_components_old(accumulator, hazard_class):
# 
#     relevant_component_rows = []
#     appended_fli_list = []
# 
#     subhazard_dict = accumulator.subhazard_dict
# 
#     #keys in subhazard dict: hazardclass_category
#     for hazard in subhazard_dict:
#         #Check if the hazard class matches the hazard, or if any relevant component hazards (if any exist for the hazard_class) are in hazard
#         if (hazard_class in hazard) or ((hasattr(hazards.__dict__[hazard_class], 'relevant_hazards')) and (any(rel_haz in hazard for rel_haz in hazards.__dict__[hazard_class].relevant_hazards))):
#             hclass, category = hazard.split('_') #here hclass could be the class of a relevant component of hazard_class
# 
#             for fli in subhazard_dict[hazard]:
# 
#                 ingredient = GHSIngredient.objects.get(cas=fli.cas)
# 
#                 try:
#                     ld50 = ingredient.ingredientcategoryinfo_set.filter(category__category=category).get(\
#                         category__hazard_class__python_class_name=hclass).ld50
#                     if ld50 == None:
#                         ld50 = 'N/A'
#                 except:
#                     ld50 = 'N/A'
# 
#                 if fli.cas in appended_fli_list and hclass != 'TOSTSingleHazard': #excluding tostsinglehazard because a single ingredient can have two different categories...(3-RI, 3-NE)
#                     duplicate = True
#                 else:
#                     duplicate = False
#                     appended_fli_list.append(fli.cas)
# 
#                 relevant_component_rows.append((
#                     hclass,
#                     category,
#                     ld50,
#                     fli.cas,
#                     ingredient.name,
#                     fli.weight,
#                     str(fli.weight/accumulator.total_weight * 100) + '%',
#                     duplicate
#                 ))
#                 
#                 
# 
#     return relevant_component_rows
#                 

def print_sds(hazard_dict):
    pass

    

    
@transaction.atomic
def import_GHS_ingredients_from_document(path_to_document):
    """
    This function is used to import GHS Ingredient hazard information from a document.
    This function will delete ALL existing GHS Ingredient information in the database
    and replace it with the hazard information from the given document.
    
    There are two options for doing this:
        1. Call this function from a shell.
        2. Use the management command 'import_hazards' from the project directory
        
        In either case, pass the path to the hazard document as an argument.
    
    """
    
    savepoint = transaction.savepoint()

    GHSIngredient.objects.all().delete()

    import_initial_data()

    labels = open_workbook(path_to_document)
    sheet = labels.sheets()[0]    

    multiplephase_list = []
    invalid_ld50_list = []
    invalid_category_list = []

    #start a transaction, save stuff, if multiple phase errors then rollback, otherwise commit transaction
    for row in range(sheet.nrows):
        
        try:    
            g = import_row(sheet, row)
            if g == None: #this happens when it's not a cas number row
                pass
            else:
                g.save()
                
        except MultiplePhaseError as e:
            multiplephase_list.append(e.cas)

        except InvalidLD50Error as e:
            invalid_ld50_list.append((e.cas, e.error_str))

        except InvalidCategoryError as e:
            invalid_category_list.append((e.cas, e.error_str))

        #print invalid_category_list

    if multiplephase_list or invalid_ld50_list or invalid_category_list:

        transaction.savepoint_rollback(savepoint)

        my_logger.warning("ERRORS:\n")

        if multiplephase_list:
            my_logger.warning("The following cas numbers contain multiple sets of hazards.  Alter the input document to have only one set of hazards per cas number.\n%s\n" % ', '.join(multiplephase_list))

        if invalid_ld50_list:
            my_logger.warning("The following cas numbers have invalid ld50s for Acute Toxicity Inhalation (ATI). ")

            for cas, error_str in invalid_ld50_list:
                my_logger.warning("%s: %s" % (cas, error_str))

        if invalid_category_list:
            my_logger.warning("The following cas numbers have invalid categories.  \nMake sure the category in the document matches EXACTLY with one of the potential categories below.")

            for cas, error_str in invalid_category_list:
                my_logger.warning("%s: %s" % (cas, error_str))

        my_logger.warning("\nIngredients were not imported.\nFix these errors in the input document and import again.")

    else:
        #create placeholder ingredient here
        p = GHSIngredient(cas = '00-00-00')
        p.name = 'Placeholder Ingredient (no hazards)'
        p.save()

        p2 = GHSIngredient(cas = '00-00-1')
        p2.name = 'Non-Hazardous Ingredient'
        p2.save()

        my_logger.warning("Ingredients imported successfully.")
        transaction.savepoint_commit(savepoint)
        

class InvalidLD50Error(Exception):
    def __init__(self, error_str, cas=None):
        self.cas = cas
        self.error_str = ast.literal_eval(error_str)[0]
    def __str__(self):
        if self.cas != None:
            return "Cas number: %s, %s" % self.cas, self.error_str


class MultiplePhaseError(Exception):
    def __init__(self, cas=None):
        self.cas = cas

    def __str__(self):
        if self.cas != None:
            return "Cas number: %s, MultiplePhaseError" % self.cas

class InvalidCategoryError(Exception):
    def __init__(self, error_str, cas=None):
        self.cas = cas
        self.error_str = error_str

    def __str__(self):
        if self.cas != None:
            return "Cas number: %s, %s" % self.cas, self.error_str
    
def import_row(sheet, row):
    """
    This function is a helper function for the main import function 'import_GHS_ingredients_from_document'.
    It takes one of the rows of the document as an input, and returns the list of hazards that are specified in that row.
    """

    cas_number = sheet.cell(row, 0).value

    #ignore rows that do not contain a cas number (table headers, footnote rows, etc)
    if cas_re.search(cas_number):
        
        g_dict = {}
        
        g_dict['cas'] = cas_number
        g_dict['reach'] = sheet.cell(row, 1).value
        g_dict['name'] = sheet.cell(row, 2).value
        g_dict['ghs_hazard_category'] = sheet.cell(row, 3).value
        g_dict['ghs_change_indicators'] = sheet.cell(row, 4).value
        g_dict['ghs_signal_words'] = sheet.cell(row, 5).value
        g_dict['ghs_codes'] = sheet.cell(row, 6).value
        g_dict['ghs_pictogram_codes'] = sheet.cell(row, 7).value
        g_dict['synonyms'] = sheet.cell(row, 8).value


        g = GHSIngredient(**g_dict)

        #need to save object before adding objects to many-to-many relationship
        g.save()

        ingredient_hazard_dict = parse_ghs_hazard_category_cell(g_dict['ghs_hazard_category'], cas_number)

        for hazard, value_dict in ingredient_hazard_dict.iteritems():

            #print hazard, value

            #print cas_number, hazard, value_dict['category']

            try:
                category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                                .get(category=value_dict['category'])
            except ObjectDoesNotExist:
                potential_tokens = HazardClass.objects.get(python_class_name=hazard).python_hazard_class.potential_tokens
                raise InvalidCategoryError("Hazard: %s, Potential Tokens: %s" % (hazard, ", ".join(potential_tokens)), cas_number)

                # print
                #
                # print cas_number, hazard, value_dict['category']
                #
                # category = HazardCategory.objects.filter(hazard_class__python_class_name=hazard)\
                #                 .get(category=value_dict['category'] + 'A')

            ing_cat_info = IngredientCategoryInfo(
                ingredient = g,
                category = category,
                ld50 = value_dict['ld50']
            )

            try:
                ing_cat_info.save()
            except ValidationError as e:
                raise InvalidLD50Error(e.__str__(), cas_number)


        return g
    
    #else, None is returned





def parse_ghs_hazard_category_cell(cell_contents, cas_number):
    """Parses the 'tokens' found in the input document and determines the hazards they correspond to.

    :param cell_contents: contents of a cell to be parsed
    :param cas_number: the current ingredient's cas number
    :return: a list of the ingredient's hazards (and categories)

    """

    """
    This function actually parses the 'tokens' found in the document.
    
    It is given the actual string contents of a cell, and it returns a dictionary of hazards that 
    any of the tokens in the cell correspond to (if there are any).
    """


    cell_contents = cell_contents
    
    #currently, if both gas AND solution are found in the contents, error is raised
    #so if they delete one it'll work.
    #however, if in the future someone puts in something other than gas or solution 
    #the multiple sets won't be detected
    if gas_re.search(cell_contents) and solution_re.search(cell_contents): #should i do and?  or OR? 
        raise MultiplePhaseError(cas_number)
    
    

    hazard_list = []

    for hazard_class in HazardClass.objects.all():

        python_hazard_class = hazard_class.python_hazard_class

        hazards_found = python_hazard_class.process_re(cell_contents)
        handle_duplicate_hazards(hazards_found, cas_number) #this will delete any duplicates
        hazard_list += hazards_found #add the hazards found to the hazard_list

    hazard_dict = {}
    for hazard, category in hazard_list:
        hazard_dict[hazard] = category
    
    return hazard_dict
    
  
        


def handle_duplicate_hazards(hazard_list, cas_number):
    '''
    In the case of duplicate hazards, we just want to save the more severe category and
    ignore the lesser category.
    '''
    duplicate_dict = {}
    for hazard, value_dict in hazard_list:
        if hazard not in duplicate_dict:
            duplicate_dict[hazard] = [value_dict['category'],]
        else:
            duplicate_dict[hazard].append(value_dict['category'])

    for hazard, potential_categories in duplicate_dict.iteritems():
        if len(potential_categories) > 1:

            if hazard == 'TOSTSingleHazard' and potential_categories == ['3NE', '3RI']:
                pass

            else:
                my_logger.warning("Found duplicate hazards for CAS number %s" % cas_number)
                my_logger.warning("Hazard: %s, Potential Categories: %s" % (hazard, potential_categories))

                lowest_index = 1000000 #any number > 7 will work
                for category in potential_categories:

                    index = HazardClassDict[hazard].keys().index(category)

                    if index < lowest_index:
                        lowest_index = index

                    try:
                        hazard_list.remove((hazard, category))
                    except:
                        pass

                most_hazardous_category = HazardClassDict[hazard].keys()[lowest_index]

                #append the hazard with its most hazardous category
                hazard_list.append((hazard, {'category': most_hazardous_category, 'ld50': None}))

                my_logger.warning("Using most hazardous category: (%s: %s)\n" % (hazard, most_hazardous_category))


def import_initial_data():

    HazardCategory.objects.all().delete()
    HazardClass.objects.all().delete()

    for hazard_class_name, category_info_dict in HazardClassDict.iteritems():
        hazard_class = HazardClass(python_class_name = hazard_class_name,
                         human_readable_name = hazard_classes.__dict__[hazard_class_name].human_readable_field)
        hazard_class.save()

        for category, hazard_category_info in category_info_dict.iteritems():

            for subcategory in hazard_category_info.subcategories:

                hazard_category = HazardCategory(
                    hazard_class = hazard_class,
                    category = category + subcategory
                )

                hazard_category.save()



def evaluate_summation_row_strings():

    string_list = []

    for hazard_class in HazardClass.objects.all():
        python_class = hazard_class.python_hazard_class

        for row in python_class.calculation_table:
            string_list.append(row[0])

    eval_dict = {}

    for string in string_list:
        eval_dict[string] = eval(string)

    return eval_dict

def get_ellipsis_pcodes():
    
    pcode_list = []
    for pcode, statement in pcode_dict.iteritems():
        if '...' in statement:
            pcode_list.append(pcode)
            
    return pcode_list

def pcode_test():
    for hcode in HCodeDict:
        for pcode in HCodeDict[hcode]['p_codes']:
            if pcode not in pcode_dict:
                print '%s: %s' % (hcode, pcode)
                
def get_hazard_from_statement(statement):
    
    for hcode, data in HCodeDict.iteritems():
        if data['statement'] == statement:
            statement_hcode = hcode
            break
    
    hazard_category_list = []
            
    for hazard_class, data in HazardClassDict.iteritems():
        for category, info in data.iteritems():
            if info.hcode == statement_hcode:
                #hazard_category_list.append(hazard_class)
                hazard_class_name = hazard_class
                hazard_category_info = info
    
    #right now, only returning the hazard that contains the hcode
    #there are a few instances where multiple categories will have the same hcode
    #i might want to return all categories that have the hcode
    #also consider returning the entire HazardCategoryInfo object
#     return hazard_category_list
    return hazard_class_name, hazard_category_info

    
    
    
                
                

