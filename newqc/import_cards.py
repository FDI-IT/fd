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

from newqc.models import Retain, ProductInfo, Lot, ImportRetain
from access.models import Flavor, Ingredient
import settings

os.chdir("%s/sample_data/qc" % settings.DUMP_DIR)
log_entry = u'"%s","%s","%s"\n'
LOG_FILENAME = 'import.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
NEW_CARD_RE = re.compile('QUALITY CONTROL FINISHED PRODUCT TESTING FORM',
                         re.IGNORECASE)
NEW_CARD_RE_TWO = re.compile('TESTING',
                         re.IGNORECASE)


SPECIAL_CELLS_NEW = (
    'name', (1,0),
    'prefix', (8,3),
    'number', (8,4),
    'testing_procedure', (6,0),
    'appearance', (1,7),
    'organoleptic_properties', (2,7),
    'flash_point', (3,7),
    'specific_gravity', (4,7) )
"""
coordinates to the corresponding properties found in a new QC card
"""

SPECIAL_CELLS_OLD = (
    'name', (0,0),
    'prefix', (3,3),
    'number', (3,4),
    'testing_procedure', (1,2) )
"""
coordinates to the corresponding properties found in an old QC card
"""

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

lot_re = re.compile('-')

def retain_row_getter(s, retain_row):
    def getter_function(x):
        return s.cell_value(retain_row, x)
    return getter_function

def get_lot_tuple(lot_num_cell):
    lot_match = lot_re.search(lot_num_cell)
    if lot_match:
        lot_number = int(lot_num_cell[:lot_match.start()])
        sub_lot_number = int(lot_num_cell[lot_match.end():])
        return (lot_number, sub_lot_number)
    else:
        print "Error getting lot tuple"
        raise
    
class MyBaseException:
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    def __unicode__(self):
        return repr(self.parameter)
    
class QCCardException(MyBaseException):
    pass

class RetainRecord:
    
    def __init__(self, row_array, path):
        """Given a row_array, get all of the info from the row
        that corresponds to a retain and store it in this object.
        """
        # Pre-declaring all of the essential values for a retain, for
        # my own sanity to see them here.
        self.retain_number = None
        self.date = None
        self.name = None
        self.prefix = None
        self.flavor_number = None
        self.lot_number = None
        self.sub_lot_number = None
        self.status = None
        self.amount = None
        self.notes = None
        
        self.path = path
        
        # simple gets
        self.retain_number = int(row_array[0].value)
        self.date = datetime.date(*xldate_as_tuple(row_array[1].value, 0)[0:3])
        self.name = unicode(row_array[2].value).strip()
        self.prefix = unicode(row_array[3].value).strip()
        self.flavor_number = int(row_array[4].value)
        self.status = unicode(row_array[6].value)
        
        # this block gets lot info
        lot_cell_value = row_array[5].value
        try:
            self.lot_number = int(lot_cell_value)
        except:
            self.lot_number, self.sub_lot_number = get_lot_tuple(lot_cell_value.strip())
        
        # this block gets amount
        try:
            self.amount = Decimal(unicode(row_array[7].value))
        except:
            pass
        
        # this block gets notes
        if self.amount is None:
            try:
                self.notes = "%s %s %s" % (row_array[7].value, row_array[8].value, row_array[9].value)
            except:
                try:
                    self.notes = "%s %s" % (row_array[7].value, row_array[8].value)
                except:
                    self.notes = row_array[7].value
        else:
            try:
                self.notes = "%s %s" % (row_array[8].value, row_array[9].value)
            except:
                try:
                    self.notes = row_array[8].value
                except:
                    self.notes = ""
        self.notes = self.notes.strip()

    def create_model_object(self):
        self.ir = ImportRetain(number=self.retain_number,
                          date=self.date,
                          name=self.name,
                          prefix=self.prefix,
                          flavor_number=self.flavor_number,
                          lot_number=self.lot_number,
                          sub_lot_number=self.sub_lot_number,
                          status=self.status,
                          amount=self.amount,
                          notes=self.notes,
                          path=self.path)
        self.ir.save()

class QCCard:
    """
    A class to help importing of QC Cards
    """
    def __init__(self, path):
        """
        Read the spreadsheet from path and populate a dictionary flavor_info
        
        self.
            path
            wb
            flavor_info
            special_cells
            my_style
        """
        self.path = path
        sheet = open_workbook(path).sheets()[0]
        scraped_flavor_info = {}
        
        # find what type of card it is and where the special cells are
        try:
            if NEW_CARD_RE.search(sheet.cell(0,0).value):
                self.special_cells = SPECIAL_CELLS_NEW
                self.retain_start_row = 8
            elif NEW_CARD_RE_TWO.search(sheet.cell(1,0).value):
                self.special_cells = SPECIAL_CELLS_OLD
                self.retain_start_row = 7
            else:
                raise QCCardException("Unable to determine card style")
        except:
            raise QCCardException("Test cell was out of range")

        # get values from the special cells and store them in a dict
        for special_cell in chunker(self.special_cells, 2):
            cell_name, loc = special_cell
            scraped_flavor_info[cell_name] = u'%s' % (sheet.cell(*loc).value)
        
        # get the flavor number from special cells
        try:    
            self.flavor_number = int(float(scraped_flavor_info.get('number', '')))
        except ValueError:
            if scraped_flavor_info.get('number', '') == 'Prod#':
                raise QCCardException("Found 111232 Caramel card")
        
        # get floating point values from special cells
        float_match = re.compile(r"\d+\.*\d*")
        for match_field in ['flash_point', 'specific_gravity']:
            matchlist = float_match.findall(scraped_flavor_info.get(match_field,''))
            if(len(matchlist) ==1):
                scraped_flavor_info[match_field] = matchlist[0]
            else:
                scraped_flavor_info[match_field] = None
                
        # get the corresponding Flavor from the number
        try:
            flavor = Flavor.objects.get(number=self.flavor_number)
        except Flavor.DoesNotExist:
            raise QCCardException("Flavor number %s does not exist." % self.flavor_number)
        
        # construct and fill in the ProductInfo object
        try:
            self.flavor_info, created = ProductInfo.objects.update_or_create(
                flavor=flavor,
                appearance = scraped_flavor_info.get('appearance', ''),
                organoleptic_properties = scraped_flavor_info.get('organoleptic_properties',''),
                testing_procedure = scraped_flavor_info.get('testing_procedure', ''),
                flash_point = scraped_flavor_info.get('flash_point', None),
                specific_gravity = scraped_flavor_info.get('specific_gravity', None),
                product_notes = scraped_flavor_info.get('notes',''),
                original_card = File(open(self.path, 'r')),
            )
            if not created:
                pass
                #log_file.write(log_entry % (self.path, "Duplicate product info", flavor.number))
        except InvalidOperation as e:
            raise QCCardException("Encountered InvalidOperation when parsing ProductInfo")
        
        # iterate over remaining rows and 
        self.retains = []
        for row_index in xrange(self.retain_start_row, sheet.nrows):
            try:
                self.retains.append(RetainRecord(sheet.row(row_index), path))
            except:
                print "Bad retain index-%s in %s file" % (row_index, self.flavor_number)
        
    def __str__(self):
        return "Card for %s" % self.flavor_number
        
    def __repr__(self):
        return "<QCCard: %s>" % self.flavor_number
       
def get_retain_row(card, s, retain_row, flavor_info):
    """
    Given a row, saves the related retain.
    """
    #import pdb; pdb.set_trace()
    flavor = flavor_info.flavor
    new_lot_num, new_sub_lot_num = get_lot_tuple( s.cell_value(retain_row,5) )
    date = get_retain_date(s.cell_value(retain_row,1))
    status = get_retain_status(s.cell_value(retain_row,6))
    amount = get_amount(s.cell_value(retain_row,7))
    # this part tests whether the lot exists or not
    existing_lots = Lot.objects.filter(number=new_lot_num, flavor=flavor, sub_lot=new_sub_lot_num)
    if existing_lots.count() > 0:
        lot = existing_lots[0]
        print "Dupe lot %s-%s found in flavor %s in %s" % (unicode(new_lot_num), unicode(new_sub_lot_num), unicode(flavor.number), card.path)
    else:
        lot = Lot(
            flavor=flavor,                                 
            number=new_lot_num, 
            sub_lot=new_sub_lot_num,
            status="FIXME!",
            amount=amount,
            date=date
        )   
        lot.save()
    
    notes = get_notes(s, retain_row)
    new_retain = Retain(
        retain=get_retain_num(s.cell_value(retain_row,0)),
        date=date,
        lot=lot,
        notes=notes,
        status=status,
    )
    
    
    new_retain.save()
    

def delete_all_cards():
    all_lots = Lot.objects.all().delete()
    all_retains = Retain.objects.all().delete()
    all_flavs = ProductInfo.objects.all().delete()
    ImportRetain.objects.all().delete()

def retains_from_card(card):
    """
    Save retains for a given card
    """
    retain_start_row = card.retain_start_row
    for s in card.wb.sheets():
        for retain_row in range(retain_start_row, s.nrows):
            get_retain_row(card, s, retain_row, card.flavor_info)


"""
The following group of functions all return data according to the type
required to construct the corresponding model object
"""
def get_retain_num( retain_num_cell ):
    """
    Returns Retain.retain (positive small int)
    """
    return int(retain_num_cell)

def get_retain_date( retain_date_cell ):
    """
    Returns Retain.date (datetime.date)
    """
    xldate = xldate_as_tuple(retain_date_cell,0)[0:3]
    return datetime.date(*xldate)

def get_product_name( product_name_cell ):
    """
    Returns Flavor.name (charfield)
    """
    return unicode(product_name_cell).strip()

def get_product_prefix( product_prefix_cell ):
    """
    Returns Flavor.prefix (charfield length=2)
    """
    return unicode(product_prefiix_cell).strip()

def get_product_number( product_number_cell ):
    """
    Returns Flavor.number (positive int)
    """
    return int(product_number_cell)

def get_retain_status( retain_status_cell ):
    """
    Returns Retain.status (charfield)
    """
    return unicode(retain_status_cell).strip()

def get_amount( lot_amount_cell ):
    """
    Returns Lot.amount (decimal)
    """
    try:
        return Decimal( unicode(lot_amount_cell) )
    except Exception as e:
        return None

def get_notes( s, retain_row ):
    """
    Returns textfield 
    """
    amount = get_amount(s.cell_value(retain_row,7))
    if amount is None:
        try:
            notes = "%s %s %s" % (s.cell_value(retain_row,7), s.cell_value(retain_row,8), s.cell_value(retain_row,9))
        except:
            try:
                notes = "%s %s" % (s.cell_value(retain_row,7), s.cell_value(retain_row,8))
            except:
                notes = s.cell_value(retain_row,7)
    else:
        try:
            notes = "%s %s" % (s.cell_value(retain_row,8), s.cell_value(retain_row,9))
        except:
            try:
                notes = s.cell_value(retain_row,8)
            except:
                notes = ""
    notes = notes.strip()
    return notes

def normalize_statuses():
    destroy_date = datetime.date(year=2009,month=1,day=1)
    for r in Retain.objects.all():
        if r.date < destroy_date:
            r.status = "Destroyed"
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
        
            
def fix_lot_statuses():
    """
    "Fix" means to set the lot to the status of the first retain.
    The first retain is going to be the most recent.
    Just do this once after importing.
    """
    for lot in Lot.objects.all():
        try:
            lot.status = lot.retains.all()[0].status
            lot.save()
        except IndexError:
            pass    

def import_flavor_cards():
    delete_all_cards()
    
    filename = '/var/www/django/dump/qc_flavor_import%s.csv' % datetime.datetime.now()
    log_file = open(filename, 'w')
    log_headers = "filename,error,additional_info\n"
    log_file.write(log_headers)
    
    
    os.chdir("/var/www/django/dump/sample_data/qc")
    card_path_list = glob.glob(u"*.[Xx][Ll][Ss]")
    card_list = []
    for card_path in card_path_list:
        try:
            card = QCCard(card_path)
        except QCCardException as e:
            print e
            continue
        except Exception as e:
            print e
            log_file.write(log_entry % (card_path, "Bad File", ''))
            continue
        
        card_list.append(card)
        
    # do these AFTER saving django model objects
    #
    # normalize_statuses()
    # fix_lot_statuses()

    log_file.close()
    
def find_common_lots(multi_lot_files):
    """Returns a list of lot numbers shared by the cards at path a and b.
    """
    filename = '/var/www/django/dump/lot_dupes-%s.csv' % datetime.datetime.now()
    log_file = codecs.open(filename, 'w', 'UTF-8')
    log_file.write("num_common;f1;f2;set\n")
    mlf_retains_cache = {}
    for mlf in multi_lot_files:
        mlf_retains_cache[mlf] = ImportRetain.objects.filter(path=mlf).values_list('lot_number')
        
        
    pair_list = []
        
    for mlf in multi_lot_files:
        mlf_retains = mlf_retains_cache[mlf]
        inner_mlfs = copy(multi_lot_files)
        inner_mlfs.remove(mlf)
        for imlf in inner_mlfs:
            imlf_retains = mlf_retains_cache[imlf]
            intersection = set(mlf_retains) & set(imlf_retains)
            common_retains = len(intersection)
            if common_retains > 0:
                if common_retains == 1:
                    intersection = intersection.pop()[0]
                    if intersection < 800000:
                        print "too old..."
                        continue
                flavor_list = sorted([int(mlf.split('_')[0]), int(imlf.split('_')[0])])
                new_pair = Set(flavor_list)
                if new_pair in pair_list:
                    print "Skipping %s" % new_pair
                    continue
                else:
                    pair_list.append(new_pair)
                    write_unicode = u"%s;%s;%s;%s\n" % (common_retains, flavor_list[0], flavor_list[1], intersection)
                    log_file.write(write_unicode)
    log_file.close()


def test(qc_path="/var/www/django/dump/sample_data/qc"):
    delete_all_cards()
    
#    filename = '/var/www/django/dump/qc_flavor_import%s.csv' % datetime.datetime.now()
#    log_file = open(filename, 'w')
#    log_headers = "filename,error,additional_info\n"
#    log_file.write(log_headers)
#    
#    
    os.chdir(qc_path)
    card_dict = {}
    failcount = 0
    for card_path in glob.glob(u"*.[Xx][Ll][Ss]"):
        try:
            card = QCCard(card_path)
            card_dict[card_path] = card
            for r in card.retains:
                r.create_model_object()
        except QCCardException as e:
            print e
            failcount += 1
            #log_file.write(log_entry % (card_path, "Bad File", ''))
        except Exception as e:
            print "Unknown error: %s" % card_path
            raise e
        
    retaincount = 0
    for card in card_dict.values():
        retaincount += len(card.retains)
        
    # here we summarize all the lots by creating a dict
    # lot_dict
    # keys: lot numbers
    # values: a list of retains that have that lot number
    lot_dict = {}
    for card in card_dict.values():
        for r in card.retains:
            lot_number = r.lot_number
            previous_list = lot_dict.get(lot_number, [])
            previous_list.append(r)
            lot_dict[lot_number] = previous_list
    
    
    # here we summarize a list of lots which reference more than one
    # retain as shown in lot_dict
    # multi_lots: list of lot numbers with more than one retain
    multi_lots = []        
    possible_multi_lots = []
    for k, v in lot_dict.iteritems():
        if len(v) > 1:
            possible_multi_lots.append(k)
    for l in possible_multi_lots:
        r_list = lot_dict[l]
        flavor_dict = {}
        for r in r_list:
            flavor_dict[r.path] = 1
        if len(flavor_dict.keys()) > 1:
            multi_lots.append(l)
    
    # here we summarize all the files which contain a multi_lot
    multi_lot_files = Set()
    for lot in multi_lots:
        retains = lot_dict[lot]
        for r in retains:
            multi_lot_files.add(r.path)
            
    # here we summarize all the filepaths that contain a multi_lot, in the
    # form of a dict, which shows which other files also share that lot.
    # path_dict
    # keys: file path
    # values: similar files
    path_dict = {}
    for lot_number in multi_lots:
        retains = lot_dict[lot_number]
        paths = []
        for r in retains:
            paths.append(r.path)
        for r in retains:
            sliced_paths = copy(paths)
            sliced_paths.remove(r.path)
            for path in sliced_paths:
                inner_dict = path_dict.get(r.path, {})
                inner_dict[path] = inner_dict.get(path, 0) + 1
                path_dict[r.path] = inner_dict
    
     
    
    print "Fail Count: %s" % failcount
    print "Retain Count: %s" % retaincount
    print "Multi Lots: %s" % len(multi_lots)

    for c in card_dict.values():
        for r in c.retains:
            retain_object = Retain()

    calculated_vals = {
        "card_dict": card_dict,
        "lot_dict": lot_dict,
        "possible_multi_lots": possible_multi_lots,
        "multi_lots": multi_lots,
        "path_dict": path_dict,
        "multi_lot_files": multi_lot_files,
    }
    
    create_lot_retain_objects(card_dict)
            
    normalize_statuses()
    fix_lot_statuses()
#    log_file.close()#
    return calculated_vals

def create_lot_retain_objects(card_dict):
    for c in card_dict.values():
        print c
        f = c.flavor_info.flavor
        for r in c.retains:
            ir = r.ir
            try:
                flavor = Flavor.objects.get(number=ir.flavor_number)
            except Flavor.DoesNotExist:
                continue
            l = Lot(
                    date=ir.date,
                    number=ir.lot_number,
                    sub_lot=ir.sub_lot_number,
                    status=ir.status,
                    amount=ir.amount,
                    flavor=flavor
                    )
            l.save()
            r = Retain(
                       retain=ir.number,
                       date=ir.date,
                       lot=l,
                       status=ir.status,
                       notes=ir.notes,
                       ir=ir
                       )
            r.save()
    