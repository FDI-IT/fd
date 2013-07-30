#!/usr/bin/env python
from optparse import make_option

from django.core.management.base import BaseCommand

from solutionfixer.models import Solution, SolutionMatchCache
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
#                    help='Anonymizes data after importing.'),
    )
    requires_model_validation = True
    can_import_settings = True
    

    def handle(self, *args, **options):
        SolutionMatchCache.objects.all().delete()
        sf = SolutionFixer()

        for solution in Solution.objects.all():
            matches = sf.get_related_ingredients(solution.ingredient)
            sorted_matches = []
            for key in sorted(matches.iterkeys(), reverse=True):
                for m in matches[key]:
                    my_append_dict = {}
                    my_append_dict['id'] = my_append_dict['value'] = m.rawmaterialcode
                    my_append_dict['label'] = m.__unicode__()
                    sorted_matches.append(my_append_dict)
                    if (len(sorted_matches) > 9):
                        break
                if (len(sorted_matches) > 9):
                    break
                
            for m in sorted_matches:
                smc = SolutionMatchCache(solution=solution,
                                         label=m['label'],
                                         value=m['value'],
                                         id=m['id'])
                smc.save()
            
       
  