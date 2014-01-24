import os
import subprocess
import hashlib
import shutil
import fnmatch
import cStringIO
from PIL import Image

from django.core.files import File

from newqc.models import *

from celery.task import task, Task

def my_hash(my_file):
    sha = hashlib.sha256()
    for chunk in iter(lambda: my_file.read(8192),''):
        sha.update(chunk)
    my_file.seek(0)
    return sha.hexdigest()

type_map = {
    'RETAIN':(Retain, TestCard),
    'RM':(RMRetain, RMTestCard),
    'BATCHSHEET_LOT':(Lot, BatchSheet),
}

exc_directory = '/srv/samba/tank/scans/exc/'

def move_exc_image(full_file_path):
    shutil.move(full_file_path, exc_directory)

@task()
def walk_scans_qccards(walk_paths=['/srv/samba/tank/scans/qccards',]):
    returns = []
    if not os.path.exists(exc_directory):
        os.makedirs(exc_directory)
    for wp in walk_paths:
        for root, dirnames, filenames in os.walk(wp):
            for filename in fnmatch.filter(filenames, '*.jpg'):
                full_file_path = os.path.join(root,filename)
                print full_file_path
                try:
                    returns.append(ImportBCDoc(full_file_path))
                except:
                    move_exc_image(full_file_path)
    return returns

class ImportBCDoc():
    def exists_hash(self):
        for TestCardType in (TestCard, RMTestCard, GenericTestCard, BatchSheet):
            possible_tcs = TestCardType.objects.filter(image_hash=self.hash)
            if possible_tcs.count() > 0:
                self.tc=possible_tcs[0]
                return True
        return False
    
    def __init__(self, img_path):
        # open the file
        self.path = img_path
        f = open(self.path,'r')
        
        #get the hash
        sha = hashlib.sha256()
        for chunk in iter(lambda: f.read(8192),''):
            sha.update(chunk)
        self.hash = sha.hexdigest()
        
        if self.exists_hash():
            return
        
        thumbnail = self.generate_thumbnail()
        
        # get the return code of zbarimg, and the value
        bc_returncode, bc_value = self.scan_for_barcode()
        if bc_returncode != 0:
            self.tc = GenericTestCard(
                image_hash=self.hash,
                large=File(open(self.path,'r')),
                thumbnail=thumbnail,
            )
            self.tc.save()
            return
    
        doc_key_type, doc_key = bc_value.split('-')
            
        # TODO this craps out when it can't split. why can't it split?
        
        # get the django ORM types from the type_map
        RetainType, TestCardType = type_map[doc_key_type]
        
        # try to get corresponding Retain
        if RetainType == Lot:
            try:
                lot = Lot.objects.get(number=doc_key)
            except:
                lot = None
            self.tc = BatchSheet(
                lot=lot,
                large=File(open(self.path,'r')),
                image_hash=self.hash,
                thumbnail=thumbnail,
            )
            self.tc.save()
        else:
            try:
                retain=RetainType.objects.get(pk=doc_key)
            except:
                retain=None
                
            
            # create testcard
            self.tc = TestCardType(
                retain=retain,
                large=File(open(self.path,'r')),
                image_hash=self.hash,
                thumbnail=thumbnail,
            )
            self.tc.save()
        
    def generate_thumbnail(self):
        large = Image.open(self.path,)
        width, height = large.size
        if width > height:
            tn = large.resize((490,380), Image.ANTIALIAS)
        else:
            tn = large.resize((380,490), Image.ANTIALIAS)
        tn_path = '/tmp/%s-tn.png' % os.path.splitext(os.path.basename(self.path))[0]
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