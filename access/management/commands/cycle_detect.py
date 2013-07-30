#!/usr/bin/env python
from operator import attrgetter
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings

from access.cycledetection import FormulaTree, FormulaTreeAlt, CycleDetection
from access.models import Flavor

from access.management.commands.draw_graph import draw_graph

class Command(BaseCommand):
    help = "A command to experiment with cycle detection."
    args = "<flavornumber>"
#    option_list = BaseCommand.option_list + (
#        make_option('--depth',
#                    action='store', 
#                    dest='depth', default=1,
#                    help='The depth at which to construct the tree.'),
#    )
    requires_model_validation = True
    can_import_settings = True                

    def handle(self, *args, **options):
#        if options.get('testdata') == True:
#            base_path = settings.CSVTEST_PATH
#        else:
#            base_path = settings.CSVSOURCE_PATH
        
        # clean up the directory where all our exception info is logged
        cd = CycleDetection()
        cd.check_all_flavors()
        for flavor in cd.cycled_flavors.keys():
            draw_graph(flavor)