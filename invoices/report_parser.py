import os
import sys
import re
import glob
import datetime
import logging
import csv
import decimal
import hashlib
from decimal import Decimal, InvalidOperation

from operator import itemgetter
from datetime import date, datetime

from access.models import Flavor

class SalesOrderLineGenerator():
    pass

def quickbooks_date_fix(d):
    return datetime.strptime(d,'%m/%d/%Y').date()

def quickbooks_flavor_fix(flavor_cell):
    # skip these common dead-ends
    if flavor_cell == '' or flavor_cell[:5] == 'Total':
        return None
    if (flavor_cell == '1' or 
        flavor_cell == '2' or # corresponds to shippin
        flavor_cell == 'Minimum Order Charge'):
        return False
    # a regex to detect a suffix     after a flavor number
    match = re.search(r'([0-9]+)',flavor_cell)
    try:
        if match:
            flavor = match.group(1)
            print match.groups()
        else:
            flavor = flavor_cell
    except:
        return False
        #raise InvoiceException("Invalid Flavor number: %s" % flavor_cell)
    
    print flavor_cell
    return flavor

class InvoiceGenerator():
    """
    A generator that yields sales order objects given a path to a quickbooks
    report.
    """
    required_headers = {
            'Num':int,
            'Date':quickbooks_date_fix,
            'Name':lambda x: x,
            'Qty':Decimal,
            'Sales Price':Decimal,
            'Amount':Decimal,
        }
    
    def __init__(self, report_file):
        self.flavor = None
        self.report_reader = csv.reader(report_file,
                                        delimiter=',',
                                        quotechar='"')
        self.header_row = self.report_reader.next()
        self.header_row_b = self.report_reader.next()
        self.cell_keys = {}
        for index, col_header in enumerate(self.header_row):
            if col_header in self.required_headers:
                self.cell_keys[col_header] = index
        missing_headers = self.missing_required_headers()
        if missing_headers:
            raise ReportException(
                    "Report is missing the following required headers: %s" %
                    repr(missing_headers))
            
    def missing_required_headers(self):
        """
        Starts with the length of required headers, and subtracts one for each
        of the required headers found. If all of them are found, the value 
        should be an empty list.
        """
        my_headers = self.required_headers.keys()
        for header in self.required_headers:
            if header in self.cell_keys:
                my_headers.remove(header)
        return my_headers
                                       
    def __iter__(self):
        return self
    
    def next(self):
        while(True):
            n = self.report_reader.next()
            try:
                x = self.try_line_item(n)
            except InvalidOperation:
                continue
            except LineItemException:
                continue
            if x['flavor'] == False:
                continue
            return x
            
    def try_line_item(self, row):
        # probably want to test for row validity here
        #
        # get or create Customer from qb field Name
        new_flavor = quickbooks_flavor_fix(row[0])
        
        if new_flavor is not None:
            self.flavor = new_flavor

        li = {}
        for k, v in self.cell_keys.iteritems():
            h = self.required_headers[k]
            li[k] = h(row[v])
        li['flavor'] = self.flavor
        return li
            
class TotalInvoiceReportParser():
    required_headers = {
            'Date':quickbooks_date_fix,
            'Qty':Decimal,
        }
    def __init__(self, report_file):
        
        
        self.report_reader = csv.reader(report_file,
                                        delimiter=',',
                                        quotechar='"')
        self.header_row_a = self.report_reader.next()
        self.header_row_b = self.report_reader.next()
        self.cell_keys = {}
        for index, col_header in enumerate(self.header_row_a):
            if col_header in self.required_headers:
                self.cell_keys[col_header] = index
                
    def __iter__(self):
        return self
    
    def next(self):
        while(True):
            n = self.report_reader.next()
            
            try:
                x = self.try_line_item(n)
#            except InvalidOperation:
#                continue
            except ValueError as e:
                continue
            if x['flavor'] == False:
                continue
            return x
            
    def try_line_item(self, row):
        # probably want to test for row validity here
        #
        # get or create Customer from qb field Name
        new_flavor = quickbooks_flavor_fix(row[0])
        
        if new_flavor is not None:
            self.flavor = new_flavor

        li = {}
        for k, v in self.cell_keys.iteritems():
            h = self.required_headers[k]
            li[k] = h(row[v])
        li['flavor'] = self.flavor
        return li
    
class InvoiceLineGenerator():
    """
    A generator that yields sales order objects given a path to a quickbooks
    report.
    """
    
    def __init__(self, report_file):
        self.report_reader = csv.reader(report_file,
                                        delimiter=',',
                                        quotechar='"')
        self.date_row = self.report_reader.next()
        self.header_row_a = self.report_reader.next()
        self.header_row_b = self.report_reader.next()
        self.cell_keys = {
            'flavor_number': 0,
            'weight': 1,
        }
                                       
    def __iter__(self):
        return self
    
    def next(self):
        """
        TODO this isn't good, the examination of the row and saving 
        corresponding model objects are coupled here.
        """
        return self.report_reader.next()
    
    def try_line_item(self, row):
        #import pdb; pdb.set_trace()
        # probably want to test for row validity here
        #
        try:
            weight_cell = Decimal(row[self.cell_keys['weight']])
        except:
            weight_cell = Decimal('0')
        
        # get or create Flavor from qb field Item
        flavor_cell = row[self.cell_keys['flavor_number']]
        # skip these common dead-ends
        if (flavor_cell == '' or
            flavor_cell == '2' or # corresponds to shippin
            flavor_cell == 'Minimum Order Charge'):
            return
        # a regex to detect a suffix after a flavor number
        match = re.search(r'([0-9]*)\.',flavor_cell)
        if match:
            flavor = Flavor.objects.get(number=match.group(1))
                #raise InvoiceException("Flavor does not exist: %s" % flavor_cell)
        else:
            flavor = Flavor.objects.get(number=flavor_cell)
                #raise InvoiceException("Invalid Flavor number: %s" % flavor_cell)
            
        return (flavor, weight_cell)

class ReportException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class InvoiceException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class LineItemException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
