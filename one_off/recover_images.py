import os

from newqc.models import ScannedDoc, RecoveredImage
from pluggable.hashing import sha_hash


from PIL import Image
from django.core.files import File


def save_all_recovered_image_paths(rootpath):
    for root, subdirs, files in os.walk(rootpath):
        for filename in files:
            if any(suffix in filename for suffix in ['.png', '.jpg']):
                
                file_path = os.path.join(root, filename)
                
                recovered_image = RecoveredImage(recovery_path = file_path)
                recovered_image.save()
                
def recover_scanned_images(rootpath):
    for recovered_image in RecoveredImage.objects.filter(hash=""):
        image_hash = sha_hash(recovered_image.recovery_path)
        recovered_image.image_hash = image_hash
        recovered_image.save()
    
    

def recover_scanned_images(rootpath, output_file):
        
    total_count = ScannedDoc.objects.count()
    recovered_image_count = RecoveredImage.objects.count()
     
    images_left_to_recover = total - recovered_image_count
    
    STORAGE_LOCATION = '/var/www/djangomedia/'
    
    f = open(output_file, 'w')
    recovery_count = 0
    
    for root, subdirs, files in os.walk(rootpath):
        
        for filename in files:
            if any(suffix in filename for suffix in ['.png', '.jpg']):
                file_path = os.path.join(root, filename)
                hash = sha_hash(file_path)
                
                if ScannedDoc.objects.filter(image_hash=hash).exists():
                    sd = ScannedDoc.objects.get(image_hash=hash)
                    sd_path = sd.large.name

                    f.write('ScannedDoc found at %s.\n' % (file_path))
                    f.flush()
                    
                    recovered_image = RecoveredImage(scanned_doc = sd,
                                                     recovery_path = file_path)
                    recovered_image.save()
                    
                    destination = '%s%s' % (STORAGE_LOCATION, sd_path)
                    os.rename(file_path, destination)
                    
                    f.write('Successfully moved to %s.\n' % destination)
                    
                    recovery_count += 1
    
        f.write('Recovered %s/%s files.\n' % (recovery_count, images_left_to_recover))
    f.close()
                    
                    
                
        