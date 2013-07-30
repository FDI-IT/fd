import os
import sys
import re
import glob
import datetime
import logging

from pluggable.csv_unicode_wrappers import UnicodeReader

from xlrd import open_workbook
from xlrd import xldate_as_tuple

from access.models import Ingredient, DigitizedFormula, ExperimentalLog

experimental_re = re.compile('\d+')

def test(path="/usr/local/django/dump/sample_data/digitized_formulas"):
    os.chdir(path)
    LOG_FILENAME = 'digitized_import.log'
    logging.basicConfig(filename=LOG_FILENAME, level=logging.WARNING)
    digitized_formula_list = glob.glob("*.[Xx][Ll][Ss]")
    dwb_list = []
    DigitizedFormula.objects.all().delete()
    for digitized_formula in digitized_formula_list:
        try:
            dwb = DigitizedWB(path=digitized_formula)
            dwb.check_sheet()
            dwb_list.append(dwb)
        except DigitizedException as err:
            print "Error in %s: %s" % (digitized_formula, err)
#        except:
#            print "Unexpected error in %s: %s" % (digitized_formula, sys.exc_info()[0])
    return dwb_list

class DigitizedException(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class DigitizedWB:
    
    rm_id_headers = ["Raw Materials by Active.ProductID",
                     "PIN #",
                     "pin #",
                     "pin#",
                     "PIN#",
                     "RM Code",]
    amount_headers = ["FlavorAmount",
                      "Amount",""
                      "Amt",]
    experimental_headers = ["Text77",]
    
    def __init__(self, path="/usr/local/django/dump/digitizedsample.xls"):
        self.rm_id_column = None
        self.amount_column = None
        self.experimental_column = None
        self.experimentalnum = None
        self.experimental_log = None
        self.ingredients = [] # keys to the ingredients table
        self.amounts = [] # the amount of the ingredients
        self.lastrow = 0 # the index of the last valid row
        self.path = path
        self.sheet = open_workbook(path).sheets()[0]
        
    def check_sheet(self):
        try:
            self.experimental_num = experimental_re.match(self.path).group(0)
            self.experimental_log = ExperimentalLog.objects.get(experimentalnum=self.experimental_num)
            print self.experimental_num
        except:
            return
        for row in range(self.sheet.nrows):
            raw_row = []
            for col in range(self.sheet.ncols):
                v = self.sheet.cell(row,col).value
                raw_row.append(v)
                self.check_cell(row,col,v)
            row_string = u'|||'.join(unicode(item) for item in raw_row)
            df = DigitizedFormula(experimental_log=self.experimental_log, raw_row=row_string)
            df.save()
                    
        if not self.rm_id_column:
            raise DigitizedException("RM ID column not found.")
        if not self.amount_column:
            raise DigitizedException("Amount column not found.")
        
#        self.sum_amounts()
#        self.test_ingredients()
    
    def check_cell(self, row, col, cell_value):
        """
        The +1 in the inner assignment statements is to offset the 
        row, so the column tuples point to the first value, and not
        the header.
        """
        if cell_value in DigitizedWB.rm_id_headers:
            if not self.rm_id_column:
                self.rm_id_column = (row+1, col)
                return
            else:
                raise DigitizedException("RM ID column exists at %s, %s" % self.rm_id_column)
        elif cell_value in DigitizedWB.amount_headers:
            if not self.amount_column:
                self.amount_column = (row+1, col)
                return
            else:
                raise DigitizedException("Amount column exists at %s, %s" % self.amount_column)
        elif cell_value in DigitizedWB.experimental_headers:
            if not self.experimental_column:
                self.experimental_column = (row+1, col)
                return
            else:
                raise DigitizedException("Experimental column exists at %s, %s" % self.experimental_column)
    
    def sum_amounts(self):
        """
        Sets self.lastrow based on the row that the loop breaked on.
        """
        col = self.amount_column[1]
        self.total_weight = 0
        for row in range(self.amount_column[0], self.sheet.nrows):
            value = self.sheet.cell(row, col).value
            if type(value) is float and value != 1000:
                self.amounts.append(value)
                self.total_weight += value
            else:
                self.lastrow = row-1
                break
        if self.total_weight != 1000:
            raise DigitizedException("Weight totals to %s" % self.total_weight)
            
    def test_ingredients(self):
        col = self.rm_id_column[1]
        for row in range(self.rm_id_column[0], self.lastrow):
            value = self.sheet.cell(row,col).value
            if value != '':
                try:
                    ing = Ingredient.objects.get(id=value)
                    self.ingredients.append(ing)
                except ValueError as inst:
                    raise DigitizedException("Invalid Ingredient ID: %s" % value)
            elif self.experimental_column != None:
                value = self.sheet.cell(row,self.experimental_column[1]).value
                if value != '':
                    ing = Ingredient.objects.get(id=5090)
                    self.ingredients.append(ing)
                else:
                    raise DigitizedException("Invalid Ingredient ID and no experimental present.")
                
        