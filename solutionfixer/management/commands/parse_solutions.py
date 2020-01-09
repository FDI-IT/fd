#!/usr/bin/env python

from decimal import Decimal
from optparse import make_option

from django.core.management.base import BaseCommand


from solutionfixer.models import Solution, SolutionStatus
from solutionfixer.parse_solutions import SolutionFixer

class Command(BaseCommand):
    args = ""
    help = ("")
    option_list = BaseCommand.option_list + (
        make_option('--testdata', action='store_true', 
                    dest='testdata', default=False,
                    help='Uses shortened test data files.'),
#        make_option('--anon', action='store_true', 
#                    dest='anon', default=False,
#                    help='Anonymizes data after impotrting.'),
    )
    requires_model_validation = True
    can_import_settings = True
    

    def handle(self, *args, **options):
        
        Solution.objects.all().delete()
        sf = SolutionFixer()
        initial_status = SolutionStatus.objects.get(status_order=1)
        for solution in SolutionFixer.solutions:
            newsol = Solution()
            newsol.ingredient = solution
            newsol.status = initial_status
            try:
                newsol.my_solvent = sf.get_solvent(solution)
            except:
                pass
            try:
                newsol.percentage = Decimal(sf.get_percentage(solution))
            except:
                pass
            try:
                newsol.save()
            except:
                newsol.mysolvent = None
                newsol.percentage = None
                newsol.save()
        
            
       
  