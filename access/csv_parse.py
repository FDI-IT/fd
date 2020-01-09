import os
import csv
from datetime import datetime
import re

from django.conf import settings

from access import models

from pluggable.csv_unicode_wrappers import UnicodeWriter



def get_csvs_from_mdb(mdb_file='/srv/samba/access/Flavor Dynamics Access.mdb',):
    base_path = settings.CSVSOURCE_PATH
    os.chdir(settings.CSVEXCEPTION_PATH)
    if os.path.exists(settings.CSVEXCEPTION_PATH):
        for exception_csv_file in os.listdir(settings.CSVEXCEPTION_PATH):
            os.remove(exception_csv_file)
    else:
        os.mkdir(settings.CSVEXCEPTION_PATH)
    try:
        # remove old csv files
        os.system('rm "{0}"/*.csv'.format(base_path))
        # call mdb-tables on all the tables in the list
        os.system('mdb-tables -1 "{0}" | while read -r table; do mdb-export "{0}" "$table" >> "{1}/$table.csv"; done'.format(mdb_file, base_path))
        # move all files that match the pattern
        os.system('ls "{0}"| grep acc | while read -r f; do mv "{0}/${{f}}" "{0}/${{f#acc*_}}"; done'.format(base_path))
    except:
        print("Failed to process %s" % mdb_file)
        raise


def parse_csv_field(db_type, csv_field):
    """
    Given the db_type of the model field we're filling, and the csv_field as a
    string, casts the csv_field to the appropriate type to fit in the model 
    field.
    
    Returns the cast csv_field.
    
    """
    if re.search('int', db_type):
        try:
            csv_field = int(csv_field)
        except ValueError:
            csv_field = 0
        
    elif db_type == 'double precision':
        try:
            csv_field = float(csv_field)
        except ValueError:
            csv_field = 0
        
    elif re.search('numeric', db_type):
        if(csv_field == ''):
            csv_field = "0"
        else:
            try:
                csv_field = str(csv_field)
            except ValueError:
                csv_field = "0"
            
    elif re.search('timestamp', db_type):
        if len(csv_field) > 11:
            mydate =  datetime.strptime(csv_field, "%m/%d/%y %H:%M:%S")
            csv_field = mydate
        else:
            mydate = datetime(1990, 1, 1)
            csv_field = mydate
    
    elif re.search('date', db_type):
        if len(csv_field) > 11:
            mydate =  datetime.strptime(csv_field, "%m/%d/%y %H:%M:%S").date()
            csv_field = mydate
        else:
            mydate = datetime(1990, 1, 1).date()
            csv_field = mydate
    
    
    elif re.search('bool', db_type):
        if re.search('1', csv_field):
            csv_field = 1
        else:
            csv_field = 0
            
    return csv_field

class FormulaBuilder:
    def __init__(self):
        self.flavors = {}
        flavors_queryset = models.Flavor.objects.all()
        for f in flavors_queryset:
            # i know there are no collisions because the unique contraint
            # on Flavor.number
            self.flavors[f.number] = f
            
        self.ingredients = {}
        ingredients_queryset = models.Ingredient.objects.all()
        for i in ingredients_queryset:
            try:
                self.ingredients[i.id].append(i)
            except:
                self.ingredients[i.id] = [i,]
    def build_relation(self, formula):
        """
        Given a row from the formula table, looks up the appropriate real PKs of
        flavors and ingredients and sets the FKs of Formula.
        """
        acc_flavor = formula.acc_flavor
        acc_ingredient = formula.acc_ingredient
        #print "acc_flavor: %s, acc_ingredient: %s" % (acc_flavor, acc_ingredient)
        try:
            formula.flavor = self.flavors[acc_flavor]
        except:
            raise models.FormulaException("Flavor not found: %s" % acc_flavor)
        try:
            possible_ingredients = self.ingredients[acc_ingredient]
        except:
            raise models.FormulaException("Ingredient not found: %s" % acc_ingredient)
        len_possible_ingredients = len(possible_ingredients)
        if len_possible_ingredients == 0:
            raise models.FormulaException("No ingredients found for %s" % acc_flavor)
        else:
            for ing in possible_ingredients:
                if ing.discontinued == False:
                    formula.ingredient = ing
                    return
            formula.ingredient = possible_ingredients[0]

class IngredientBuilder:
    
    def build_relation(self, ingredient):
        flavornum = ingredient.flavornum
        if (flavornum == 0 or
            flavornum == None):
            ingredient.sub_flavor = None
        else:
            try:
                ingredient.sub_flavor = models.Flavor.objects.get(
                                                    number=flavornum)
            except:
                ingredient.sub_flavor = None
                raise models.FormulaException("Ingredient %s represents non-existent sub-flavor: %s" %
                                       (ingredient.id,
                                       ingredient.flavornum))        

class ExperimentalBuilder:
    def build_relation(self,experimental):
        pass
#        """
#        Given a row from the formula table, looks up the appropriate real PKs of
#        flavors and ingredients and sets the FKs of Formula.
#        
#        """
#        if experimental.product_number != 0:
#            try:
#                experimental.flavor = models.Flavor.objects.get(number=experimental.product_number)
#            except Exception as inst:
#                experimental.flavor = None
#        else:
#            experimental.flavor = None
#         
class ProductSpecialInformationBuilder:   
    def build_relation(self,psi):
        """
        Given a row from the formula table, looks up the appropriate real PKs of
        flavors and ingredients and sets the FKs of Formula.
        """
        try:
            f = models.Flavor.objects.get(number=psi.flavornumber)
            if psi.productid != f.id:
                print(psi.flavornumber)
                psi.flavor=None
            else:
                psi.flavor=f
            
        except models.Flavor.DoesNotExist:
            psi.flavor=None
            
class LegacyPurchaseBuilder:
    def build_relation(self,lp):
        print(lp.poduedate)
    
class NoRelationBuilder:
    def build_relation(self,model_instance):
        """
        A placeholder function is necessary when no extra relationships need to be
        processed for a particular type of model.
        
        """
        pass
    
class LegacyPurchaseMigrate:
    def __init__(self):
        models.PurchaseOrder.objects.all().delete()
        models.PurchaseOrderLineItem.objects.all().delete()
        
        self.lp_dict = {}
        
        for lp in models.LegacyPurchase.objects.all():
            if lp.ponumber in self.lp_dict:
                self.lp_dict[lp.ponumber].append(lp)
            else:
                self.lp_dict[lp.ponumber] = [lp,]
        
        for ponumber, poentries in self.lp_dict.items():
            try:
                poentry=poentries[0]
                shipper = models.Shipper.objects.get(shipperid=poentry.shipperid)
                ship_to = models.ShipTo.objects.get(shiptoid=poentry.shiptoid)
                supplier = models.Supplier.objects.get(suppliercode=poentry.suppliercode)
                if poentry.poduedate is None:
                    po,created = models.PurchaseOrder.objects.get_or_create(
                        number=ponumber,
                        shipper=shipper,
                        ship_to=ship_to,
                        supplier=supplier,
                        memo=poentry.pomemo,
                        memo2=poentry.pomemo2,
                    )
                else:
                    po,created = models.PurchaseOrder.objects.get_or_create(
                        number=ponumber,
                        shipper=shipper,
                        ship_to=ship_to,
                        supplier=supplier,
                        memo=poentry.pomemo,
                        memo2=poentry.pomemo2,
                        due_date=poentry.poduedate,
                    )
                po.date_ordered = poentry.dateordered
                po.save()
                for poentry in poentries:
                    try:
                        raw_material = models.Ingredient.objects.get(rawmaterialcode=poentry.rawmaterialcode)
                        if poentry.poduedate is None:
                            poli = models.PurchaseOrderLineItem.objects.create(
                                po=po,
                                raw_material=raw_material,
                                date_received=poentry.datereceived,
                                memo=poentry.pomemo,
                                memo2=poentry.pomemo2,
                                quantity=poentry.poquantity,
                                package_size=poentry.packagesize,
                                legacy_purchase=poentry,
                            )
                        else:
                            poli = models.PurchaseOrderLineItem.objects.create(
                                po=po,
                                raw_material=raw_material,
                                date_received=poentry.datereceived,
                                memo=poentry.pomemo,
                                memo2=poentry.pomemo2,
                                quantity=poentry.poquantity,
                                due_date=poentry.poduedate,
                                package_size=poentry.packagesize,
                                legacy_purchase=poentry,
                            )
                    except models.Ingredient.DoesNotExist as e:
                        print(e)
                        print(poentry.rawmaterialcode)
            except models.Shipper.DoesNotExist as e:
                print(e)
                print(poentry.shipperid)
            except models.ShipTo.DoesNotExist as e:
                print(e)
                print(poentry.shiptoid)
            except models.Supplier.DoesNotExist as e:
                print(e)
                print(poentry.suppliercode)
                    
            
def generic_exception_handle(e, 
                             csv_row, 
                             model_exception_writer, 
                             model_class):
    """
    Records the exception in a file for later review, in addition to printing
    to stdout.

    """
    emsg = str(model_class)
    emsg += ' -> ' + str(type(e))
    try:
        exception_message = str(e.value)
    except:
        exception_message = str(e.args)
        
    if exception_message == '()':
        exception_message = repr(e)
    
    emsg += ' -> ' + exception_message
    
    csv_row.append(emsg)
    
    model_exception_writer.writerow(csv_row)
    
    print("Caught %s" % (emsg, ))

    
class ExceptionCSVWriter():
    
    def __init__(self, model_class, header_row):
        self.file_path = settings.CSVEXCEPTION_PATH + \
                            '/' + model_class._meta.db_table + '.csv'
        self.csv_file = open(self.file_path, 'a')
        self.csv_writer = UnicodeWriter(self.csv_file)
        self.header = list(header_row)
        self.header.append('Exception')
        self.csv_writer.writerow(self.header)
        
    def writerow(self, row):
        return self.csv_writer.writerow(row)
     
    def close(self):
        return self.csv_file.close()

class RowMunger():
    """
    Provides a method for returning a dictionary that pairs csv row data with
    the appropriate column headers.
    
    """
    
    def __init__(self, model_class, base_path):
        """
        Initializes a csv reader and the header_row
        
        """
        self.model_class = model_class
        self.csv_file = open(base_path + 
                             '/' + 
                             model_class._meta.db_table + 
                             '.csv')
        self.csv_reader = csv.reader(self.csv_file,
                                     delimiter=',',
                                     quotechar='\"')
        self.header_row = next(self.csv_reader)
        self.field_map = self.field_map()
        
    def __iter__(self):
        return self
        
    def __next__(self):
        data_row = [str(s, 'utf-8') for s in next(self.csv_reader)]
        
        if len(data_row) == len(self.header_row):
            return data_row
        else:
            raise RowLenException(self.header_row, data_row)
        
    def line_num(self):
        return self.csv_reader.line_num
    
    def close(self):
        self.csv_file.close()
    
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
                        model_field = self.model_class._meta.fields[j]
                        map_list.append((i,model_field))
                        break
        
        if len(csv_field_list_check) == 0:
            return map_list
        else:
            print(csv_field_list_check)
            raise Exception(self.model_class)
        
        #model_field = model_class._meta.fields[mapped_field[1]]
    
class RowLenException(Exception):
    """
    Raised when a source row and header row don't have equal length
    
    """
    def __init__(self, header_row, data_row):
        print("Header row:")
        print(header_row)
        print("Data row:")
        print(data_row)
        print(type(self))
        print(self.args)
        print(self)
    