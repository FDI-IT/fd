#!/usr/bin/env python
from operator import attrgetter
from optparse import make_option

from django.core.management.base import NoArgsCommand
from django.conf import settings

from access.models import Flavor

class Command(NoArgsCommand):
    help = "A command to update the costs of all flavors."
#    option_list = BaseCommand.option_list + (
#        make_option('--depth',
#                    action='store', 
#                    dest='depth', default=1,
#                    help='The depth at which to construct the tree.'),
#    )
    requires_model_validation = True
    can_import_settings = True                

    def handle_noargs(self, *args, **options):
#        if options.get('testdata') == True:
#            base_path = settings.CSVTEST_PATH
#        else:
#            base_path = settings.CSVSOURCE_PATH
        
        # clean up the directory where all our exception info is logged
        cu = CostUpdater()
        cu.update_all_flavor_costs()