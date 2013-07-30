import os
import sys
import re
import glob
import datetime
import logging
from xlrd import open_workbook
from xlrd import xldate_as_tuple
from fd.qc.models import Retain
from fd.flavorbase.models import Flavor
from django.db import connection, transaction, IntegrityError
from fd.production.models import Lot

LOG_FILENAME = '/home/stachurski/fd/qc/import.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in xrange(0, len(seq), size))

lot_re = re.compile('-')

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
        """
        try:
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

        except UnicodeEncodeError, err:
            print repr(s.cell(*loc).value)
            print self.wb.codepage
            print err
            print path

def glob_cards():
    """
    iterates over QC cards.
    """

    delete_all_cards()

    os.chdir("/home/stachurski/qcc")
    cardlist = glob.glob("*.[Xx][Ll][Ss]")
    for card_path in cardlist:
        print card_path
        card = QCCard(card_path)
        my_flavor = flavor_from_card(card)
        retains_from_card(card, my_flavor)

def delete_all_cards():

    all_retains = Retain.objects.all()
    all_retains.delete()
    all_flavs = Flavor.objects.all()
    all_flavs.delete()

def flavor_from_card( card ):
    """
    Save a flavor from a given card, or exit the program.
    """
    
    i = card.flavor_info
    try:
        flavor_number = int(float(i.get('number', '')))

        float_match = re.compile(r"\d+\.*\d*")
        for match_field in ['flash_point', 'specific_gravity']:
            matchlist = float_match.findall(i.get(match_field,''))
            if(len(matchlist) ==1):
                i[match_field] = matchlist[0]
            else:
                i[match_field] = None

        f = Flavor(prefix = i.get('prefix'),
                   appearance = i.get('appearance', ''),
                   organoleptic_properties = i.get('organoleptic_properties', ''),
                   testing_procedure = i.get('testing_procedure', ''),
                   flash_point = i.get('flash_point', None),
                   specific_gravity = i.get('specific_gravity', None),
                   name = i.get('name'),
                   number = flavor_number)
        
        f.save()
        return f
    except IntegrityError:
        transaction.rollback()
    except Exception, err:
        logging.debug("Error " + err.message)
        logging.debug(type(err))
        logging.debug(i)

def retains_from_card( card, flavor ):
    """
    Save retains for a given card
    """
    print flavor
    if(card.my_style == "NEW"):
        retain_start_row = 8
    else:
        retain_start_row = 7
    
    retain_list = []

    for s in card.wb.sheets():
        for retain_row in range(retain_start_row, s.nrows):
            try:
                sid = transaction.savepoint()
                get_retain_row(s, retain_row, flavor)
            except IntegrityError:
                print "caught integrity error"
                transaction.savepoint_rollback(sid)

def get_retain_row(s, retain_row, flavor):
    """
    Given a row, saves the related retain.
    """
    new_lot_num, new_sub_lot_num = get_lot_tuple( s.cell_value(retain_row,5) )
    new_lot = Lot(
        lot = new_lot_num,
        sub_lot = new_sub_lot_num,
        flavor = flavor,
    )
    new_lot.save()
    
    new_retain = flavor.retains.create(
        retain = get_retain_num( s.cell_value(retain_row,0) ),
        date = get_retain_date( s.cell_value(retain_row,1) ),
        status = get_retain_status( s.cell_value(retain_row,6) ),
    )
    new_retain.lot = new_lot
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
    return product_name_cell

def get_product_prefix( product_prefix_cell ):
    """
    Returns Flavor.prefix (charfield length=2)
    """
    return product_prefiix_cell

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
            print lot_number
            print sub_lot_number
            raise Exception
    return (lot_number, sub_lot_number)

def get_retain_status( retain_status_cell ):
    """
    Returns Retain.status (charfield)
    """
    return retain_status_cell

def get_amount( lot_amount_cell ):
    """
    Returns Lot.amount (decimal)
    """
    return Decimal( lot_amount_cell )

def get_notes( retain_notes_cell ):
    """
    Returns textfield 
    """
    return retain_notes_cell
