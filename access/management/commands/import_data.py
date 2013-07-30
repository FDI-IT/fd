#!/usr/bin/env python

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
#
from access import models
from access.anonymizer import Anonymizer
from access.csv_parse import *

from solutionfixer.models import Solution, SolutionStatus

class Command(BaseCommand):
    args = "<fd.access.models.* ...>"
    help = ("Scans the mbd file indicated in settings for data in the argument models")
    option_list = BaseCommand.option_list + (
        make_option('--testdata', action='store_true', 
                    dest='testdata', default=False,
                    help='Uses shortened test data files.'),
        make_option('--anon', action='store_true', 
                    dest='anon', default=False,
                    help='Anonymizes data after importing.'),
    )
    requires_model_validation = True
    can_import_settings = True
    
    #sort the model list so that FK rows exist
    # TODO UNICODEERROR DERPDERP!
    test_model_dict = {
                   "Formula": models.Formula,
                   ##str(models.Customer):True,
                   "ExperimentalLog": models.ExperimentalLog,
                   "Shipper": models.Shipper,
                   "ShipTo": models.ShipTo,
                   ##str(models.ExperimentalFormula):True,
                   ##str(models.Incoming):True,
                   "Supplier":models.Supplier,
                   ##str(models.ExperimentalProduct):True,
                   "Ingredient": models.Ingredient,
                   "Flavor": models.Flavor,
                   #"ProductSpecialInformation": models.ProductSpecialInformation,
                   "LegacyPurchase":models.LegacyPurchase
                   }
    
    test_models_order = [
                   models.Formula,
                   ##str(models.Customer):True,
                   models.ExperimentalLog,
                   models.Shipper,
                   models.ShipTo,
                   ##str(models.ExperimentalFormula):True,
                   ##str(models.Incoming):True,
                   models.Supplier,
                   ##str(models.ExperimentalProduct):True,
                   models.Ingredient,
                   models.Flavor,
                   #models.ProductSpecialInformation,
                   ##str(models.LegacyPurchase):True
                   ]                  
    
    def handle(self, *args, **options):
        
        model_args = []
        for arg in args[1:]:
            model_args.append(self.test_model_dict[arg])
        model_list = sorted(model_args,
                            key=attrgetter('import_order'))
    
        # set the path: test files or real files
        if options.get('testdata') == True:
            self.base_path = settings.CSVTEST_PATH
            # THIS IS AWFUL! TESTDATA IS probably broken
            raise
        else:
            self.base_path = settings.CSVSOURCE_PATH
            get_csvs_from_mdb(args[0])
        
        
        
        name_indexed_model_dict = {}
        print model_list
        for model in model_list:
            name_indexed_model_dict[model.__name__] = model
        print name_indexed_model_dict 
        for model in model_list:
            print "Deleting %s records..." % model
            model.objects.all().delete()
        
        for model in model_list:
            print "Importing %s records..." % model
            self.import_model_data(model)
            """
            Models need a "access_table_name" field to indicate which table
            is the source of data of the model.
            """
        if options.get('anon') == True:
            self.handle_anon(model_list)
            
        # TODO check integrity here!
        
    def handle_anon(self, model_list):
        anonymizer = Anonymizer()
        if (self.test_model_dict['Flavor'] in model_list):
            anonymizer.anonymize_flavors()
        
        if(self.test_model_dict['Ingredient'] in model_list):
            anonymizer.anonymize_ingredients()
            import Queue
            q = Queue.Queue()
            supplier_codes = ("abt", 'cna','kerry','vigon','FDI')
            for word in supplier_codes:
                q.put(word)               
            for ing in models.Ingredient.objects.all():
                sup = q.get()
                ing.suppliercode = sup
                q.put(sup)
                ing.save()
    
    @transaction.commit_manually
    def import_model_data(self, model):
        print str(model)
        
        # find certain model classes that need real relationships added
        if str(model) == str(models.Formula):
            relation_processor = FormulaBuilder()
        elif str(model) == str(models.ExperimentalLog):
            relation_processor = ExperimentalBuilder()
#        elif str(model) == str(models.ProductSpecialInformation):
#            relation_processor = ProductSpecialInformationBuilder()
        elif str(model) == str(models.Ingredient):
            relation_processor = IngredientBuilder()
        elif str(model) == str(models.LegacyPurchase):
            relation_processor = LegacyPurchaseBuilder()
        else:
            relation_processor = NoRelationBuilder()
        
        # create all the objects I need
        model_munger = RowMunger(model, self.base_path)
        model_exception_writer = \
            ExceptionCSVWriter(model, model_munger.header_row)
        model_field_map = model_munger.field_map
        
        sid_counter = 0
        # iterate over each row in the csv file
        for csv_row in model_munger:
            sid = transaction.savepoint()
            model_instance = model()
            try:
                #for each field in the row, set the model attribute
                for (csv_index, model_field) in model_field_map:
                    csv_field = unicode.strip(csv_row[csv_index])             
                    parsed_csv_field = \
                        parse_csv_field(model_field.db_type(), csv_field)
                    setattr(model_instance,
                        model_field.attname,
                        parsed_csv_field)                            
                      
                relation_processor.build_relation(model_instance)
                model_instance.save()
            except IntegrityError as e:
                transaction.savepoint_rollback(sid)
                print "%s %s -> %s" % (str(model), 
                                   str(model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     model) 
            except DatabaseError as e:
                transaction.savepoint_rollback(sid)
                raise e
            except Exception as e:
                transaction.savepoint_rollback(sid)
                print "%s %s -> %s" % (str(model), 
                                   str(model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     model)
                
            sid_counter+=1
            if sid_counter > 100:
                transaction.commit()
                sid_counter = 0
        transaction.commit()
        model_exception_writer.close()