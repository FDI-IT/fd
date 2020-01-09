import os
import subprocess

from optparse import make_option
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import get_models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError

from access import models
from access import scratch
from access import scratch_dict
from access.csv_parse import get_csvs_from_mdb
from access.utils import IntegrityCheck, ImportData, UpdateData

from solutionfixer.models import Solution, SolutionStatus
from solutionfixer.models import ProcessSolutions


class Command(BaseCommand):
    debug = False
    
    args = "mdb-file"
    help = ("Gets tables from an mdb, imports/updates records, and recalculates cached data.")
    option_list = BaseCommand.option_list + (
        make_option('--anon', action='store_true', 
                    dest='anon', default=False,
                    help='Anonymizes data after importing.'),
    )
    requires_model_validation = True
    can_import_settings = True
    
    import_model_list = sorted([#models.Formula, 
                                #models.ProductSpecialInformation, 
                                models.ExperimentalLog,],
                               key=attrgetter('import_order'))
    update_model_list = []
                        # models.Flavor, models.Ingredient)
    
    
    def handle(self, *args, **options):
        print("HANDLING!")
        get_csvs_from_mdb(args[0])
        id = ImportData()
        id.import_data(self.import_model_list)
        del id
        
        ud = UpdateData()
        ud.update_data(self.update_model_list)
        del ud
        
        if options.get('anon') == True:
            for model in update_model_list:
                model.anonymize()
            
        ps = ProcessSolutions()
        ps.process()
        del ps
        
        ic = IntegrityCheck()
        ic.start_pass()
        del ic
        
        scratch_dict.build_all_trees()
        scratch.build_all_leaf_weights()
        scratch.synchronize_all_prices()
        