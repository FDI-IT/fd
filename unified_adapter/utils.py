import re

from decimal import Decimal

from xlrd import open_workbook

from unified_adapter.models import ProductInfo, import_applications

boolean_pattern = re.compile("y|yes|x", re.I)
def parse_boolean_field(field_value):
    if field_value == True:
        return True
    elif field_value == False:
        return False
    
    try:
        match = boolean_pattern.match(field_value.strip())
    except AttributeError:
        return True
    
    if match:
        return True
    else:
        return False
    
def parse_string_field(field_value):
    try:
        return unicode(field_value.strip())
    except:
        return ""
    
def parse_decimal_field(field_value):
    try:
        return Decimal(str(field_value))
    except:
        return Decimal('0')
    
def parse_integer_field(field_value):
    try:
        return int(field_value)
    except:
        return 0

"""Static info from Norma's sheet
"""
key_index = {
    'allergens':(-1,),
    'approved_promote':(9,parse_string_field),
    'concentrate':(26,parse_boolean_field),
    'customer':(33,parse_string_field),
    'description':(35,parse_string_field),
    'dry':(28,parse_boolean_field),
    'duplication':(23,parse_boolean_field),
    'emulsion':(27,parse_boolean_field),
    'experimental_number':(5,parse_integer_field),
    'export_only':(24,parse_string_field),
    'flash':(30,parse_decimal_field),
    'gmo_free':(15,parse_boolean_field),
    'heat_stable':(21,parse_boolean_field),
    'initials':(6,parse_string_field),
    'keyword_1':(2,parse_string_field),
    'keyword_2':(3,parse_string_field),
    'kosher':(16,parse_string_field),
    'liquid':(25,parse_boolean_field),
    'location_code':(11,parse_string_field),
    'memo':(34,parse_string_field),
    'microsensitive':(-1,),
    'name':(4,parse_string_field),
    'nat_art':(0,parse_string_field),
    'no_diacetyl':(20,parse_boolean_field),
    'no_msg':(18,parse_boolean_field),
    'no_pg':(19,parse_boolean_field),
    'nutri_on_file':(-1,),
    'organic':(14,parse_boolean_field),
    'organoleptic_properties':(-1,),
    'oil_soluble':(29,parse_boolean_field),
    'percentage_yield':(-1,),
    'production_number':(7,parse_integer_field),
    'prop65':(17,parse_boolean_field),
    'same_as':(8,parse_string_field),
    'sold':(10,parse_boolean_field),
    'solubility':(-1,),
    'specific_gravity':(31,parse_decimal_field),
    'testing_producedure':(-1,),
    'transfat':(-1,),
    'unitprice':(-1,),
}



def get_sheet(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    re_init()
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    return sheet

def scan_objects(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    production_numbers = {}
    experimental_numbers = {}
    
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    
    for x in range(2, sheet.nrows):
        print x
        r = sheet.row(x)
        production_number = r[7].value
        if production_number != "":
            try:
                production_numbers[production_number] += 1
            except:
                production_numbers[production_number] = 1
        experimental_number = r[5].value
        if experimental_number != "":
            try:
                experimental_numbers[experimental_number] += 1
            except:
                experimental_numbers[experimental_number] = 1
                
    return (production_numbers, experimental_numbers)

def update_location_codes(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    
    for x in range(1, sheet.nrows):
        r = sheet.row(x)
        
        
        
def import_objects(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    re_init()
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    
    for x in range(1, sheet.nrows):
        r = sheet.row(x)
        
        pi = ProductInfo()
        for k,v in key_index.iteritems():
            try:
                if v[0] != -1:
                    field_value = r[v[0]].value
                    if field_value == "":
                        pass #defer to default
                    else:
                        pi.__setattr__(k,v[1](field_value))
            except:
                print k
                print v
        pi.save()
    for pi in ProductInfo.objects.all():
        pi.initials = pi.initials.upper()
        pi.save()
    import_applications()
    #import_allergens()
#    
#def parse_row(row):
#    
#    print flavor_number
#    try:
#        f = Flavor.objects.get(number=flavor_number)
#    except Flavor.DoesNotExist:
#        print "Does not exist: %s" % row[FLAVOR_NUMBER]
#        return
#    except ValueError:
#        print "Invalid production number: %s" % row[FLAVOR_NUMBER]
#        return 
#    
#    for app in app_types:
#        
#        try:
#            usage_level = row[app[APP_LEVEL]].value
#            usage_level = Decimal(str(usage_level))
#        except:
#            usage_level = 0
#        try:
#            memo = row[app[APP_MEMO]].value
#        except:
#            memo = ""

#        
#        if usage_level != 0 or memo != '':
#            print app[APP_NAME]
#            print 'usage level: "%s" -- memo: "%s"' % (usage_level, memo)
#            application = Application(flavor=f,
#                    application_type=app[APP_OBJ],
#                    usage_level=usage_level,
#                    memo=memo
#                )
#            application.save()
#    
#    
def re_init():
    ProductInfo.objects.all().delete()
    