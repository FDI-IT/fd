"""
Bar code documents
"""
import os
import subprocess
import shutil
import hashlib
from PIL import Image

from django.core.files import File

"""we should try to get this out of this file. 
documents shouldn't depend on models.
it should be the other way around.
"""
from newqc.models import Retain, RMRetain, Lot, TestCard, RMTestCard, BatchSheet, GenericTestCard
DocumentTypes = (TestCard, RMTestCard, GenericTestCard, BatchSheet)
type_map = {
    'RETAIN':(Retain, TestCard),
    'RM':(RMRetain, RMTestCard),
    'BATCHSHEET_LOT':(Lot, BatchSheet),
}

def my_hash(my_path):
    with open(my_path,'r') as my_file:
        sha = hashlib.sha256()
        for chunk in iter(lambda: my_file.read(8192),''):
            sha.update(chunk)
        return sha.hexdigest()
    return None

exc_directory = '/srv/samba/tank/scans/exc/'
hash_exists_directory = '/srv/samba/tank/scans/old/'

# move will silently overwrite the destination, 
# so we should rename the file to the hash 
# so no different files overwrite each other
def move_exc_image(full_file_path):
    shutil.move(full_file_path, exc_directory)
    
def move_old_image(full_file_path):
    shutil.move(full_file_path, hash_exists_directory)

class ImportBCDoc():
       
    def __init__(self, img_path):
        """Importing a barcode document.
        
        Given a path.
        
        #. Open it
        #. Hash it
        #. Check the hash does not exist
        #. Barcode Scan it
        #. Check the type and ID of the barcodes
        #. Dispatch the file to that type's processor
        """
        self.path = img_path
        self.hash = my_hash(img_path)
        
        if self.hash is None:
            # Not sure what to do if the file cannot be hashed.
            return
        
        # this should do something like,
        # remove if hash exists and is verified in the database
        self.hash_uniqueness = True
        for DocumentType in DocumentTypes:
            if DocumentType.objects.filter(image_hash=self.hash).exists():
                self.hash_uniqueness = False
                
        if not self.hash_uniqueness:
            self.move_path = os.path.join(hash_exists_directory, self.hash)
            shutil.move(self.path, self.move_path)
            # TODO: there should be a way to log this from tasks
            # maybe by inspecting the returned object from within tasks
            return
        
        # get the return code of zbarimg, and the value
        bc_returncode, bc_value = self.scan_for_barcode()
        
        # this dict is required to create any type of document, even generic
        document_create_kwargs = self.get_document_create_kwargs()
        
        # if bc_returncode != 0 it means 
        # something went wrong scanning, but not making a thumbnail
        # we save this as a generic doc type for later analysis
        if bc_returncode != 0:
            self.save_as_generic_document(document_create_kwargs)
            return
    
        # try to split bc on -, if that does not yield 2 parts
        # we save this as a generic doc type for later analysis
        bc_split = bc_value.split('-')
        if len(bc_split) != 2:
            self.save_as_generic_document(document_create_kwargs)
            return
            
        self.doc_type_str, self.bc_key = bc_split
        
        # get the django ORM types from the type_map
        ReferredObjectType, DocumentType = type_map[self.doc_type_str]
        # we need this method specifically because the name of the 
        # referred object attribute is not standard between the 
        # document type classes (retain, rmretain, lot, etc)
        self.document = DocumentType.create_from_referred_object_from_bc_key(self.bc_key)
        
        self.document.save()

    def get_document_create_kwargs(self):
        return {
                'thumbnail':self.generate_thumbnail(),
                'image_hash':self.hash,
                'large':File(open(self.path,'r')),
            }
            
    def save_as_generic_document(self, document_create_kwargs):
        self.tc = GenericTestCard(
                **document_create_kwargs
            )
        self.tc.save()
        return

    def generate_thumbnail(self):
        large = Image.open(self.path,)
        width, height = large.size
        if width > height:
            tn = large.resize((490,380), Image.ANTIALIAS)
        else:
            tn = large.resize((380,490), Image.ANTIALIAS)
        tn_path = os.path.join(
                '/tmp',
                '%s-tn.png' % self.hash)
        tn.save(tn_path)
        thumbnail_file = File(open(tn_path,'r'))
        return thumbnail_file
        
    #@task()
    def scan_for_barcode(self):
        process = subprocess.Popen(
            [
                '/usr/bin/zbarimg',
                '-q', 
                '-Sean13.disable',
                '-Sean8.disable',
                '-Si25.disable',
                '-Scode39.disable',
                '-Scode128.disable',
                self.path,
            ], 
            shell=False, 
            stdout=subprocess.PIPE)
        process.wait()
        if process.returncode != 0:
            hash_path = '/tmp/%s.jpg' % self.hash
            process = subprocess.Popen(
                [
                    '/usr/bin/convert',
                    '-quiet',
                    '-blur',
                    '2',
                    '-black-threshold',
                    '70%',
                    self.path,
                    hash_path,
                ],
            )
            process.wait()
            process = subprocess.Popen(
            [
                '/usr/bin/zbarimg',
                '-q', 
                '-Sean13.disable',
                '-Sean8.disable',
                '-Si25.disable',
                '-Scode39.disable',
                '-Scode128.disable',
                hash_path
            ], 
            shell=False, 
            stdout=subprocess.PIPE)
            process.wait()
            if process.returncode != 0:
                return (process.returncode, process.communicate()[0])
            # TODO
            # Error handling code here
            #  -crop 500x500+1950x500
            # -blur 2
            # -black-threshold 70%
        try:
            scan_value_raw = process.communicate()[0]
            scan_value = scan_value_raw.split(':')[1]
            return (0, scan_value)
        except Exception as e:
            return (0, process.communicate()[0])
