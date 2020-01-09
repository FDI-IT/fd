#!/usr/bin/env python

import os
import subprocess

from decimal import InvalidOperation

from optparse import make_option
from django.db.models import Q
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import get_models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError

from access.models import Purchase
from access.exceptions import FormulaException
from access.anonymizer import Anonymizer
from access.csv_parse import (
                                 RowMunger, 
                                 ExceptionCSVWriter, 
                                 parse_csv_field, 
                                 generic_exception_handle,
                                 build_ingredient_relations,
                                 get_csvs_from_mdb
                                 )

#from solutionfixer.models import Solution, SolutionStatus


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
        print(args)
        mdb_file = args[0]
        get_csvs_from_mdb(mdb_file)
        if options.get('testdata') == True:
            self.base_path = settings.CSVTEST_PATH
            # THIS IS AWFUL! TESTDATA IS probably broken
            raise
        else:
            self.base_path = settings.CSVSOURCE_PATH
            
        #self.flag_stat = SolutionStatus.objects.get(status_name="flagged")
        self.debug = False
        self.resemble_count = 0
        self.new_count = 0
        self.different_count = []
        self.exception_count = 0
        self.model_munger = RowMunger(Purchase, self.base_path)
        
        self.model_field_map = self.model_munger.field_map
        
        self.update_ingredient_data()
        
    @transaction.atomic
    def update_ingredient_data(self):
        model_exception_writer = \
            ExceptionCSVWriter(Ingredient, self.model_munger.header_row)
        previous_solution_count = Solution.objects.all().count()
        
        sid_counter = 0
        first_sid = transaction.savepoint()
#
        for csv_row in self.model_munger:
            sid = transaction.savepoint()
            sid_counter+=1
            try:
                self.process_row(csv_row)
            except FormulaException as e:
                print("Formula Exception: %s" % e)
                transaction.savepoint_rollback(sid)
                print("Ingredient: %s -> %s" % (str(self.model_munger.line_num()), 
                                   csv_row))
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
            except InvalidOperation as e:
                print("Invalid Operation: %s" % e)
                transaction.savepoint_rollback(sid)
                print("Ingredient: %s -> %s" % (str(self.model_munger.line_num()), 
                                   csv_row))
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
            except Exception as e:
                self.exception_count+=1
                transaction.savepoint_rollback(sid)
                print("Ingredient: %s -> %s" % (str(self.model_munger.line_num()), 
                                   csv_row))
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
                raise e
            if sid_counter > 200:
                transaction.savepoint_commit(sid)
                sid_counter = 0
                
            if previous_solution_count != Solution.objects.all().count():
                if self.debug:
                    transaction.savepoint_rollback(first_sid)
                    import pdb; pdb.set_trace()
        model_exception_writer.close()
        
        print("Resembles: %s" % self.resemble_count)
        print("Different: %s" % len(self.different_count))
        print("Exceptions: %s" % self.exception_count)
        print("New: %s" % self.new_count)
        
    def process_row(self, csv_row): 
        new_model_instance = Ingredient()
        #for each field in the row, set the model attribute
        for (csv_index, model_field) in self.model_field_map:
            csv_field = str.strip(csv_row[csv_index])        
            parsed_csv_field = parse_csv_field(model_field.db_type(), csv_field)
            setattr(new_model_instance,
                model_field.attname,
                parsed_csv_field)                            
        build_ingredient_relations(new_model_instance)
        try:
            old_model_instance = Ingredient.objects.get(pk=new_model_instance.pk)
        except:
            new_model_instance.save()
            self.new_count += 1
            return
        new_model_instance.clean_fields()
        
        # diff field is the name of a field, or true if there are no differences
        difference_field = new_model_instance.resembles(old_model_instance)
        if (difference_field == True):
            self.resemble_count+=1
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
        else:
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
            solutions_to_flag = Solution.objects.filter(Q(ingredient=old_model_instance) | 
                                                        Q(my_base=old_model_instance) |
                                                        Q(my_solvent=old_model_instance))
            for soluflag in solutions_to_flag:
                soluflag.status=self.flag_stat
                soluflag.save()
            
            
            
            self.different_count.append(difference_field)
            print("Difference in %s - old: %s | new: %s" % (
                                            old_model_instance,
                                            getattr(old_model_instance, difference_field),
                                            getattr(new_model_instance, difference_field)))
