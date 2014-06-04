from datetime import date

from django.contrib.contenttypes.models import ContentType

from reversion.models import Revision, Version

from newqc.models import ScannedDoc, TestCard, RMTestCard, BatchSheet, GenericTestCard


def get_full_object_list():
    object_list = []
    Models_to_scan = (TestCard, RMTestCard, BatchSheet, GenericTestCard)
    
    for Model in Models_to_scan:
        object_list.extend(Model.objects.all())
        
    return object_list

old = date(1990,1,1)
def scanned_doc_key_function(scanned_doc):
    related_obj = scanned_doc.get_related_object()
    print related_obj
    if related_obj is not None:
        return related_obj.date
    return old

def test():
    sorted_full_object_list = sorted(get_full_object_list(), key=scanned_doc_key_function)
    for scanned_doc in sorted_full_object_list:
        s = ScannedDoc(content_object=scanned_doc)
        s.save()
        print s
    

def main():
    object_list = get_full_object_list()
    return object_list
        
    
if __name__ == "__main__":
    main()
