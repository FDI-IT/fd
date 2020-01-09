from access.models import Flavor

def fix_indivisible():
    for f in Flavor.objects.all():
        print(f)
        if f.yield_field != 100 or f.spraydried == True:
            f.indivisible = True
            f.save()
        else:
            f.indivisible = False
            f.save()