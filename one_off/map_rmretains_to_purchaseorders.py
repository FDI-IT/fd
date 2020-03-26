import re

from datetime import date, timedelta

from newqc.models import RMRetain
from access.models import PurchaseOrder

def map_rmretains_to_purchaseorders(path_to_file):
    retain_po_re = re.compile('(\d*)-(\d*)-R?(\d*).pdf')
    
    textfile = open(path_to_file)
    contents = textfile.read()
    
    #parsed_data will be a list of tuples: (PIN, PONUM, RNUM)
    parsed_data = retain_po_re.findall(contents)
    
    error_data = []
    
    for pin, ponum, rnum in parsed_data:
        
        print pin, ponum, rnum
        
        try:
            purchase_order = PurchaseOrder.objects.get(number=ponum)
            
            within_30_days = [purchase_order.date_ordered, purchase_order.date_ordered + timedelta(days=60)]
            
            #using pin just for extra validation, only really need rnum
            rm_retain = RMRetain.objects.filter(pin=pin).filter(date__range=within_30_days).get(r_number=rnum)
            
            rm_retain.po = purchase_order
            rm_retain.save()
        except Exception as e:
            error_data.append((('PIN %' % pin, 'PO Number: %s' % ponum, 'R Number: %s' % rnum), (e.message, type(e))))
    
    return error_data