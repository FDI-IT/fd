import os

from newqc.models import ScannedDoc, RecoveredImage

from PIL import Image
from django.core.files import File

def regenerate_thumbnails():
    counter = 0
    for scanned_doc in ScannedDoc.objects.all():
        if not os.path.isfile(scanned_doc.thumbnail.path):
            generate_thumbnail(scanned_doc)
            print counter
            counter += 1
            
    print counter
    
def generate_thumbnail(scanned_doc):
    
    image_path = scanned_doc.large.path
    try:
        image = Image.open(image_path)
        
        width, height = image.size
        if width > height:
            tn = image.resize((490,380), Image.ANTIALIAS)
        else:
            tn = image.resize((380,490), Image.ANTIALIAS)
        tn_path = os.path.join(
                '/tmp',
    
                '%s-tn.png' % scanned_doc.image_hash)
        tn.save(tn_path)
        thumbnail_file = File(open(tn_path,'r'))
   
        scanned_doc.thumbnail = thumbnail_file
        scanned_doc.save()

    except Exception as e:
        print "Unable to Image.open('%s') -- %s" % (image_path, repr(e))
        return    
    
def find_scanned_docs_without_images(output_file):
    f = open(output_file, 'w')
    count = 0
    
    for scanned_doc in ScannedDoc.objects.all():
        
        if not os.path.isfile(scanned_doc.large.path):
            f.write('%s\n' % scanned_doc.pk)
            print 'Scanned Doc with pk %s has no large image' % scanned_doc.pk
            count += 1            

    print 'Total: %s' % count
    f.close()
