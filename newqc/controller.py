class SimpleTestCardException(Exception):
    def __init__(self, value):
        self.value = value
        
    def __str__(self):        
        return ("Multiple testcards detected for retain %s" % unicode(self.value))
     

def testcard_simple_status_to_pass(tc):
    r = tc.retain
    if r.testcard_test.all().count() >  1:
        raise SimpleTestCardException(tv)
    
    tc.status="Passed"
    tc.save()
    r.status="Passed"
    r.save()
    r.lot.status="Passed"
    r.lot.save()
    
def testcard_simple_status_to_under_review(tc):
    r = tc.retain
    if r.testcard_test.all().count() >  1:
        raise SimpleTestCardException(tv)
    
    tc.status="Under Review"
    tc.save()
    r.status="Under Review"
    r.save()
    r.lot.status="Under Review"
    r.lot.save()