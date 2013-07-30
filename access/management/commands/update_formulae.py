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

from access.models import Formula
from access.anonymizer import Anonymizer
from access.csv_parse import (
                                 RowMunger, 
                                 ExceptionCSVWriter, 
                                 parse_csv_field, 
                                 generic_exception_handle,
                                 get_csvs_from_mdb,
                                 FormulaBuilder
                                 )

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
    relation_processor = FormulaBuilder()
    
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
        self.model_munger = RowMunger(Formula, self.base_path)
        self.model_field_map = self.model_munger.field_map
            
        self.update_formula_data()

    def update_formula_data(self):
        model_exception_writer = \
            ExceptionCSVWriter(Formula, self.model_munger.header_row)
        
        # iterate over each row in the csv file
        for csv_row in self.model_munger:
            try:
                self.process_row(csv_row)
            except DatabaseError as e:
                raise e
            except ValidationError as e:
                self.exception_count += 1
                print "%s %s -> %s" % (str(Flavor), 
                                   str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row,
                                     model_exception_writer, 
                                     Flavor)
#            except UnicodeDecodeError as e:
#                raise e
            except Exception as e:
                self.exception_count += 1
                print "%s %s -> %s" % (str(Formula), 
                                   str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row,
                                     model_exception_writer, 
                                     Formula)
                
        model_exception_writer.close()
        
        print "Resembles: %s" % self.resemble_count
        print "Different: %s" % len(self.different_count)
        print "Exceptions: %s" % self.exception_count
        print "New: %s" % self.new_count
        
        
    def process_row(self, csv_row):
        
        new_model_instance = Formula()
        #for each field in the row, set the model attribute
        for (csv_index, model_field) in self.model_field_map:
            csv_field = unicode.strip(csv_row[csv_index])         
            parsed_csv_field = \
                parse_csv_field(model_field.db_type(), csv_field)
            setattr(new_model_instance,
                model_field.attname,
                parsed_csv_field)
        self.relation_processor.build_relation(new_model_instance)
                             
        new_model_instance.save()
        print new_model_instance.flavor 
        