"""
Bar code documents
"""
import os, errno, logging, cStringIO
import subprocess
import shutil
import zbar
from PIL import Image

from django.core.files import File

from pluggable.hashing import sha_hash as my_hash
from pluggable.move_no_overwrite import move_no_overwrite

from newqc.models import Retain, RMRetain, Lot, TestCard, RMTestCard, BatchSheet, ScannedDoc, ScannedSymbol
DocumentTypes = (TestCard, RMTestCard, BatchSheet)
type_map = {
    'RETAIN':(Retain, TestCard),
    'RM':(RMRetain, RMTestCard),
    'BATCHSHEET_LOT':(Lot, BatchSheet),
}

# set up logging
LOG_PATH = '/var/log/django/'
LOG_FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
try:
    os.makedirs(LOG_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LOG_PATH):
        pass
    else:
        raise
LOG_FILENAME = '/var/log/django/scan_docs.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO, formatter=LOG_FORMATTER)

# configure the barcode scanner
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

# configure file destination directories
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
        
def safe_move_to_exc_directory(src):
    move_no_overwrite(src, EXC_DIRECTORY)

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
        
        try:
            self.hash = sha_hash(img_path)
        except Exception as e:
            """Excepting Exception because not sure what
            kinds of exceptions the sha_hash function can
            raise.
            """
            self.process_error("%s has no hash!" % self.path)
            return
        
        if self.hash is None:
            self.process_error("%s: %s -- Unable to hash %s" % (type(e), repr(e), self.path))
            return
        
        if ScannedDoc.objects.filter(image_hash=self.hash).exists():
            self.process_hash_exists()
            return
        
        try:
            self.image = Image.open(self.path)
        except Exception as e:
            self.process_error("%s Unable to Image.open('%s') -- %s" % (type(e), self.path, repr(e)))
            return

        self.generate_scanneddoc_kwargs()
        
        self.zbar_scan()
        
        self.doc_type_str, self.bc_key = bc_value
        # get the django ORM types from the type_map
        ReferredObjectType, DocumentType = type_map[self.doc_type_str]
        # we need this method specifically because the name of the 
        # referred object attribute is not standard between the 
        # document type classes (retain, rmretain, lot, etc)
        self.sd = DocumentType.create_from_referred_object_from_bc_key(self.bc_key, self.model_instance_create_kwargs)
        self.sd.save()
        self.logger.info("Saved a %s:%s from %s" % (str(DocumentType), self.sd.pk, self.path))
        self.move_scanned_image()
        
    def move_scanned_image(self):
        my_name, my_extension = os.path.splitext(self.path)
        my_move_name = "%s%s" % (self.hash, my_extension)
        move_complete_path = os.path.join(COMPLETE_PATH, my_move_name)
        shutil.move(self.path, move_complete_path)
        self.logger.info("Moved scanned file %s to %s" % (self.path, move_complete_path))

    def process_error(self, error_message):
        self.logger.error(error_message)
        safe_move_to_exc_directory(self.path)

    def process_hash_exists(self):
        my_name, my_extension = os.path.splitext(self.path)
        my_move_name = "%s%s" % (self.hash, my_extension)
        move_path = os.path.join(HASH_EXISTS_DIRECTORY, my_move_name)
        move_no_overwrite(self.path, move_path)
        self.logger.warn("Existing hash found, moving %s to %s" % (self.path, move_path))
        
    def setup_logging(self):
        self.logger = logging.getLogger()
        self.log_stream = cStringIO.StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        self.log_handler.setLevel(logging.INFO)
        self.log_handler.setFormatter(LOG_FORMATTER)
        self.logger.addHandler(self.log_handler)
        
    @property            
    def flush_import_log(self):
        self.log_handler.flush()
        import_log = self.log_stream.getvalue()
        self.logger.removeHandler(self.log_handler)
        return import_log

    def generate_scanneddoc_kwargs(self):
        self.thumbnail = self.generate_thumbnail()
        self.large_file = File(open(self.path,'r'))
        self.sd_create_kwargs = {
                'thumbnail':self.thumbnail,
                'image_hash':self.hash,
                'large':self.large_file,
            }

             
    def save_as_generic_document(self):
        self.sd = ScannedDoc(
                **self.model_instance_create_kwargs
            )
        self.sd.save()
        self.logger.info("Saved a generic ScannedDoc:%s from %s" % (self.sd.pk, self.path))

    def generate_thumbnail(self):
        width, height = self.image.size
        if self.width > self.height:
            tn = self.image.resize((490,380), Image.ANTIALIAS)
        else:
            tn = self.image.resize((380,49ass ScannedDoc(models.Model):
    related_object_name = None
    
    image_hash = models.CharField(max_length=64, blank=True)
    large = models.ImageField(upload_to='scanned_doc_large')
    thumbnail = models.ImageField(upload_to='scanned_doc_thumbnail')
    notes = models.TextField(blank=True, default="")
    scan_time = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    import_log = models.TextField(blank=True,default="")
    
    class Meta:
        ordering = ['-id']
        
    @property0), Image.ANTIALIAS)
        tn_path = os.path.join(
                '/tmp',
                '%s-tn.png' % self.hash)
        tn.save(tn_path)
        thumbnail_file = File(open(tn_path,'r'))
        return thumbnail_file
    
    def zbar_scan(self):
        # get the return code of zbarimg, and the value
        # the value, if valid, is a two tuple, doc_type_str and bc_key
        bc_returncode, bc_value = self.scan_for_barcode()
        # self.logger.info("BC Return %s | BC Value %s | for %s" % (bc_returncode, bc_value, self.path))

        # if bc_returncode != 0 it means 
        # something went wrong scanning, but not making a thumbnail
        # we save this as a generic doc type for later analysis
        if bc_returncode != 0:
            self.save_as_generic_document()
            return
        
    def scan_for_barcode(self):
        converted_image = self.image.convert('L')
        width, height = converted_image.size
        raw = converted_image.tostring()
        scanned_image = zbar.Image(width, height, 'Y800', raw)
        scanner.scan(scanned_image)
        
        self.symbol_list = []
        
        for zbar_symbol in scanned_image.symbols:
            scanned_symbol = ScannedSymbol()
            scanned_symbol.parse_zbar_symbol(zbar_symbol)
            self.symbol_list.append(scanned_symbol)
        
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
