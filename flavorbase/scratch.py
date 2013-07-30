import os
import sys
import re
import glob
import datetime

from decimal import InvalidOperation
from decimal import Decimal, ROUND_HALF_UP

from xlrd import open_workbook
from xlrd import xldate_as_tuple

from django.core.files import File
from django.db import connection, transaction, IntegrityError

from newqc.models import Retain, ProductInfo, TestCard, Lot
from access.models import Flavor, Ingredient
import settings

os.chdir("%s/qc" % settings.DUMP_DIR)
log_entry = '"%s","%s","%s"\n'
lot_re = re.compile('-')

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))


class QCCard:
    """
    A class to help importing of QC Cards
    """

    special_cells_new = (
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

    special_cells_old = (
        'name', (0,0),
        'prefix', (3,3),
        'number', (3,4),
        'testing_procedure', (1,2) )
    """
    coordinates to the corresponding properties found in an old QC card
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
        self.wb = open_workbook(path)
        self.flavor_info = {}
        
        new_card_re = re.compile('QUALITY CONTROL FINISHED PRODUCT TESTING FORM',
                                 re.IGNORECASE)
        self.my_style = "FAIL"
        for s in self.wb.sheets():
            testcell = s.cell(0,0).value
            if new_card_re.search(testcell):
                self.special_cells = QCCard.special_cells_new
                self.my_style = "NEW"
            else:
                self.special_cells = QCCard.special_cells_old
                self.my_style = "OLD"
        
        for special_cell in chunker(self.special_cells, 2):
            cell_name, loc = special_cell
            self.flavor_info[cell_name] = u'%s' % (s.cell(*loc).value)

def delete_all_cards():
    all_lots = Lot.objects.all().delete()
    all_retains = Retain.objects.all().delete()
    all_flavs = ProductInfo.objects.all().delete()
    all_tcs = TestCard.objects.all().delete()

def flavor_from_card( card,i,log_file ):
    """
    Save a flavor from a given card, or exit the program.
    """
    
    #try:
    flavor_number = int(float(i.get('number', '')))
    
    float_match = re.compile(r"\d+\.*\d*")
    for match_field in ['flash_point', 'specific_gravity']:
        matchlist = float_match.findall(i.get(match_field,''))
        if(len(matchlist) ==1):
            i[match_field] = matchlist[0]
        else:
            i[match_field] = None

    flavor = Flavor.objects.get(number=flavor_number)
    flavor_info, created = ProductInfo.objects.get_or_create(
        flavor=flavor,
    )
    if created:
        flavor_info.appearance = i.get('appearance', '')
        flavor_info.organoleptic_properties = i.get('organoleptic_properties',
                                        '')
        flavor_info.testing_procedure = i.get('testing_procedure', '')
        flavor_info.flash_point = i.get('flash_point', None)
        flavor_info.specific_gravity = i.get('specific_gravity', None)
        flavor_info.notes = i.get('notes','')
        flavor_info.original_card = File(open(card.path, 'r'))
    else:
        log_file.write(log_entry % (card.path, "Duplicate product info", flavor.number))
               
    flavor_info.save()

    card.flavor_info = flavor_info
    card.flavor = flavor
    
def retains_from_card(card):
    """
    Save retains for a given card
    """
    if(card.my_style == "NEW"):
        retain_start_row = 8
    else:
        retain_start_row = 7
    for s in card.wb.sheets():
        for retain_row in range(retain_start_row, s.nrows):
            get_retain_row(card, s, retain_row, card.flavor_info)


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
        print "Dupe lot %s-%s found in flavor %s in %s" % (str(new_lot_num), str(new_sub_lot_num), str(flavor.number), card.path)
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
    return str(product_name_cell).strip()

def get_product_prefix( product_prefix_cell ):
    """
    Returns Flavor.prefix (charfield length=2)
    """
    return str(product_prefiix_cell).strip()

def get_product_number( product_number_cell ):
    """
    Returns Flavor.number (positive int)
    """
    return int(product_number_cell)

def get_lot_tuple( lot_num_cell ):
    """
    Returns a tuple (lot, sub-lot) (positive int, positive int)
    """
    try:
        lot_num = int(lot_num_cell)
        return lot_num, None
    except:
        lot_match = lot_re.search(lot_num_cell)
        if lot_match:
            lot_number = int(lot_num_cell[:lot_match.start()])
            sub_lot_number = int(lot_num_cell[lot_match.end():])
        else:
            print "Error getting lot tuple"
            raise
    return (lot_number, sub_lot_number)

def get_retain_status( retain_status_cell ):
    """
    Returns Retain.status (charfield)
    """
    return str(retain_status_cell).strip()

def get_amount( lot_amount_cell ):
    """
    Returns Lot.amount (decimal)
    """
    try:
        return Decimal( str(lot_amount_cell) )
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
    for r in Retain.objects.all():
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
    for lot in Lot.objects.all():
        try:
            lot.status = lot.retain_set.all()[0].status
            lot.save()
        except IndexError:
            pass        

def import_flavor_cards():
    delete_all_cards()
    
    filename = '/usr/local/django/dump/qc_flavor_import%s.csv' % datetime.datetime.now()
    log_file = open(filename, 'w')
    log_headers = "filename,error,additional_info\n"
    log_file.write(log_headers)
    
    
    os.chdir("/usr/local/django/dump/qc")
    card_path_list = glob.glob("*.[Xx][Ll][Ss]")
    card_list = []
    for card_path in card_path_list:
        try:
            card = QCCard(card_path)
            card_list.append(card)
            i = card.flavor_info
            flavor_number = int(float(i.get('number', ''))) 
        except:
            log_file.write(log_entry % (card_path, "Bad File", ''))
            continue
                
        try:
            flavor = Flavor.objects.get(number=flavor_number)
        except Flavor.DoesNotExist:
            log_file.write(log_entry % (card_path, "Flavor Does Not Exist", ''))
            continue 
        except Exception as e:
            log_file.write(log_entry % (card_path, "Other Flavor Error", str(e)))
            continue
        
        try:
            flavor_from_card(card,i,log_file)        
        except InvalidOperation as e:
            log_file.write(log_entry % (card_path, 'InvalidOperation', str(e)))
            continue
        
        try:
            retains_from_card(card)
        except Exception as e:
            log_file.write(log_entry % (card_path, 'Bad Retains', str(e)))
            continue
        
    normalize_statuses()
    fix_lot_statuses()

