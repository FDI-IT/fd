from access.models import Flavor, ExperimentalLog, LocationCode
from unified_adapter.models import ProductInfo

def populate():
    for pi in ProductInfo.objects.exclude(location_code=""):
        print pi
        try:
            f = Flavor.objects.get(number=pi.production_number)
            f.location_code = pi.location_code
            f.save()
            print "Found flavor %s" % (f)
        except:
            pass
        
        try:
            e = ExperimentalLog.objects.get(experimentalnum=pi.experimental_number)
            e.location_code = pi.location_code
            e.save()
            print "Found experimental %s" % (e)
        except:
            pass

def populate_location_codes_specific(ModelClass):
    for x in ModelClass.objects.exclude(location_code=None):
        lc = LocationCode(location_code=x.location_code,content_object=x)
        lc.save()
        
def populate_location_codes_generic():
    LocationCode.objects.all().delete()
    for MC in (Flavor, ExperimentalLog):
        populate_location_codes_specific(MC)
        
