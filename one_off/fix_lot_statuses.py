from newqc.models import Lot

def fix_lots():
    for lot in Lot.objects.filter(status="resample"):
        lot.status="Resample"
        lot.save()
        
    for lot in Lot.objects.filter(status="adjust"):
        lot.status="Rework"
        lot.save()
        
    for lot in Lot.objects.filter(status="Fix"):
        lot.status="Rework"
        lot.save()
        
    for lot in Lot.objects.filter(status="Reblend"):
        lot.status="Rework"
        lot.save()
        
    for lot in Lot.objects.filter(status="Reject "):
        lot.status="Reject"
        lot.save()
    
    for lot in Lot.objects.filter(status="Passed "):
        lot.status="Passed"
        lot.save()
        
    for lot in Lot.objects.filter(status="Destroyed"):
        lot.status="Expired"
        lot.save()
        
    for lot in Lot.objects.filter(status="Reject"):
        lot.status="Rejected"
        lot.save()
        
    for lot in Lot.objects.filter(status="Under review"):
        lot.status="Hold"
        lot.save()
        
    for lot in Lot.objects.filter(status="Pending"):
        lot.status="Created"
        lot.save()