from newqc.models import *

tc_all = TestCard.objects.all()

def get_tc_retains_and_lots():
    tc_retains = Retain.objects.none()
    tc_lots = Lot.objects.none()
    for tc in tc_all:
        retains = tc.retain_set.all()
        tc_retains = tc_retains | retains
        for r in retains:
            tc_lots = tc_lots | r.lot_set.all()
        tc_retains = tc_retains | tc.retain_set.all()
    return {'tc_retains':tc_retains,
            'tc_lots':tc_lots}
    
# find out what lot statuses look like and retain statuses as well.
    

retains_not_pending = Retain.objects.exclude(status__iexact="pending")
lots_not_pending = Lot.objects.exclude(status__iexact="pending")

for r in Retain.objects.exclude(status="Pending"):
    pass
    
for l in Lot.objects.exclude(status="Pending"):
    pass