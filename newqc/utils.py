# TODO Account for other types of files

import os
import subprocess
import shutil
import hashlib
from itertools import chain

import glob
import time
import re

from datetime import datetime, date

from django.core.files import File

from access.models import Flavor, Formula, Ingredient
from newqc import models

class CurlOutput:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents += buf

def get_card_file(search_path):
    try:
        return glob.glob('%s*.jbg' % search_path)[0]
    except IndexError:
        return False 

def process_jbg(jbg_path):
    # get the name for later
    jbg_name = jbg_path.split('/')[-1]
    
    # a copy is made before it's deleted...better that than lose anything
    cache_jbg_path = "/usr/local/django/dump/imagecache/%s - %s" % (datetime.now(), jbg_name)
    shutil.copyfile(jbg_path, cache_jbg_path)
    process = subprocess.Popen(['echo'], shell=False)

    # a converted and rotated png on the ram disk
    png_path = ("/tmp/image_ram/%s" % jbg_name).replace('.jbg', '.png')
        
    subprocess_arglist = ['/usr/local/bin/convert', cache_jbg_path, '-rotate', '-90>', png_path]
    process = subprocess.Popen(subprocess_arglist, shell=False)
    process.wait()

    # the actualy bar code analaysis off the ram disk
    process = subprocess.Popen(
        ['/usr/bin/zbarimg', png_path], 
        shell=False, 
        stdout=subprocess.PIPE)
    process.wait()
    # just in case you need to convert to a cropped selection, increase
    # zbarimg success rated
    # convert /usr/local/django/dump/scanbatch/image\(6\).png -crop 1100x1100+400+400 crop.png
    #
    # parsing the results
    scan_value = process.communicate()[0]
    retain_pk = scan_value.split(':')[1].split('-')[1]
    
    tc = models.TestCard(
        retain=models.Retain.objects.get(pk=retain_pk), 
        large=File(open(png_path, 'r')),
        image_hash=hash)
    tc.save()
  
    os.remove(png_path)
    os.remove(tmp_jbg_path)
    
    return tc

def scan_card():
    card_file = get_card_file('/usr/local/django/dump/scanbatch/')
    
    if card_file:
        jbg_file = open(card_file, 'r')
        sha = hashlib.sha256()
        for chunk in iter(lambda: jbg_file.read(8192),''):
            sha.update(chunk)
        hash = sha.hexdigest()
        if models.TestCard.objects.filter(image_hash=hash).count() == 0:
            tc = process_jbg(card_file, hash)
            return tc
        else:
            os.remove(card_file)
    else:
        pass
    return False

def get_lcrs():
    lcrs = {}
    last_chance_year = date.today().year-3
    last_chance_retains = models.Retain.objects.filter(date__year=last_chance_year).filter(status="Passed").select_related()
    for r in last_chance_retains:
        print r
        f = r.lot.flavor
        if f in lcrs:
            continue
        retain_list = f.combed_sorted_retain_superset()
        if r == retain_list[0]:
            lcrs[f] = r
    return lcrs
        
