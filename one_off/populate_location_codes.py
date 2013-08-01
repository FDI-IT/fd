from access.models import Flavor, ExperimentalLog
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