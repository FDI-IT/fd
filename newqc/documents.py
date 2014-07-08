"""
Bar code documents
"""
import os, errno, logging, cStringIO
import subprocess
import shutil
import zbar
from PIL import Image

from django.core.files import File

from pluggable.hashing import sha_hash
from pluggable.move_no_overwrite import move_no_overwrite

from newqc.models import Retain, RMRetain, Lot, TestCard, RMTestCard, BatchSheet, ScannedDoc, ScannedSymbol
DocumentTypes = (TestCard, RMTestCard, BatchSheet)
type_map = {
    'RETAIN':(Retain, TestCard),
    'RM':(RMRetain, RMTestCard),
    'BATCHSHEET_LOT':(Lot, BatchSheet),
    'SCANNED_DOC':(None, ScannedDoc),
}

# set up logging
LOG_PATH = '/var/log/django/'
LOG_FORMATTER = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
LOG_FILE_HANDLER = logging.FileHandler(LOG_FILENAME)
LOG_FILE_HANDLER.setLevel(logging.INFO)
LOG_FILE_HANDLER.setFormatter(LOG_FORMATTER)

# configure the barcode scanner
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

# configure file destination directories
EXC_DIRECTORY = '/srv/samba/tank/scans/exc/'
COMPLETE_PATH = '/srv/samba/tank/scans/imported_barcode_docs/'
HASH_EXISTS_DIRECTORY = '/srv/samba/tank/scans/hash_exists/'
for MY_DESTINATION_DIR in (EXC_DIRECTORY, COMPLETE_PATH, HASH_EXISTS_DIRECTORY):
    try:
        os.makedirs(MY_DESTINATION_DIR)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
            pass
        else:
            raise
        
def safe_move_to_exc_directory(src):
    move_no_overwrite(src, EXC_DIRECTORY)
    
class NoSymbolTargetException(Exception):
    def __init__(self, *args, **kwargs):
        super(NoSymbolTargetException, self).__init__(*args, **kwargs)

class ImportBCDoc():
    def __init__(self, img_path):
        """Importing a barcode document.
        
        Given a path.

        #. Set up logging
        #. Hash it
        #. Check the hash does not exist
        #. If it does, move the file and return
        #. Barcode Scan it
        #. Check the type and ID of the barcodes
        #. Dispatch the file to that type's processor
        #. Tear down logging
        """
        self.setup_logging()
        
        self.path = img_path
        self.logger.info("Importing %s" % self.path)
        
        try:
            self.hash = sha_hash(img_path)
        except Exception as e:
            """Excepting Exception because not sure what
            kinds of exceptions the sha_hash function can
            raise.
            """
            self.process_error("%s: %s -- Unable to hash %s" % (
                type(e), repr(e), self.path))
            return
        
        if self.hash is None:
            self.process_error("%s has no hash!" % self.path)
            return
            
        if ScannedDoc.objects.filter(image_hash=self.hash).exists():
            self.process_hash_exists()
            return
        
        try:
            self.image = Image.open(self.path)
        except Exception as e:
            self.process_error("%s Unable to Image.open('%s') -- %s" % (
                type(e), self.path, repr(e)))
            return
        
        # this could possibly raise some exceptions that I haven't
        # though of yet -- potentially unsafe section
        self.symbol_list = self.zbar_scan()
        
        try:
            self.bc_type, self.bc_key = self.get_barcode_target()
            ReferredObjectType, DocumentType = type_map[self.bc_type]
        except NoSymbolTargetException as e:
            # the finally block depends on these values
            self.bc_type = None
            self.bc_key = None
            ReferredObjectType = None
            DocumentType = ScannedDoc
        finally:
            self.sd_create_kwargs = self.generate_scanneddoc_kwargs()
           
            self.my_doc = DocumentType.create_from_referred_object_from_bc_key(
                self.bc_key, self.sd_create_kwargs)
            self.my_doc.save()
            self.move_scanned_image()
            # now that my_doc is saved we need to save the associated
            # ScannedSymbol objects that were created earlier
            for s in self.symbol_list:
                s.scanned_doc = self.my_doc
                s.save()
            self.logger.info("Saved %s:%s from %s" % (
                str(DocumentType), self.my_doc.pk, self.path))
            

    def move_scanned_image(self):
        self.dst = move_no_overwrite(self.path, COMPLETE_PATH)
        self.logger.info("Moved scanned file %s to %s" % (
            self.path, self.dst))

    def process_error(self, error_message):
        self.logger.error(error_message)
        self.dst = safe_move_to_exc_directory(self.path)
        self.logger.error("%s moved to $s" % (self.path, self.dst))
        
    def process_no_symbol(self, message):
        self.logger.warn(process_error)

    def process_hash_exists(self):
        my_name, my_extension = os.path.splitext(self.path)
        my_move_name = "%s%s" % (self.hash, my_extension)
        move_path = os.path.join(HASH_EXISTS_DIRECTORY, my_move_name)
        self.dst = move_no_overwrite(self.path, move_path)
        self.logger.warn("Existing hash found, moving %s to %s" % (
            self.path, self.dst))
        
    def setup_logging(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(LOG_FILE_HANDLER)
        self.log_stream = cStringIO.StringIO()
        self.stream_handler = logging.StreamHandler(self.log_stream)
        self.stream_handler.setLevel(logging.INFO)
        self.stream_handler.setFormatter(LOG_FORMATTER)
        self.logger.addHandler(self.stream_handler)
        
    def flush_import_log(self):
        self.stream_handler.flush()
        import_log = self.log_stream.getvalue()
        self.logger.removeHandler(self.stream_handler)
        return import_log

    def generate_scanneddoc_kwargs(self):
        self.thumbnail = self.generate_thumbnail()
        self.large_file = File(open(self.path,'r'))
        self.import_log = self.flush_import_log()
        return {
                'thumbnail':self.thumbnail,
                'image_hash':self.hash,
                'large':self.large_file,
                'import_log':self.import_log,
            }

    def create_generic_document(self):
        sd = ScannedDoc(
                **self.model_instance_create_kwargs
            )
        return sd 
 
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
    
    def zbar_scan(self):
        """Parses all the found symbols and fills symbol_list
        with models.ScannedSymbol
        """
        converted_image = self.image.convert('L')
        width, height = converted_image.size
        raw = converted_image.tostring()
        scanned_image = zbar.Image(width, height, 'Y800', raw)
        scanner.scan(scanned_image)
        
        symbol_list = []
        
        for zbar_symbol in scanned_image.symbols:
            sd = ScannedSymbol(zbar_symbol=zbar_symbol)
            symbol_list.append(sd)
            self.logger.info("Found barcode: %s" % sd)
        
        return symbol_list
        
    def get_barcode_target(self):
        if len(self.symbol_list) == 0:
            message = "No barcodes found"
            self.logger.info(message)
            raise NoSymbolTargetException(message)
        
        for s in self.symbol_list:
            bc_split = s.symbol_data.split('-')
            if len(bc_split) == 2:
                if bc_split[0] in type_map:
                    return bc_split
        
        message = "No target found in symbol list"
        self.logger.info(message)
        return ("SCANNED_DOC", None)
