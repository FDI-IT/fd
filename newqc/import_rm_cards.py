import os
import sys
import re
import glob
import datetime
import logging
import codecs

from copy import copy

from sets import Set

from decimal import InvalidOperation
from decimal import Decimal, ROUND_HALF_UP

from xlrd import open_workbook
from xlrd import xldate_as_tuple

from django.core.files import File
from django.db import connection, transaction, IntegrityError
#from django.db.models import Q

from newqc.models import RMImportRetain, RMInfo, RMRetain
from access.models import Flavor, Ingredient
import settings

os.chdir("%s/sample_data/qc/Raw Materials/" % settings.DUMP_DIR)
log_entry = u'"%s","%s","%s"\n'
LOG_FILENAME = 'import_rm.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

SPECIAL_CELLS = (
        'name', (7,3),
        'pin', (7,1),
        'testing_procedure', (5,3)
    )

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

class MyBaseException:
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    def __unicode__(self):
        return repr(self.parameter)
    
class RMCardException(MyBaseException):
    pass

class RetainRecord:
    r_number_pattern = re.compile('(\d+)')
    def __init__(self, row_array, path):
        """Given a row_array, get all of the info from the row
        that corresponds to a retain and store it in this object.
        """
        # Pre-declaring all of the essential values for a retain, for
        # my own sanity to see them here.        
        self.path = path
        
        # simple gets
        self.date = datetime.date(*xldate_as_tuple(row_array[0].value, 0)[0:3])
        self.pin = int(row_array[1].value)
        self.supplier = unicode(row_array[2].value).strip()
        self.name = unicode(row_array[3].value).strip()
        self.lot = unicode(row_array[4].value)
        
        
        
        r_number_cell = row_array[5].value
        if r_number_cell == "":
            self.r_number = 0
        else:
            try:
                r_num_int = int(r_number_cell)
                self.r_number = r_num_int
            except:
                r_number_str = str(r_number_cell)
                r_number_result = self.r_number_pattern.search(r_number_str)
            
                if r_number_result is not None:
                    self.r_number = r_number_result.group()
                else:
                    raise RMCardException( "Unable to scrape r_number: %s" % row_array[5].value )
            
        if self.r_number == "":
            raise RMCardException( "Unable to scrape r_number: %s" % row_array[5].value )
        
        self.status = unicode(row_array[6].value).strip()
        try:
            self.notes = unicode(row_array[8].value).strip()
        except:
            self.notes = ""

    def create_model_object(self):
        sid = transaction.savepoint()
        self.ir = RMImportRetain(
                          date=self.date,
                          pin=self.pin,
                          supplier=self.supplier,
                          name=self.name,
                          lot=self.lot,
                          r_number=self.r_number,
                          status=self.status,
                          notes=self.notes,)
        
        try:
            self.ir.save()
            transaction.savepoint_commit(sid)
        except Exception as e:
            print ("Unhandled Exception: %s -- %s" % (self.ir, e)).rstrip()
            transaction.savepoint_rollback(sid)
            
    
class RMCard:
    """
    A class to help importing of RM Cards
    """
    def __init__(self, path):
        """
        Read the spreadsheet from path and populate a dictionary flavor_info
        
        self.
            path
            wb
            special_cells
        """
        self.path = path
        sheet = open_workbook(path).sheets()[0]
        scraped_rm_info = {}
        
        # get values from the special cells and store them in a dict
        for special_cell in chunker(SPECIAL_CELLS, 2):
            cell_name, loc = special_cell
            scraped_rm_info[cell_name] = u'%s' % (sheet.cell(*loc).value)
        
        # get the flavor number from special cells
        try:
            self.pin = int(float(scraped_rm_info.get('pin', '')))
        except Exception as e:
            raise RMCardException("Unable to scrape info from %s: %s" % (path,e))

        # get the corresponding Flavor from the number
        rms = Ingredient.objects.filter(id=self.pin).order_by('-discontinued')
        try:
            rm = rms[0]
        except IndexError:
            raise RMCardException("PIN doesn't exist: %s" % self.pin)
        
        self.rm_info = RMInfo(
                pin=self.pin,
                testing_procedure=scraped_rm_info.get('testing_procedure', ''),
                notes=scraped_rm_info.get('notes',''),
                original_card = File(open(self.path, 'r')),
            )
        self.rm_info.save()
        
        # iterate over remaining rows and 
        self.retains = []
        for row_index in xrange(7, sheet.nrows):
            try:
                self.retains.append(RetainRecord(sheet.row(row_index), path))
            except Exception as e:
                print "Bad retain index-%s in %s file: %s" % (row_index, self.pin, e)
        
    def __str__(self):
        return "Card for %s" % self.pin
        
    def __repr__(self):
        return "<RMCard: %s>" % self.pin
  

def delete_all_cards():
    RMImportRetain.objects.all().delete()
    RMInfo.objects.all().delete()
    RMRetain.objects.all().delete()

def normalize_statuses():
    destroy_date = datetime.date(year=2009,month=1,day=1)
    for r in RMRetain.objects.all():
        if r.date < destroy_date:
            r.status = "Expired"
            r.save()
        else:
            s = r.status
            if (s == 'pass' or
                s == 'passed' or
                s == 'Pass'):
                r.status = 'Passed'
                r.save()
            elif (s == 'reject' or
                  s == 'rejected' or
                  s == 'Reject'):
                r.status = 'Rejected'
                r.save()

def test(rm_path="/var/www/django/dump/sample_data/qc/Raw Materials/"):
    delete_all_cards()
    
#    filename = '/var/www/django/dump/qc_flavor_import%s.csv' % datetime.datetime.now()
#    log_file = open(filename, 'w')
#    log_headers = "filename,error,additional_info\n"
#    log_file.write(log_headers)
#    
#    
    os.chdir(rm_path)
    card_dict = {}
    failcount = 0
    for card_path in glob.glob(u"*.[Xx][Ll][Ss]"):
        try:
            #print card_path
            card = RMCard(card_path)
            card_dict[card_path] = card
            for r in card.retains:
                r.create_model_object()
        except RMCardException as e:
            print "RMCardException %s: %s" % (card_path,e,)
            failcount += 1
            #log_file.write(log_entry % (card_path, "Bad File", ''))
    create_rm_retain_objects(card_dict)
    return card_dict
    
#    retaincount = 0
#    for card in card_dict.values():
#        retaincount += len(card.retains)
#        
#    # here we summarize all the lots by creating a dict
#    # lot_dict
#    # keys: lot numbers
#    # values: a list of retains that have that lot number
#    lot_dict = {}
#    for card in card_dict.values():
#        for r in card.retains:
#            lot_number = r.lot_number
#            previous_list = lot_dict.get(lot_number, [])
#            previous_list.append(r)
#            lot_dict[lot_number] = previous_list
#    
#    
#    # here we summarize a list of lots which reference more than one
#    # retain as shown in lot_dict
#    # multi_lots: list of lot numbers with more than one retain
#    multi_lots = []        
#    possible_multi_lots = []
#    for k, v in lot_dict.iteritems():
#        if len(v) > 1:
#            possible_multi_lots.append(k)
#    for l in possible_multi_lots:
#        r_list = lot_dict[l]
#        flavor_dict = {}
#        for r in r_list:
#            flavor_dict[r.path] = 1
#        if len(flavor_dict.keys()) > 1:
#            multi_lots.append(l)
#    
#    # here we summarize all the files which contain a multi_lot
#    multi_lot_files = Set()
#    for lot in multi_lots:
#        retains = lot_dict[lot]
#        for r in retains:
#            multi_lot_files.add(r.path)
#            
#    # here we summarize all the filepaths that contain a multi_lot, in the
#    # form of a dict, which shows which other files also share that lot.
#    # path_dict
#    # keys: file path
#    # values: similar files
#    path_dict = {}
#    for lot_number in multi_lots:
#        retains = lot_dict[lot_number]
#        paths = []
#        for r in retains:
#            paths.append(r.path)
#        for r in retains:
#            sliced_paths = copy(paths)
#            sliced_paths.remove(r.path)
#            for path in sliced_paths:
#                inner_dict = path_dict.get(r.path, {})
#                inner_dict[path] = inner_dict.get(path, 0) + 1
#                path_dict[r.path] = inner_dict
#    
#     
#    
#    print "Fail Count: %s" % failcount
#    print "Retain Count: %s" % retaincount
#    print "Multi Lots: %s" % len(multi_lots)
#
#    for c in card_dict.values():
#        for r in c.retains:
#            retain_object = Retain()
#
#    calculated_vals = {
#        "card_dict": card_dict,
#        "lot_dict": lot_dict,

#            
#        "possible_multi_lots": possible_multi_lots,
#        "multi_lots": multi_lots,
#        "path_dict": path_dict,
#        "multi_lot_files": multi_lot_files,
#    }
#    

#            
#    normalize_statuses()
#    fix_lot_statuses()
##    log_file.close()#
#    return calculated_vals

def create_rm_retain_objects(card_dict):
    for c in card_dict.values():
        #print c.rm_info
        for r in c.retains:
            sid = transaction.savepoint()            
            try: 
                ir = r.ir
                r = RMRetain(
                           date=ir.date,
                           pin=ir.pin,
                           supplier=ir.supplier,
                           lot=ir.lot,
                           r_number=ir.r_number,
                           status=ir.status,
                           notes=ir.notes,
                           ir=ir
                           )
                r.save()
                transaction.savepoint_commit(sid)
            except Exception as e:
                print ("Unhandled Exception: %s -- %s" % (ir, e)).rstrip()
                transaction.savepoint_rollback(sid)
    