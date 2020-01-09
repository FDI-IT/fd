import csv
import unicodedata

import reversion

from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from access.models import Flavor, PurchaseOrderLineItem, LeafWeight, Supplier, ExperimentalLog, Formula
from newqc.models import Retain, RMRetain
from hazards.models import GHSIngredient

from django.db import transaction

#output an excel spreadsheet from a django queryset.  field_list is a list of any object attributes that should be output
def print_list_from_queryset(queryset, field_list, order_by_field=None, document_name='list.csv'):
    w = csv.writer(open(document_name, 'wb'), delimiter=",", quotechar='"')

    w.writerow(field_list)

    for object in queryset.order_by(order_by_field):
        row = []
        for field in field_list:
            row.append(unicodedata.normalize('NFKD', getattr(object, field)).encode('ascii','ignore'))
        w.writerow(row)

#output an excel spreadsheet from a list of lists.  this just makes it easier to print a list from the shell
def print_list(print_list, document_name):
    w = csv.writer(open(document_name, 'wb'), delimiter=",", quotechar='"')

    for list in print_list:
        row = []
        for value in list:
            row.append(unicodedata.normalize('NFKD', value).encode('ascii','ignore')) #convert any unicode to ascii for output purposes
        w.writerow(row)

def get_flavors_using_raw_material_primary(ingredient_list, exclude_ingredient=None):
    from access.models import Formula
    flavor_set = set()
    for formula in Formula.objects.filter(ingredient=ingredient_list[0]):
        current_flavor = formula.flavor
        if len(ingredient_list) > 1:
            if Formula.objects.filter(flavor=current_flavor,ingredient=ingredient_list[1]).exists():
                flavor_set.add(current_flavor)
        elif exclude_ingredient is not None:
            if Formula.objects.filter(flavor=current_flavor,ingredient=exclude_ingredient).exists():
                pass
            else:
                flavor_set.add(current_flavor)
        else:
            #this statement should never be hit because there will either be two key ngredients or one exclude_ingredient
            flavor_set.add(current_flavor)
            print(2/0)
    return flavor_set


def print_experimentals_with_recent_retains():
    experimental_list = []

    for ex in ExperimentalLog.objects.exclude(flavor=None):
        if Retain.objects.filter(lot__flavor__in=ex.flavor.loaded_renumber_list).filter(date__gte=datetime(2013,0o1,0o1)).count() > 2:
            experimental_list.append(ex)

    w = csv.writer(open('experimental_list.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['Number/Initials', 'Product Name'])

    for ex in experimental_list:
        w.writerow([unicodedata.normalize('NFKD', '%s-%s' % (ex.experimentalnum, ex.initials)).encode('ascii','ignore'),
                    unicodedata.normalize('NFKD', '%s %s %s' % (ex.natart, ex.product_name, ex.label_type)).encode('ascii','ignore')])


def print_suppliers():
    #Iterate through purchase order line items created in 2014 and later
    #Get suppliers through the purchase order
    #Add suppliers to a dictionary where the key is the supplier name, and value is the most recent purchased raw material
    #If the same supplier is encountered, compare the raw materials and put the most recent purchased raw material as value

    supplier_dict = {}

    for poli in PurchaseOrderLineItem.objects.filter(date_received__gte=datetime(2014,0o1,0o1)):
        if poli.po.supplier not in supplier_dict:
            supplier_dict[poli.po.supplier] = poli.date_received
        else:
            if poli.date_received > supplier_dict[poli.po.supplier]:
                supplier_dict[poli.po.supplier] = poli.date_received


    w = csv.writer(open('supplier_list.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['Supplier', 'Contact Name', 'Last Purchase Date'])

    #cas_number_discrepancy_list.sort(key=lambda x: x[1], reverse=True)
    supplier_list = sorted(list(supplier_dict.items()), key=lambda x: x[1], reverse=True)

    for supplier, last_purchase_date in supplier_list:
        w.writerow([unicodedata.normalize('NFKD', supplier.suppliername).encode('ascii','ignore'),
                    unicodedata.normalize('NFKD', supplier.contactname).encode('ascii','ignore'),
                    last_purchase_date.strftime('%m/%d/%Y')])

def print_purchased_raw_materials():
    w = csv.writer(open('raw_material_list.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['PIN', 'RM Code', 'Name'])

    rm_list = []
    for poli in PurchaseOrderLineItem.objects.filter(date_received__year='2015'):
        if poli.raw_material not in rm_list:
            rm_list.append(poli.raw_material)

    rm_list = sorted(rm_list, key =lambda item: item.id)

    for rm in rm_list:
        w.writerow([rm.id, rm.rawmaterialcode, unicodedata.normalize('NFKD', rm.product_name).encode('ascii','ignore')])

def print_product_allergens():
    w = csv.writer(open('allergens.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['#', 'Name', 'Allergens'])
    for fl in Flavor.objects.filter(valid=True, approved=True, sold=True).exclude(allergen='None'):
        name = unicodedata.normalize('NFKD', fl.name).encode('ascii', 'ignore')
        w.writerow([fl.number, name, fl.allergen])

def print_flavor_names():
    w = csv.writer(open('flavor_list.csv', 'wb'), delimiter=",", quotechar='"')
    flavor_name_set = set()

    for fl in Flavor.objects.filter(sold=True,approved=True,valid=True).distinct():
        flavor_name_set.add(unicodedata.normalize('NFKD', fl.name).encode('ascii', 'ignore'))

    for flavor_name in flavor_name_set:
        w.writerow([])

def print_flavor_names_with_prefixes():
    w = csv.writer(open('numbered_flavor_list.csv', 'wb'), delimiter=",", quotechar='"')
    flavor_name_set = set()

    twoyearsago = datetime.now().date() - relativedelta(years=2)

    for fl in Flavor.objects.filter(sold=True,approved=True,valid=True).distinct():
        if fl.lot_set.exists() and fl.lot_set.all()[0].date >= twoyearsago:
            flavor_name_set.add((fl.prefix, fl.number, unicodedata.normalize('NFKD', fl.name).encode('ascii', 'ignore')))

    for prefix, number, name in flavor_name_set:
        w.writerow([prefix, number, name])

def print_cas_number_discrepancies():
    cas_number_discrepancy_list = []

    for ing in Ingredient.objects.filter(sub_flavor=None,discontinued=False).exclude(cas=''):
        if not GHSIngredient.objects.filter(cas=ing.cas).exists():
            related_product_count = LeafWeight.objects.filter(ingredient=ing, root_flavor__sold=True,root_flavor__valid=True,root_flavor__approved=True).count()
            cas_number_discrepancy_list.append((ing, related_product_count))

    cas_number_discrepancy_list.sort(key=lambda x: x[1], reverse=True)

    w = csv.writer(open('cas_number_discrepancies.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['PIN', 'Name', '# of Products Containing this Ingredient', 'Current CAS Number'])

    for ing, product_count in cas_number_discrepancy_list:
        w.writerow([ing.id, ing, product_count, ing.cas])

def print_flavors_with_flashpoints_over_threshold(threshold):
    w = csv.writer(open('micro_and_flash_over_141.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['Flavor', 'Flashpoint'])


    for fl in Flavor.objects.filter(sold=True,approved=True,valid=True,microtest__icontains='yes',flashpoint__gte=141):
        w.writerow([fl.long_name, fl.flashpoint])

def print_cancerous_ingredients():
    w = csv.writer(open('carcinogenicity_hazard_raw_materials.csv','wb'), delimiter=",", quotechar='"')

    carcinogenicity_hazard_categories = HazardCategory.objects.filter(hazard_class__python_class_name='CarcinogenicityHazard')

    for ghs_ingredient in GHSIngredient.objects.all():
        ingredient_carcinogenicity_hazard = [ch for ch in ghs_ingredient.hazard_set.all() if ch in carcinogenicity_hazard_categories]
        if ingredient_carcinogenicity_hazard and Ingredient.objects.filter(cas=ghs_ingredient.cas).exists():
            fdi_ingredient = Ingredient.objects.get(cas=ghs_ingredient.cas)
            w.writerow([fdi_ingredient, ingredient_carcinogenicity_hazard, LeafWeight.objects.filter(ingredient=fdi_ingredient,root_flavor__valid=True,root_flavor__approved=True,root_flavor__sold=True)])



def print_products_by_pr(threshold):
    flavor_list = []
    twoyearsago = datetime.now().date() - relativedelta(years=2)


    for fl in Flavor.objects.filter(sold=True):
        if fl.lot_set.exists() and fl.lot_set.all()[0].date >= twoyearsago:
            try:
                if fl.unitprice != 0 and fl.unitprice/fl.rawmaterialcost < threshold :
                    flavor_list.append(fl)
            except:
                print("Flavor %s, up: %s, rmc: %s" % (fl, fl.unitprice, fl.rawmaterialcost))

    w = csv.writer(open('profitratio_list.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['#', 'Name', 'Profit Ratio', 'Parent Flavor', 'Most Recent Lot'])

    for fl in flavor_list:

        most_recent_lot_date = fl.lot_set.all()[0].date

        name = unicodedata.normalize('NFKD', fl.name).encode('ascii', 'ignore')
        w.writerow([fl.number, name, round(fl.unitprice/fl.rawmaterialcost, 3), '-', most_recent_lot_date])

        for g in fl.get_gazintas():

            if not g.lot_set.all().exists():
                lot_date_gazinta = "No Lots"
            else:
                lot_date_gazinta = g.lot_set.all()[0].date

            try:
                if g.unitprice != 0 and g.unitprice/g.rawmaterialcost < threshold:

                    w.writerow([g.number, unicodedata.normalize('NFKD', g.name).encode('ascii', 'ignore'), round(g.unitprice/fl.rawmaterialcost, 3), fl.number, lot_date_gazinta])
            except:
                "Gazinta %s: up %s, rmc %s" % (g, g.unitprice, g.rawmaterialcost)

#from hazards import hazard_classes
from hazards.models import HazardAccumulator
from hazards.initial_data import HazardClassDict, get_hazard_class_dict_copy, CategoryTestRow
from hazards.tasks import get_hazard_from_statement, get_highest_weight_hazardous_component

def print_all_hazard_statements():
    w = csv.writer(open('hazard_statements.csv', 'wb'), delimiter=",", quotechar='"')

    hazardous_flavors = Flavor.objects.filter(sold=True,approved=True,valid=True).filter(hazard_set__isnull=False).distinct()

    statement_set = set()

    for fl in hazardous_flavors:
        statement_set.update(fl.merged_hcode_info['statement'])

    for statement in statement_set:
        w.writerow([statement])

def print_flavor_hazard_report_2(filter_terms, filter_numbers):

    HazardClassDictCOPY = get_hazard_class_dict_copy()

    hazard_report_flavors = []
    hazardous_ingredients = set()

    #get list of sold, approved, and valid hazardous flavors containing those filter statements
    hazardous_flavors = Flavor.objects.filter(sold=True,approved=True,valid=True).filter(hazard_set__isnull=False).filter(number__in=filter_numbers).distinct()

    #find out which filter statements each flavor contains
    for flavor in hazardous_flavors:

        #Only include flavors that have lots created
        if flavor.lot_set.exists():

            if any(flavor.hazard_statements_contain(term) for term in filter_terms):
                formula_list = flavor.get_hazard_formula_list()
                accumulator = HazardAccumulator(formula_list)

    #         formula_list = flavor.get_hazard_formula_list()
    #         accumulator = HazardAccumulator(formula_list)

            hazard_report_rows = []
            term_count = 0
            difference_sum = 0

            for term in filter_terms:

                for hazard_statement in flavor.merged_hcode_info['statement']:
                    if term.lower() in hazard_statement.lower():

                        term_count += 1

                        #here we will get the name of the corresponding hazard, as well as the
                        #HazardCategoryInfo tuple of the least hazardous category that contains the keyword
    #                     hazard_class_name = get_hazard_from_statement(hazard_statement)[0]

                        hazard_class_name, hazard_category_info = get_hazard_from_statement(hazard_statement)

                        my_accumulator = hazards.__dict__[hazard_class_name].get_my_accumulator()
                        accumulator.set_accumulation_dict(my_accumulator)

                        #get hazardous flavor's corresponding hazard and category
                        hazard_category = flavor.hazard_set.get(hazard_class__python_class_name=hazard_class_name)
    #
    #                     #get the corresponding HazardCategoryInfo tuple which contains the test
    #                     hazard_category_info = HazardClassDictCOPY[hazard_category.hazard_class.python_class_name][hazard_category.category]
                        category_test = hazard_category_info.category_test

                        threshold_str = category_test.render_test()

                        if "LD50" in threshold_str:
                            threshold_str = "LD50" + threshold_str.split("LD50")[1]
                        elif "+" in threshold_str:
                            threshold_str = "* >=" + threshold_str.split(">=")[1]
                        else:
                            threshold_str = "S >=" + threshold_str.split(">=")[1]

                        value = category_test.value(accumulator)

                        #when I append '_val' to a variable it means I'm converting it to a float/int from string
                        if "%" in value:
                            value_val = category_test.value_int(accumulator)

                        else:
                            value_val = float(value)

                        threshold_val = float(category_test.threshold)

                        difference = round(abs((threshold_val - value_val)/threshold_val) * 100, 4)

                        difference_sum += difference

                        most_hazardous_ingredient, most_hazardous_ingredient_weight = get_highest_weight_hazardous_component(accumulator, hazard_class_name)

                        hazard_report_rows.append([hazard_statement, hazard_category, threshold_str, value, str(difference)+"%", '%s - %s' % (most_hazardous_ingredient, most_hazardous_ingredient_weight)])

#                         if most_hazardous_ingredient not in hazardous_ingredients:
#                             hazardous_ingredients[most_hazardous_ingredient] = 1
#                         else:
#                             hazardous_ingredients[most_hazardous_ingredient] += 1

                        print("threshold: %s, haz: %s" % (threshold_str, most_hazardous_ingredient))
                        hazardous_ingredients.add((threshold_str, most_hazardous_ingredient, term))
                        print(hazardous_ingredients)

            if hazard_report_rows:
                average_difference = difference_sum/term_count
                print(flavor, hazard_report_rows)
                hazard_report_flavors.append((flavor, term_count, hazard_report_rows, average_difference))

    hazard_report_flavors = sorted(hazard_report_flavors, key=lambda item: (item[1], item[3]))
    #return hazard_report_flavors

    w = csv.writer(open('hazardous_flavor_report.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['Flavor', 'Statement', 'Corresponding Hazard', 'Threshold', 'Value', '% Difference', 'Prevalent Ingredient'])

    for flavor, term_count, report_rows, avg_difference in hazard_report_flavors:

        row_index = 0
        for row in report_rows:
            if row_index == 0:
                flavor_string = '%s %s' % (flavor.number, unicodedata.normalize('NFKD', flavor.name).encode('ascii', 'ignore'))
            else:
                flavor_string = '-'

            w.writerow([flavor_string, row[0], row[1], row[2], row[3], row[4], row[5]])

            row_index += 1

    w2 = csv.writer(open('hazardous_ingredient_list.csv', 'wb'), delimiter=",", quotechar='"')
    w2.writerow(['Ingredient', 'Threshold', 'Keyword'])

    for ingredient, threshold, keyword in hazardous_ingredients:
        w2.writerow([ingredient, threshold, keyword])

    #flavor, term, statement, corresponding hazard/category, threshold, value, highest contrib ingredient, other categories?

    #print out the hcodes which contain those statements
    #print the corresponding hazards
    #print the threshold and current values
    #print related hazardous ingredietns and their percentages within the product

def print_flavor_hazard_report(filter_terms):

    HazardClassDictCOPY = get_hazard_class_dict_copy()

    hazard_report_flavors = []
    hazardous_ingredients = set()

    #get list of sold, approved, and valid hazardous flavors containing those filter statements
    hazardous_flavors = Flavor.objects.filter(sold=True,approved=True,valid=True).filter(hazard_set__isnull=False).distinct()

    #find out which filter statements each flavor contains
    for flavor in hazardous_flavors:

        #Only include flavors that have lots created
        if flavor.lot_set.exists():

            if any(flavor.hazard_statements_contain(term) for term in filter_terms):
                formula_list = flavor.get_hazard_formula_list()
                accumulator = HazardAccumulator(formula_list)

    #         formula_list = flavor.get_hazard_formula_list()
    #         accumulator = HazardAccumulator(formula_list)

            hazard_report_rows = []
            term_count = 0
            difference_sum = 0

            for term in filter_terms:

                for hazard_statement in flavor.merged_hcode_info['statement']:
                    if term.lower() in hazard_statement.lower():

                        term_count += 1

                        #here we will get the name of the corresponding hazard, as well as the
                        #HazardCategoryInfo tuple of the least hazardous category that contains the keyword
    #                     hazard_class_name = get_hazard_from_statement(hazard_statement)[0]

                        hazard_class_name, hazard_category_info = get_hazard_from_statement(hazard_statement)

                        my_accumulator = hazards.__dict__[hazard_class_name].get_my_accumulator()
                        accumulator.set_accumulation_dict(my_accumulator)

                        #get hazardous flavor's corresponding hazard and category
                        hazard_category = flavor.hazard_set.get(hazard_class__python_class_name=hazard_class_name)
    #
    #                     #get the corresponding HazardCategoryInfo tuple which contains the test
    #                     hazard_category_info = HazardClassDictCOPY[hazard_category.hazard_class.python_class_name][hazard_category.category]
                        category_test = hazard_category_info.category_test

                        threshold_str = category_test.render_test()

                        if "LD50" in threshold_str:
                            threshold_str = "LD50" + threshold_str.split("LD50")[1]
                        elif "+" in threshold_str:
                            threshold_str = "* >=" + threshold_str.split(">=")[1]
                        else:
                            threshold_str = "S >=" + threshold_str.split(">=")[1]

                        value = category_test.value(accumulator)

                        #when I append '_val' to a variable it means I'm converting it to a float/int from string
                        if "%" in value:
                            value_val = category_test.value_int(accumulator)

                        else:
                            value_val = float(value)

                        threshold_val = float(category_test.threshold)

                        difference = round(abs((threshold_val - value_val)/threshold_val) * 100, 4)

                        difference_sum += difference

                        most_hazardous_ingredient, most_hazardous_ingredient_weight = get_highest_weight_hazardous_component(accumulator, hazard_class_name)

                        hazard_report_rows.append([hazard_statement, hazard_category, threshold_str, value, str(difference)+"%", '%s - %s' % (most_hazardous_ingredient, most_hazardous_ingredient_weight)])

#                         if most_hazardous_ingredient not in hazardous_ingredients:
#                             hazardous_ingredients[most_hazardous_ingredient] = 1
#                         else:
#                             hazardous_ingredients[most_hazardous_ingredient] += 1

                        print("threshold: %s, haz: %s" % (threshold_str, most_hazardous_ingredient))
                        hazardous_ingredients.add((threshold_str, most_hazardous_ingredient, term))
                        print(hazardous_ingredients)

            if hazard_report_rows:
                average_difference = difference_sum/term_count
                print(flavor, hazard_report_rows)
                hazard_report_flavors.append((flavor, term_count, hazard_report_rows, average_difference))

    hazard_report_flavors = sorted(hazard_report_flavors, key=lambda item: (item[1], item[3]))
    #return hazard_report_flavors

    w = csv.writer(open('hazardous_flavor_report.csv', 'wb'), delimiter=",", quotechar='"')
    w.writerow(['Flavor', 'Statement', 'Corresponding Hazard', 'Threshold', 'Value', '% Difference', 'Prevalent Ingredient'])

    for flavor, term_count, report_rows, avg_difference in hazard_report_flavors:

        row_index = 0
        for row in report_rows:
            if row_index == 0:
                flavor_string = '%s %s' % (flavor.number, unicodedata.normalize('NFKD', flavor.name).encode('ascii', 'ignore'))
            else:
                flavor_string = '-'

            w.writerow([flavor_string, row[0], row[1], row[2], row[3], row[4], row[5]])

            row_index += 1

    w2 = csv.writer(open('hazardous_ingredient_list.csv', 'wb'), delimiter=",", quotechar='"')
    w2.writerow(['Ingredient', 'Threshold', 'Keyword'])

    for ingredient, threshold, keyword in hazardous_ingredients:
        w2.writerow([ingredient, threshold, keyword])

    #flavor, term, statement, corresponding hazard/category, threshold, value, highest contrib ingredient, other categories?

    #print out the hcodes which contain those statements
    #print the corresponding hazards
    #print the threshold and current values
    #print related hazardous ingredietns and their percentages within the product

from access.models import Ingredient
from solutionfixer.models import Solution

def get_solution_cas_numbers():
    for i in Ingredient.objects.filter(sub_flavor=None,cas=''):
        if Solution.objects.filter(ingredient=i).exists():
            sol = Solution.objects.get(ingredient=i)
            try:
                base_ing = Ingredient.objects.get(pk=sol.my_base_id)

                if base_ing.cas != '':
                    i.cas = base_ing.cas
                    i.save()
                    print("Ingredient %s CAS number successfully changed to %s" % (i, i.cas))

            except:
                print("Solution %s has no base id" % sol)

def remove_solution_cas_numbers():

    count = 0
    for i in Ingredient.objects.filter(sub_flavor=None):
        if Solution.objects.filter(ingredient=i).exists():
            sol = Solution.objects.get(ingredient=i)
            if sol.cas != '':
                sol.cas = ''
                count += 1

    print("Removed the CAS number of %s solutions." % count)



@transaction.atomic()
@reversion.create_revision()
def import_additional_cas_numbers(document_path, username):

    #Get user for revision log (will probably always be matta)
    user = User.objects.get(username=username)

    count = 0

    with open(document_path, 'rb') as csvfile:
        f = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in f:
            ingredient_id = row[0]
            if row[4] == 'non-hazardous':
                new_cas = '00-00-1'
                raw_materials = Ingredient.objects.filter(id=ingredient_id)
                #Get both active and discontinued ingredients since they both represent the same ingredient and should have the same hazards
                for raw_material in raw_materials:
                    #Only change the cas if it hasn't already been changed
                    if raw_material.cas != '00-00-1':
                        raw_material.cas = new_cas
                        print('Changing cas of %s to %s' % (raw_material, new_cas))
                        reversion.set_comment("Changing CAS to non-hazardous CAS number 00-00-1.  Old CAS: %s" % row[3])
                        raw_material.save()
                        count += 1
#             elif row[4] == 'pending':
#                 raw_materials = Ingredient.objects.filter(id=ingredient_id)
#                 for raw_material in raw_materials:
#                     raw_material.cas = row[3]
#                     raw_material.save()
#                     count_2 += 1

    print("Total number of cas numbers changed to '00-00-1': %s" % count)

def get_lot_data(flavor, year):

    #get data for flavor and its renumbers

    total_weight = 0
    total_lot_count = 0
    total_sale = 0

    #list of tuples (number, # lots created that year, selling price), will sort from most lots to least
    renumber_lot_distribution = []

    for fl_id in flavor.loaded_renumber_list:
        fl = Flavor.objects.get(id=fl_id)
        lot_set = fl.lot_set.filter(date__year=year).exclude(retains=None)

        if lot_set.exists():
            total_lot_count += lot_set.count()

            for lot in lot_set:
                total_weight += lot.amount
                total_sale += lot.amount * fl.unitprice

            renumber_lot_distribution.append((fl.number, lot_set.count(), fl.unitprice))

        for lot in lot_set:
            total_weight += lot.amount


    if total_lot_count == 0:
        average_lot_weight = 0
    else:
        average_lot_weight = total_weight/total_lot_count

    #sort the renumbers by number of lots created
    renumber_lot_distribution.sort(key=lambda x: x[1], reverse=True)

    renumber_lot_distribution_string = ", ".join(["%s (%s lots, $%s)" % (tup[0], tup[1], tup[2]) for tup in renumber_lot_distribution])

    #get most popular flavor of all renumbers (if any)
    if renumber_lot_distribution:
        best_selling = Flavor.objects.get(number=renumber_lot_distribution[0][0])
    else:
        best_selling = None


    return best_selling, total_weight, "$%s" % total_sale, total_lot_count, average_lot_weight, renumber_lot_distribution_string

def print_end_of_year_report(year):
    #Print 1 list - will contain products that have an average lot weight of at least 20 OR a total lot count of at least 20

    headers = ["Prefix", "Number", "Nat/Art", "Name", "Total Weight %s (lbs)" % year, "Total Sale %s" % year, "# of Lots Sold %s" % year,
                "Avg. Lot Weight %s" % year, "Renumber Lot Distribution"]
    rows = [headers]

    renumber_set = set()

    for fl in Flavor.objects.filter(sold=True).exclude(unitprice=None):
        if fl.id not in renumber_set:
            print(fl)
            renumber_set.update(fl.loaded_renumber_list)
            flavor, total_weight, total_sale, total_lot_count, avg_weight, renumber_lot_distribution = get_lot_data(fl, year)

            if avg_weight >= 20 or total_lot_count > 20:

                rows.append([flavor.prefix, flavor.number, flavor.natart, "%s %s" % (flavor.name, flavor.label_type),
                         total_weight, total_sale, total_lot_count, avg_weight, renumber_lot_distribution])

    final_list = []
    for row in rows:
        final_list.append(list(map(str, row)))

    print_list(final_list, '%s_yearly_report' % year)


def print_retain_costs(year):
    #print out two lists, one for product retains and one for raw material retains
    #six columns - RM number, RM name, price per pound, price of half an ounce, price of bottle, total price of retain

    product_retain_list = []
    rmc_total = 0
    bottle_total = 0
    grand_total = 0

    bottle_price = Decimal(0.48)

    product_retain_list.append(['Retain #', 'Flavor', 'Raw Material Cost (per lb)',
                                'Half Ounce Cost', 'Bottle Price', 'Total Price'])

    for retain in Retain.objects.filter(date__year=year).order_by('retain'):
        half_ounce_price = retain.lot.flavor.rawmaterialcost/32
        total_price = half_ounce_price + bottle_price

        rmc_total += half_ounce_price
        bottle_total += bottle_price
        grand_total += total_price

        product_retain_list.append([str(retain.retain),
                                    str(retain.lot.flavor),
                                    str(retain.lot.flavor.rawmaterialcost),
                                    str(half_ounce_price),
                                    str(bottle_price),
                                    str(total_price)])

    product_retain_list.append(['','','',str(rmc_total), str(bottle_total), str(grand_total)])

    rm_retain_list = []
    rmc_total = 0
    bottle_total = 0
    grand_total = 0

    rm_retain_list.append(['Retain #', 'Ingredient', 'Raw Material Cost (per lb)',
                            'Half Ounce Cost', 'Bottle Price', 'Total Price'])

    for rmretain in RMRetain.objects.filter(date__year=year).order_by('r_number'):
        half_ounce_price = rmretain.related_ingredient.unitprice/32
        total_price = half_ounce_price + bottle_price

        rmc_total += half_ounce_price
        bottle_total += bottle_price
        grand_total += total_price

        rm_retain_list.append([str(rmretain.r_number),
                               rmretain.related_ingredient.__str__(),
                               str(rmretain.related_ingredient.unitprice),
                               str(half_ounce_price),
                               str(bottle_price),
                               str(total_price)])

    rm_retain_list.append(['','','',str(rmc_total), str(bottle_total), str(grand_total)])

    print_list(product_retain_list, 'product_retain_costs.csv')
    print_list(rm_retain_list, 'rm_retain_costs.csv')

def print_unique_rms_in_OTCO_products():
    product_numbers = [161029,161027,161032,161031,161035,161034,161038,161037,161059,161058,161062,161061,161041,
                       161040,161047,161046,161050,161049,161053,161052,161056,161055,161044,161043,161080,161079,
                       161063,161072,161071,161076,161075,142053,142052,161082,161081,161078,161077,161084,161083,
                       161074,161073]
    experimental_numbers = [13422,13451,13450,13421,13494,13473,13472,13395,13394,13293,13294,13323,13322,13294,13296,
                            13419,13418,13345,13346,13482,13481,13484,13479,13478,13318,13367,13366,13429,13428,13417,
                            13416,13400,13399,13290,13424,13389,13457,13456,13413,13412,13259,13317,13432,13431,13291,
                            13498,13520,13521,13523,13524,13540,13539,13546,13549,13550]

    fset = set()
    rm_dict = {}

    for num in product_numbers:
        fset.add(Flavor.objects.get(number=num))
    for exnum in experimental_numbers:
        fset.add(ExperimentalLog.objects.get(experimentalnum=exnum).flavor)

    for fl in fset:
        for lw in LeafWeight.objects.filter(root_flavor=fl):
            if lw.ingredient not in rm_dict:
                rm_dict[lw.ingredient] = {'rm_total_amount': lw.weight, 'product_list': [fl.number]}
            else:
                rm_dict[lw.ingredient]['rm_total_amount'] += lw.weight
                rm_dict[lw.ingredient]['product_list'].append(fl.number)

    rm_list = []
    for k, v in list(rm_dict.items()):
        rm_list.append([k.id,k.art_nati, k.prefix, k.product_name, v['rm_total_amount'], v['product_list']])

    rm_list = sorted(rm_list, key=lambda x: -x[4])

    final_list = []
    for row in rm_list:
        final_list.append([str(x) for x in row])

    print_list('unique_rms_in_otco_products.csv', final_list)
