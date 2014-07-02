import os
import re
import logging
import errno
from datetime import date, datetime

from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from reversion import revision

from newqc.models import *

# matches a date given a file formatted a certain way from our scanner
FILENAME_DATE_RE = re.compile('(?P<year>\d{4})_(?P<month>\d{2})_(?P<date>\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})')

# set up logging
LOG_PATH = '/var/log/django/'
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/populate_scanned_docs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logger = logging.getLogger()

# maps the old models to the new ones
old_new_type_map = {
        OldTestCard: TestCard,
        OldRMTestCard: RMTestCard,
        OldBatchSheet: BatchSheet,                
    }

# if a date can't be inferred, use this one
OLD = datetime(1990,1,1)

def create_new_related_object(old_scanned_doc):
    """Given an old model object, instantiate a new one based on it.
    """
    NewType = old_new_type_map[type(old_scanned_doc)]
    
    large = File(open(old_scanned_doc.large.path,'r'))
    thumbnail = File(open(old_scanned_doc.thumbnail.path,'r'))
    scan_time = get_create_time_for_content_object(old_scanned_doc)
    related_object_name = old_scanned_doc.related_object_name
    related_object = getattr(old_scanned_doc, related_object_name)
    
    new_object_kwargs = {
        'image_hash': old_scanned_doc.image_hash,
        'large': large,
        'thumbnail': thumbnail,
        'notes': old_scanned_doc.notes,
        'scan_time': scan_time,
        related_object_name: related_object,
    }
    
    return NewType(**new_object_kwargs)

def scrub_old_data():
    """Fix minor errors before they would come up when instantiating
    new objects.
    """
    
    for tc in OldTestCard.objects.filter(retain=None):
        g = OldGenericTestCard(
                image_hash=tc.image_hash,
                large=tc.large,
                thumbnail=tc.thumbnail,
                notes=tc.notes,
                create_time=tc.create_time,
                modified_time=tc.modified_time,                   
            )
        g.save()
        tc.delete()

def get_full_object_list():
    """Gets all of the objects to scan.
    """
    object_list = []
    Models_to_scan = (
                      OldTestCard, 
                      OldRMTestCard, 
                      OldBatchSheet,
                      )
    
    for Model in Models_to_scan:
        object_list.extend(Model.objects.all())
        
    return object_list

def scanned_doc_pre_key_function(scanned_doc):
    """Key function to sort all model objects based on date, so that they
    can be inserted into the new models in date order.
    """
    m = FILENAME_DATE_RE.match(os.path.basename(scanned_doc.large.name))
    if m is not None:
        datetime_dict = m.groupdict()
        datetime_dict = convert_datetime_dict_values_to_int(datetime_dict)
        create_time = datetime(
            datetime_dict['year'],
            datetime_dict['month'],
            datetime_dict['date'],
            datetime_dict['hour'],
            datetime_dict['minute'],     
        )
        ret_val = create_time
    else:
        related_obj = scanned_doc.related_object
        if related_obj is None:
            ret_val = OLD
        else:
            ret_val = datetime.combine(related_obj.date, datetime.min.time())
    return ret_val

def convert_datetime_dict_values_to_int(datetime_dict):
    """Converts FILENAME_DATE_RE matches to a format usable by datetime
    """
    for k,v in datetime_dict.iteritems():
        datetime_dict[k] = int(v)
    return datetime_dict

def get_create_time_for_content_object(content_object):
    """Tries to infer the closest create time of a file, else returns OLD
    """
    m = FILENAME_DATE_RE.match(os.path.basename(content_object.large.name))
    if m is not None:
        datetime_dict = m.groupdict()
        datetime_dict = convert_datetime_dict_values_to_int(datetime_dict)
        create_time = datetime(
            datetime_dict['year'],    
            datetime_dict['month'],
            datetime_dict['date'],
            datetime_dict['hour'],
            datetime_dict['minute'],                       
        )
    else:
        create_time = OLD
    return create_time

@revision.create_on_success
def process_scanned_doc(scanned_doc):
    logger.info("Migrating %s:%s" % (type(scanned_doc), scanned_doc.pk))
    try:
        s = create_new_related_object(scanned_doc)
        s.save()
        migration_string = "Migrated from %s:%s" % (type(scanned_doc), scanned_doc.pk) 
        revision.comment = migration_string
        logger.info(migration_string)
    except IOError as e:
        logger.warn("IOError on %s:%s -- %s" % (type(scanned_doc), scanned_doc.pk, e))
    except Exception as e:
        logger.error("Unmanaged exception '%s' on %s:%s -- %s" % (type(e), type(scanned_doc), scanned_doc.pk, e))

def execute():
    """For every object in the old models, try to instantiate a new
    model object.
    """
    scrub_old_data()
    ScannedDoc.objects.all().delete()    
    logger.info("Cleared ScannedDoc model")
    full_object_list = get_full_object_list()
    sorted_full_object_list = sorted(full_object_list, key=scanned_doc_pre_key_function)
    for scanned_doc in sorted_full_object_list:
        process_scanned_doc(scanned_doc)

def main():
    logger.info("Starting to migrate scanned docs")
    execute()
    
if __name__ == "__main__":
    main()
