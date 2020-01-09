import os
import io
from PIL import Image, ImageOps
from newqc import models
from django.core.files import File
import settings

def main():
    size = 1100, 825
    for b in models.BatchSheet.objects.all():
        l = Image.open(b.large.file)
        thumbnail = File(open('%s/batchsheets_thumbnail/lands_thumb.jpg' % settings.MEDIA_ROOT))
#        l.thumbnail(size, Image.ANTIALIAS)
#        l.save(b.thumbnail.file, "JPEG")
        b.thumbnail.delete()
        b.save()
        
    
if __name__ == "__main__":
    main()
