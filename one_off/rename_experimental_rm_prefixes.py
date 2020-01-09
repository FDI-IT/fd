from access.models import Flavor, Ingredient, ExperimentalLog


def rename_experimental_rm_prefixes():
    
    for experimental_rm in Ingredient.objects.filter(prefix__contains='EX'):
            
        #NOT APPROVED, EX PREFIX and 50000-59999
        #IF ALL TRUE, Use experimental prefix
        #IF ONE OR TWO TRUE, raise error, something is wrong
        #IF NONE TRUE, use flavor prefix
        
        flavor = experimental_rm.sub_flavor
        if flavor == None:
            print('Ingredient %s has no sub_flavor.  This ingredient will not be changed.' % experimental_rm.__str__())
        else:
            if (not flavor.approved) and (50000 < flavor.number < 59999) and (flavor.experimental_log.count() > 0):
                exlog = flavor.experimental_log.all()[0]
                if exlog == None:
                    print('sub_flavor %s of ingredient %s has no experimental log...' % (flavor, experimental_rm))
                else:
                    experimental_rm.prefix = '%s-%s' % (exlog.experimentalnum, exlog.initials)
            else:
                if (flavor.approved and flavor.number < 50000):
                    experimental_rm.prefix = '%s-%s' % (flavor.prefix, flavor.number)
                
                if (flavor.approved and 50000 < flavor.number < 59999):
                    print('sub_flavor %s of ingredient %s is approved, but still has an experimental number.' % (flavor, experimental_rm))

                if (not flavor.approved) and (not 50000 < flavor.number < 59999):
                    print('sub_flavor %s of ingredient %s is not approved, but does not have a number in the experimental range.' % (flavor, experimental_rm))

            experimental_rm.save()
        
    print('Done.')
        