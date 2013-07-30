from decimal import Decimal

from xlrd import open_workbook


from access.models import Flavor

"""Static info from Norma's sheet
"""
APP_NAME = 0
APP_LEVEL = 1
APP_MEMO = 2
APP_OBJ = 3
app_types = [
             ["Misc.",30,31],
             ["Coffee",32,33],
             ["Tea Black",34,None],
             ["Tea White",35,None],
             ["Tea Green",36,None],
             ["Tea Rooibos",37,None],
             ["Flavorcoat",38,None],
             ["Tea Instant",39,None],
             ["Tea Herbal",40,None],
             ["Bakery",41,42],
             ["Beverage",43,44],
             ["Confectionary",45,46],
             ["Dairy",47,48],
             ["Meat & Savory",49,50],
             ["Prepared Foods",51,52],
             ["Snacks",53,54],
             ["Health & Nutraceuticals",55,56],
             ["Personal Hygiene",57,58],
             ["Pet",59,60],
             ["Tobacco",61,None],
             ["Non-food Fragrance",62,63],
             ]

def import_applications(spreadsheet_path="/usr/local/django/dump/sample_data/flavors.xls"):
    re_init()
    wb = open_workbook(spreadsheet_path)
    sheet = wb.sheets()[0]
    
    for x in range(1, sheet.nrows):
        parse_row(sheet.row(x))

FLAVOR_NUMBER = 6
def parse_row(row):
    flavor_number = row[FLAVOR_NUMBER].value
    print flavor_number
    try:
        f = Flavor.objects.get(number=flavor_number)
    except Flavor.DoesNotExist:
        print "Does not exist: %s" % row[FLAVOR_NUMBER]
        return
    except ValueError:
        print "Invalid production number: %s" % row[FLAVOR_NUMBER]
        return 
    
    for app in app_types:
        
        try:
            usage_level = row[app[APP_LEVEL]].value
            usage_level = Decimal(str(usage_level))
        except:
            usage_level = 0
        try:
            memo = row[app[APP_MEMO]].value
        except:
            memo = ""
        
        if usage_level != 0 or memo != '':
            print app[APP_NAME]
            print 'usage level: "%s" -- memo: "%s"' % (usage_level, memo)
            application = Application(flavor=f,
                    application_type=app[APP_OBJ],
                    usage_level=usage_level,
                    memo=memo
                )
            application.save()
    
    
def re_init():
    Application.objects.all().delete()
    ApplicationType.objects.all().delete()

    for app in app_types:
        app_type = ApplicationType(name=app[APP_NAME])
        app_type.save()
        app.append(app_type)
    