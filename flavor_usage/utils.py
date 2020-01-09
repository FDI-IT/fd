from decimal import Decimal
from xlrd import open_workbook

from access.models import Flavor
from flavor_usage.models import Application, ApplicationType, Tag

def create_tags_from_applications():
    for app in Application.objects.all():
        if not Tag.objects.filter(name=app.application_type,flavor=app.flavor).exists():
            tag = Tag(name = app.application_type.name,
                      flavor = app.flavor)
            tag.save()


"""Static info from Norma's sheet
"""
APP_NAME = 0
APP_LEVEL = 1
APP_MEMO = 2
APP_OBJ = 3
app_types = [
             ["Misc.",36,37],
             ["Coffee",38,39],
             ["Tea Black",40,None],
             ["Tea White",41,None],
             ["Tea Green",42,None],
             ["Tea Rooibos",43,None],
             ["Flavorcoat",44,None],
             ["Tea Instant",45,None],
             ["Tea Herbal",46,None],
             ["Bakery",47,48],
             ["Beverage",49,50],
             ["Syrups",51,52],
             ["Confectionary",53,54],
             ["Dairy",55,56],
             ["Meat & Savory",57,58],
             ["Prepared Foods",59,60],
             ["Snacks",61,62],
             ["Health & Nutraceuticals",63,64],
             ["Personal Hygiene",65,66],
             ["Pet",67,68],
             ["Tobacco",69,None],
             ["Non-food Fragrance",70,71],
             ]


def import_applications(spreadsheet_path="/var/www/django/dump/sample_data/flavors.xls"):
    re_init()
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    for x in range(2, sheet.nrows):
        parse_row(sheet.row(x))

translate_table = {ord('%'):None}

def usage_range_check(usage_level_value):
    if '-' in usage_level_value:
        usage_level_value = usage_level_value.translate(translate_table)
        usage_level_list = usage_level_value.split('-')
        print(usage_level_list)
        if len(usage_level_list) == 2:
            usage_level_list = sorted(usage_level_list)
            try:
                usage_level = Decimal(usage_level_list[0])
                top_usage_level = Decimal(usage_level_list[1])
                return (usage_level, top_usage_level)
            except:
                pass
    return False

def usage_number_check(usage_level_value):
    try:
        return Decimal(str(usage_level_value))

    except:
        return False

FLAVOR_NUMBER = 7
def parse_row(row):
    flavor_number = row[FLAVOR_NUMBER].value
    print(flavor_number)
    try:
        f = Flavor.objects.get(number=flavor_number)
    except Flavor.DoesNotExist:
        #print "Does not exist: %s" % row[FLAVOR_NUMBER]
        return
    except ValueError:
        #print "Invalid production number: %s" % row[FLAVOR_NUMBER]
        return 
    
    for app in app_types:
        memo = ""
        memo_value = ""
        usage_level = 0
        top_usage_level = None
        
        usage_level_value = row[app[APP_LEVEL]].value
        
        if app[APP_MEMO] is not None:
            memo_value = row[app[APP_MEMO]].value
            
        if (usage_level_value == "" and (memo_value == "" or memo_value == 0)) or usage_level_value == "NO":
            continue
        
        if usage_level_value != '':
            usage_level_number = usage_number_check(usage_level_value)
                
            if usage_level_number is not False:
                usage_level = usage_level_number
                if usage_level == 1:
                    memo = "Usage level was TRUE"
                    usage_level = 0
                elif usage_level < 1:
                        usage_level = usage_level * 100
            else:
                usage_level_range = usage_range_check(usage_level_value)
                if usage_level_range is not False:
                    
                    usage_level = usage_level_range[0]
                    top_usage_level = usage_level_range[1]
                else:
                    memo = "Usage level: %s" % usage_level_value

        if len(memo) > 0:
            if len(memo_value) > 0:
                memo = "%s | %s" % (memo, memo_value)
        else:
            memo = memo_value
            
        print('app: %s -- usage level: "%s" -- memo: "%s"' % (app[APP_NAME], usage_level, memo))
        application = Application(flavor=f,
                application_type=app[APP_OBJ],
                usage_level=usage_level,
                top_usage_level=top_usage_level,
                memo=memo,
                added_from_spreadsheet=True,
                original_spreadsheet_fields="'%s' | '%s'" % (usage_level_value, memo_value),
            )
        application.save()
    
    
def re_init():
    Application.objects.filter(added_from_spreadsheet=True).delete()
    #ApplicationType.objects.all().delete()

    for app in app_types:
        app_type,created = ApplicationType.objects.get_or_create(name=app[APP_NAME])
        if created:
            app_type.save()
        app.append(app_type)
    