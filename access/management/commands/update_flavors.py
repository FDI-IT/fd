#!/usr/bin/env python

import os
import subprocess

from optparse import make_option
from django.db.models import Q
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import get_models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError

from access.models import Flavor
from access.anonymizer import Anonymizer
from access.csv_parse import (
                                 RowMunger, 
                                 ExceptionCSVWriter, 
                                 parse_csv_field, 
                                 generic_exception_handle,
                                 get_csvs_from_mdb
                                 )

from solutionfixer.models import Solution, SolutionStatus

class Command(BaseCommand):
    args = "<access.models.* ...>"
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
    
    
    def handle(self, *args, **options):
        mdb_file = args[0]
        get_csvs_from_mdb(mdb_file)
        if options.get('testdata') == True:
            self.base_path = settings.CSVTEST_PATH
            # THIS IS AWFUL! TESTDATA IS probably broken
            raise
        else:
            self.base_path = settings.CSVSOURCE_PATH
            
        self.debug = False
        self.resemble_count = 0
        self.different_count = []
        self.new_count = 0
        self.exception_count = 0
        self.model_munger = RowMunger(Flavor, self.base_path)
        self.model_field_map = self.model_munger.field_map
            
        self.update_flavor_data()
        
    @transaction.atomic
    def update_flavor_data(self):
        model_exception_writer = \
            ExceptionCSVWriter(Flavor, self.model_munger.header_row)
        
        sid_counter = 0
        # iterate over each row in the csv file
        for csv_row in self.model_munger:
            sid = transaction.savepoint()
            sid_counter+=1
            try:
                self.process_row(csv_row)
            except DatabaseError as e:
                transaction.savepoint_rollback(sid)
                raise e
            except ValidationError as e:
                self.exception_count += 1
                transaction.savepoint_rollback(sid)
                print("%s %s -> %s" % (str(Flavor), 
                                   str(self.model_munger.line_num()), 
                                   csv_row))
                generic_exception_handle(e, 
                                     csv_row,
                                     model_exception_writer, 
                                     Flavor)
#            except UnicodeDecodeError as e:
#                raise e
#            except Exception as e:
#                self.exception_count += 1
#                transaction.savepoint_rollback(sid)
#                print "%s %s -> %s" % (str(Flavor), 
#                                   str(self.model_munger.line_num()), 
#                                   csv_row)
#                generic_exception_handle(e, 
#                                     csv_row,
#                                     model_exception_writer, 
#                                     Flavor)
                
            if sid_counter > 200:
                transaction.savepoint_commit(sid)
                sid_counter = 0
        
        model_exception_writer.close()
        
        print("Resembles: %s" % self.resemble_count)
        print("Different: %s" % len(self.different_count))
        print("Exceptions: %s" % self.exception_count)
        print("New: %s" % self.new_count)
        
        
    def process_row(self, csv_row):
        new_model_instance = Flavor()
        #for each field in the row, set the model attribute
        for (csv_index, model_field) in self.model_field_map:
            csv_field = str.strip(csv_row[csv_index])         
            parsed_csv_field = \
                parse_csv_field(model_field.db_type(), csv_field)
            setattr(new_model_instance,
                model_field.attname,
                parsed_csv_field)                            
            
        try:
            old_model_instance = Flavor.objects.get(number=new_model_instance.number)
        except:
            self.new_count += 1
            new_model_instance.save()
            return
        
        new_model_instance.clean_fields()
        
        difference_field = new_model_instance.resembles(old_model_instance)
        if (difference_field == True):
            self.resemble_count+=1
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
        else:    
            self.different_count.append(difference_field)
            print("Difference in %s - old: %s | new: %s" % (
                                            old_model_instance,
                                            getattr(old_model_instance, difference_field),
                                            getattr(new_model_instance, difference_field)))
            if self.debug:
                import pdb; pdb.set_trace()
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
        #new_model_instance.save()