from access.models import Flavor


def consolidate_risk_assessment_groups():
    for fl in Flavor.objects.all():
        if fl.risk_assessment_group == 7:
            fl.risk_assessment_group = 2
        if fl.risk_assessment_group == 8:
            fl.risk_assessment_group = 5
        if fl.risk_assessment_group == 10:
            fl.risk_assessment_group = 0
        if fl.risk_assessment_group == 11:
            fl.risk_assessment_group = 1
        fl.save()
        
        '''
        
RISK_ASSESSMENT_CHOICES = ( #OLD
    (0,"Antimicrobial"),
    (1,"Regularly Monitored"),
    (2,"Non-supportive"),
    (3,"Bacteriostatic"),
    (4,"Hot packed/heat treated"),
    (5,"Low pH, <3.9"),
    (6,"COA Salmonella"),
    (7,"Not typically microsensitive"),
    (8,"Apple Flakes"),
    (9,"Spray Dried"),
    (10,"Benzyl Alcohol"),
    (11,"Testing Required"),
    (12,"Pending"),
)

RISK_ASSESSMENT_CHOICES = (  #NEW
    (0, "Antimicrobial"),
    (1, "Regularly Monitored"),
    (2, "Bacteriostatic"),
    (3, "Hot packed/heat treated"),
    (4, "Low pH, <3.9"),
    (5, "COA Salmonella"),
    (6, "Spray Dried"),
)
    
    '''