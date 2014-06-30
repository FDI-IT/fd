"""
Bar code documents
"""
import os, errno, logging
import subprocess
import shutil
import hashlib
import zbar
from PIL import Image

from django.core.files import File

"""we should try to get this out of this file. 
documents shouldn't depend on models.
it should be the other way around.
"""
from newqc.models import Retain, RMRetain, Lot, TestCard, RMTestCard, BatchSheet, ScannedDoc
DocumentTypes = (TestCard, RMTestCard, BatchSheet)
type_map = {
    'RETAIN':(Retain, TestCard),
    'RM':(RMRetain, RMTestCard),
    'BATCHSHEET_LOT':(Lot, BatchSheet),
}

# set up logging
LOG_PATH = '/var/log/django/'
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
logger = logging.getLogger()

scanner = zbar.ImageScanner()
# configure the reader
scanner.parse_config('enable')


def my_hash(my_path):
    with open(my_path,'r') as my_file:
        sha = hashlib.sha256()
        for chunk in iter(lambda: my_file.read(8192),''):
            sha.update(chunk)
        return sha.hexdigest()
    return None

EXC_DIRECTORY = '/srv/samba/tank/scans/exc/'
COMPLETE_PATH = '/srv/samba/tank/scans/imported_barcode_docs/'
for MY_DESTINATION_DIR in (EXC_DIRECTORY, COMPLETE_PATH):
    try:
        os.makedirs(MY_DESTINATION_DIR)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
            pass
        else:
            raise

class ImportBCDoc():
       
    def __init__(self, img_path):
        """Importing a barcode document.
        
        Given a path.

        #. Hash it
        #. Check the hash does not exist
        #. If it does, move the file and return
        #. Barcode Scan it
        #. Check the type and ID of the barcodes
        #. Dispatch the file to that type's processor
        """
        self.path = img_path
        self.hash = my_hash(img_path)
        
        if self.hash is None:
            # Not sure what to do if the file cannot be hashed.
            logger.warn("%s has no hash!" % self.path)
            return
        
        # this should do something like,
        # remove if hash exists and is verified in the database
        if ScannedDoc.objects.filter(image_hash=self.hash).exists():
            return
        
        try:
            self.image = Image.open(self.path)
        except IOError as e:
            logger.error("IOError: Unable to Image.open('%s') -- %s" % (self.path, repr(e)))

        # get the return code of zbarimg, and the value
        # the value, if valid, is a two tuple, doc_type_str and bc_key
        bc_returncode, bc_value = self.scan_for_barcode()
        logger.info("BC Return %s | BC Value %s | for %s" % (bc_returncode, bc_value, self.path))

        # if bc_returncode != 0 it means 
        # something went wrong scanning, but not making a thumbnail
        # we save this as a generic doc type for later analysis
        if bc_returncode != 0:
            self.save_as_generic_document()
            return
        
        self.doc_type_str, self.bc_key = bc_value
        # get the django ORM types from the type_map
        ReferredObjectType, DocumentType = type_map[self.doc_type_str]
        # we need this method specifically because the name of the 
        # referred object attribute is not standard between the 
        # document type classes (retain, rmretain, lot, etc)
        self.sd = DocumentType.create_from_referred_object_from_bc_key(self.bc_key, self.model_instance_create_kwargs)
        self.sd.save()
        logger.info("Saved a %s:%s from %s" % (str(DocumentType), self.sd.pk, self.path))
        self.move_scanned_image()
    
    def move_scanned_image(self):
        my_name, my_extension = os.path.splitext(self.path)
        my_move_name = "%s%s" % (self.hash, my_extension)
        move_complete_path = os.path.join(COMPLETE_PATH, my_move_name)
        shutil.move(self.path, move_complete_path)
        logger.info("Moved scanned file %s to %s" % (self.path, move_complete_path))

    def process_hash_exists(self):
        my_name, my_extension = os.path.splitext(self.path)
        my_move_name = "%s%s" % (self.hash, my_extension)
        self.move_path = os.path.join(HASH_EXISTS_DIRECTORY, my_move_name)
        shutil.move(self.path, self.move_path)
        logger.warn("Existing hash found, moving %s to %s" % (self.path, self.move_path))
    
    @property
    def model_instance_create_kwargs(self):
        return {
                'thumbnail':self.generate_thumbnail(),
                'image_hash':self.hash,
                'large':File(open(self.path,'r')),
            }
             
    def save_as_generic_document(self):
        self.sd = ScannedDoc(
                **self.model_instance_create_kwargs
            )
        self.sd.save()
        logger.info("Saved a generic ScannedDoc:%s from %s" % (self.sd.pk, self.path))

    def generate_thumbnail(self):
        width, height = self.image.size
        if width > height:
            tn = self.image.resize((490,380), Image.ANTIALIAS)
        else:
            tn = self.image.resize((380,490), Image.ANTIALIAS)
        tn_path = os.path.join(
                '/tmp',
                '%s-tn.png' % self.hash)
        tn.save(tn_path)
        thumbnail_file = File(open(tn_path,'r'))
        return thumbnail_file
        
    def scan_for_barcode(self):
        converted_image = self.image.convert('L')
        width, height = converted_image.size
        raw = converted_image.tostring()
        scanned_image = zbar.Image(width, height, 'Y800', raw)
        scanner.scan(scanned_image)
        
        symbols = list(scanned_image.symbols)
        
        if len(symbols) != 1:
            return (1, "")
        
        s = symbols[0]
        
        # try to split bc on -, if that does not yield 2 parts
        # we save this as a generic doc type for later analysis
        bc_split = s.data.split('-')
        if len(bc_split) != 2:
            return (1, s.data)
        
        return (0, bc_split)
