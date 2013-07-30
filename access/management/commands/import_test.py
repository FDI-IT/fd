#!/usr/bin/env python
from django.core.management.base import NoArgsCommand
import os
from access import models
from django.db.models import get_models
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
import re
import csv
from datetime import datetime
from operator import attrgetter


#MOST RECENT ERRORS

#Caught <class 'psycopg2.IntegrityError'>->('null value in column "ProductID" 
# violates not-null constraint\n',)->null value in column "ProductID" violates 
# not-null constraint
#
#Caught <class 'psycopg2.IntegrityError'>->('null value in column 
# "FlavorAmount" violates not-null constraint\n',)->null value in column 
# "FlavorAmount" violates not-null constraint

@transaction.commit_manually
class Command(NoArgsCommand):
    help = ("Given a decrypted MDB file, migrates the data to the FD project "
            "through intermediary csv files")
    requires_model_validation = True
    can_import_settings = True
    base_path = settings.CSVSOURCE_PATH
    model_list = get_models(models)
    model_list.reverse()
    test_models = {
                   str(models.Formula):True,
                   #str(models.Customer):True,
                   #str(models.ExperimentalLog):True,
                   #str(models.Shipper):True,
                   #str(models.ShipTo):True,
                   #str(models.ExperimentalFormula):True,
                   #str(models.Incoming):True,
                   #str(models.Supplier):True,
                   #str(models.ExperimentalProduct):True,
                   str(models.Ingredient):True,
                   str(models.Flavor):True,
                   #str(models.ProductSpecialInformation):True,
                   #str(models.LegacyPurchase):True
                   }
                   
    
    def munge_row(self, model_obj, model_munger):
        """
        Return a model object based on the contents of row
        """
        pass
    
    def handle_noargs(self, **options):
        
        os.chdir(settings.CSVEXCEPTION_PATH)
        if os.path.exists(settings.CSVEXCEPTION_PATH):
            for exception_csv_file in os.listdir(settings.CSVEXCEPTION_PATH):
                os.remove(exception_csv_file)
        else:
            os.mkdir(settings.CSVEXCEPTION_PATH)
        
        sorted_model_list = sorted(self.model_list,
                                   key=attrgetter('import_order'))
        
        try:
            for model_class in sorted_model_list:
                if str(model_class) in self.test_models:
                    pass
                else:
                    continue
                
                if str(model_class) == str(models.Formula):
                    build_relationship = process_formula_row
                else:
                    build_relationship = process_no_relation

                model_munger = RowMunger(model_class)
                model_exception_writer = \
                    ExceptionCSVWriter(model_class, model_munger.header_row)
                model_field_map = model_munger.field_map()
                
                for csv_row in model_munger:
                    print "%s %s -> %s" % (str(model_class), 
                                           str(model_munger.line_num()), 
                                           csv_row)
                    model_instance = model_class()
                    for mapped_field in model_field_map:
                        
                        model_field = model_class._meta.fields[mapped_field[1]]
                        csv_field = csv_row[mapped_field[0]]
                        
                        parsed_csv_field = \
                            parse_csv_field(model_field.db_type(), csv_field)
                        
                        setattr(model_instance,
                                model_field.attname,
                                parsed_csv_field)                            
                    try:                        
                        build_relationship(model_instance)
                    except:
                        continue
                    
                    try:
                        model_instance.save()
                    except Exception as inst:
                        """
                        Catches an exception saving the model, records it in 
                        the exception file and prints it to stdout
                        """
                        generic_exception_handle(inst, 
                                                 csv_row, 
                                                 model_exception_writer, 
                                                 model_class)
                
                model_exception_writer.close()
        except:
            transaction.rollback()
            raise
        transaction.commit()
        
def parse_csv_field(db_type, csv_field):
    db_type = model_field.db_type()
    
    if db_type == 'integer' or db_type == 'smallint':
        if re.search('[0-9]', csv_field):
            csv_field = int(csv_field)
        else:
            csv_field = 0
        
    elif db_type == 'double precision':
        if re.search('[0-9]', csv_field):
            csv_field = float(csv_field)
        else:
            csv_field = 0
        
    elif re.match('numeric', db_type):
        if re.search('[0-9]', csv_field):
            csv_field = str(csv_field)
        else:
            csv_field = 0
            
    elif re.match('timestamp', db_type):
        if len(csv_field) > 11:
            mydate =  datetime.strptime(csv_field, "%m/%d/%y %H:%M:%S")
            csv_field = mydate
        else:
            mydate = datetime(1990, 1, 1)
            csv_field = mydate
    
    elif re.match('bool', db_type):
        if re.search('1', csv_field):
            csv_field = 1
        else:
            csv_field = 0
            
    return csv_field

def generic_exception_handle(self, 
                             e, 
                             csv_row, 
                             model_exception_writer, 
                             model_class):
    emsg = str(model_class)
    emsg += ' -> ' + str(type(e))
    emsg += ' -> ' + str (e.args)
    
    csv_row.append(emsg)
    
    model_exception_writer.writerow(csv_row)
    
    print "Caught %s" % (emsg, )
    transaction.rollback()
    
def process_formula_row(model_instance):
    acc_flavor = model_instance.acc_flavor
    acc_ingredient = model_instance.acc_ingredient
    print "acc_flavor: %s, acc_ingredient: %s" % (acc_flavor, acc_ingredient)
    model_instance.flavor = models.Flavor.objects.get(number=acc_flavor)
    
    possible_ingredients = models.Ingredient.objects.filter(
                                            id=acc_ingredient
                                        ).exclude(
                                            discontinued=True)
    
    if possible_ingredients.count() > 1:
        print possible_ingredients
        raise 
    
def process_no_relation(model_instance):
    pass
        
class ExceptionCSVWriter():
    
    def __init__(self, model_class, header_row):
        self.file_path = settings.CSVEXCEPTION_PATH + \
                            '/' + model_class._meta.db_table + '.csv'
        self.csv_file = open(self.file_path, 'a')
        self.csv_writer = csv.writer(self.csv_file)
        self.header = list(header_row)
        self.header.append('Exception')
        self.csv_writer.writerow(self.header)
        
    def writerow(self, row):
        return self.csv_writer.writerow(row)
     
    def close(self):
        return self.csv_file.close()
         


class RowMunger():
    """
    This class provides a method for returning a dictionary that pairs csv row
    data with the appropriate column headers.
    """
    
    def __init__(self, model_class):
        """
        Initializes a csv reader and the header_row
        """
        self.model_class = model_class
        self.csv_file = open(settings.CSVSOURCE_PATH + 
                             '/' + 
                             model_class._meta.db_table + 
                             '.csv')
        self.csv_reader = csv.reader(self.csv_file,
                                     delimiter=',',
                                     quotechar='\"')
        self.header_row = self.csv_reader.next()
        
    def __iter__(self):
        return self
        
    def next(self):
        data_row = self.csv_reader.next()
        
        if len(data_row) == len(self.header_row):
            return data_row
        else:
            raise RowLenException(self.header_row, data_row)
        
    def line_num(self):
        return self.csv_reader.line_num
    
    def close(self):
        close(self.csv_file)
    
    def field_map(self):
        """
        Checks to see that every field in the self.header_row maps to one of
        the fields of in target_model
        
        Returns a list of tuples mapping csv to model fields
        """
        csv_field_list = self.header_row
        csv_field_list_check = list(csv_field_list)
        target_field_list = self.model_class._meta.fields
        
        map_list = []
                       
        for i, csv_field in enumerate(csv_field_list):
            myre = re.compile(csv_field, re.I)
            for j, target_field in enumerate(target_field_list):
                target_field_name = target_field.db_column
                if target_field_name:
                    matchobj = myre.match(target_field_name)
                    if matchobj:
                        csv_field_list_check.remove(csv_field)
                        map_list.append((i,j))
                        break
            
        if len(csv_field_list_check) == 0:
            return map_list
        else:
            raise Exception(self.model_class)
    
class RowLenException(Exception):
    """
    Raised when a source row and header row don't have equal length
    """
    def __init__(self, header_row, data_row):
        print "Header row:"
        print header_row
        print "Data row:"
        print data_row
        print type(self)
        print self.args
        print self
    