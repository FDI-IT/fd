from access.models import Flavor, FlavorCategoryInfo

def populat():
    for f in Flavor.objects.filter(valid=True):
        try:
            hazards = f.get_hazards()
            # print hazards
        except Exception as e:
            print f, e