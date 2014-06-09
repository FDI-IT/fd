import os
import re
from datetime import date, datetime

from django.contrib.contenttypes.models import ContentType

from reversion.models import Revision, Version

from newqc.models import ScannedDoc, TestCard, RMTestCard, BatchSheet, GenericTestCard

filename_date_re = re.compile('(?P<year>\d{4})_(?P<month>\d{2})_(?P<date>\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})')

def get_full_object_list():
    object_list = []
    Models_to_scan = (TestCard, RMTestCard, BatchSheet, GenericTestCard)
    
    for Model in Models_to_scan:
        object_list.extend(Model.objects.all())
        
    return object_list

old = date(1990,1,1)

def scanned_doc_key_function(scanned_doc):
    related_obj = scanned_doc.related_object
    print related_obj
    if related_obj is not None:
        return related_obj.date
    return old

def convert_datetime_dict_values_to_int(datetime_dict):
    for k,v in datetime_dict.iteritems():
        datetime_dict[k] = int(v)
    return datetime_dict

def get_create_time_for_content_object(content_object):
    m = filename_date_re.match(os.path.basename(content_object.large.name))
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
        create_time = old
    return create_time

def test():
    ScannedDoc.objects.all().delete()
    full_object_list = get_full_object_list()
    sorted_full_object_list = sorted(full_object_list, key=scanned_doc_key_function)
    for scanned_doc in sorted_full_object_list:
        s = ScannedDoc(content_object=scanned_doc)
        s.content_object.create_time  = get_create_time_for_content_object(scanned_doc)
        s.content_object.save()
        s.save()
        print s
    

def main():
    object_list = get_full_object_list()
    return object_list
        
    
if __name__ == "__main__":
    main()
