import csv
from decimal import Decimal

from datetime import datetime


class SalesOrderLineGenerator():
    pass

def quickbooks_date_fix(d):
    return datetime.strptime(d,'%m/%d/%Y')

class SalesOrderGenerator():
    """
    A generator that yields sales order objects given a path to a quickbooks
    report.
    """
    required_headers = {
            'Num':int,
            'Date':quickbooks_date_fix,
            'P. O. #':lambda x: x,
            'Name':lambda x: x,
            'Item':lambda x: x,
            'Item Description':lambda x: x,
            'Qty':Decimal,
            'Sales Price':Decimal,
            'Ship Date':quickbooks_date_fix,
            'Due Date':quickbooks_date_fix,
            'Amount':Decimal,
        }
    
    def __init__(self, report_file):
        self.report_reader = csv.reader(report_file,
                                        delimiter=',',
                                        quotechar='"')
        self.header_row = next(self.report_reader)
        self.header_row_b = next(self.report_reader)
        self.cell_keys = {}
        for index, col_header in enumerate(self.header_row):
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
        my_headers = list(self.required_headers.keys())
        for header in self.required_headers:
            if header in self.cell_keys:
                my_headers.remove(header)
        return my_headers
                                       
    def __iter__(self):
        return self
    
    def __next__(self):
        """
        TODO this isn't good, the examination of the row and saving 
        corresponding model objects are coupled here.
        """
        return next(self.report_reader)
    
    def try_line_item(self, row):
        # probably want to test for row validity here
        #
        # get or create Customer from qb field Name
        li = {}
        for k, v in self.cell_keys.items():
            h = self.required_headers[k]
            li[k] = h(row[v])
        return li
    
class ReportException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class SalesOrderException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    
class LineItemException(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
