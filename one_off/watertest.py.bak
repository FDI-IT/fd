from haccp.models import WaterTest

from datetime import date
import random
from decimal import Decimal

start_date = date(2009,1,7)
delta = date(2009,1,14) - start_date
vacation_dates = (date(2009,12,30),date(2010,12,29),date(2011,12,28),date(2012,12,26))

def populate_results():
    WaterTest.objects.all().delete()
    
    test_date = start_date
    
    zone = 1
    
    while(test_date < date.today()):
        
        for x in range(1,5):
            
            test_result = Decimal(random.randrange(1,7,1))/10
            
            wt = WaterTest(test_date=test_date,
                      zone=zone,
                      test_result=test_result)
            
            wt.save()
            zone += 1
            if zone > 18:
                zone = 1
                
        test_date += delta
        if test_date in vacation_dates:
            print test_date
            test_date += delta
        