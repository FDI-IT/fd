import os
import re
import subprocess
import shutil
import hashlib
import pycurl
import time

from datetime import datetime

from newqc.models import TestCard, Retain
from newqc.utils import CurlOutput

from celery.task import task, Task

@task()
def process_jbg(jbg_path):
    logger = CurlPrinter.get_logger(logfile='curlprinter.log')
    logger.info("Processing %s" % jbg_path)
    sha = hashlib.sha256()
    jbg_file = open(jbg_path, 'r')
    for chunk in iter(lambda: jbg_file.read(8192),''):
        sha.update(chunk)
    hash = sha.hexdigest()
    if TestCard.objects.filter(image_hash=hash).count() != 0:
        raise # the image hash already exists in the database
    
    # get the name for later
    jbg_name = jbg_path.split('/')[-1]
    
    # a copy is made before it's deleted...better that than lose anything
    cache_jbg_path = "/var/www/django/dump/imagecache/%s - %s" % (datetime.now(), jbg_name)
    shutil.copyfile(jbg_path, cache_jbg_path)
    
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
    # convert /var/www/django/dump/scanbatch/image\(6\).png -crop 1100x1100+400+400 crop.png
    #
    # parsing the results
    scan_value = process.communicate()[0]
    retain_pk = scan_value.split(':')[1].split('-')[1]
    
    tc = TestCard(
        retain=Retain.objects.get(pk=retain_pk), 
        large=File(open(png_path, 'r')),
        image_hash=hash)
    tc.save()
  
    os.remove(png_path)
    logger.info("About to return")
    return tc


class CurlPrinter(Task):
    max_retries=2
    
    def run(self):
        logger = self.get_logger(logfile='curlprinter.log')
    
        logger.info("Setting up CURL")
        c = pycurl.Curl()
        c.setopt(pycurl.CONNECTTIMEOUT, 3) 
        c.setopt(c.COOKIEJAR, 'cookie.txt')
        coutput = CurlOutput()
        c.setopt(c.WRITEFUNCTION, coutput.body_callback)
        try:
            logger.info("Contacting printer")
            c.setopt(c.URL, "http://192.168.10.200/")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/frame.cgi?PageFlag=b_frame.tpl&Dummy=1")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/box_index.cgi?PageFlag=b_ix30.tpl&Dummy=2")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/en/pages/b_ubody.htm?Dummy=3")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/bpbl.cgi?BoxKind=UserBox&Dummy=4")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=12&Cookie=&Dummy=5")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/blogin.cgi?BOX_No=12&Cookie=&Dummy=6")
            c.perform()
            c.setopt(c.URL, "http://192.168.10.200/bheader.cgi?BOX_No=12&Dummy=7")
            c.perform()
            coutput.contents = ""
            c.setopt(c.URL, "http://192.168.10.200/bdocs.cgi?BOX_No=12&DocStart=1&DIDS=&Dummy=8")
            c.perform()
        except Exception as e:
            logger.warning("Unable to contact printer. Retrying...")
            self.retry(exc=e)
        
        logger.info("Parsing Doc IDs")
        doc_re = "javascript:doc_pages\('(\d+)'\)"
        try:
            doc_id = re.search(doc_re, coutput.contents).group(1)
        except:
            logger.error("Unable to parse document ID with doc_re")
            raise
        
        logger.info("Doc ID found: %s" % doc_id)
        
        
        coutput.contents = ""
        c.setopt(c.URL, "http://192.168.10.200/bpages.cgi?BOX_No=12&DocID=%s&PgStart=1&PIDS=&Dummy=9" % doc_id)
        c.perform()
        dummy = 10 
        matchcount = coutput.contents.count('dot_blue')
        matchcount = matchcount / 2
        logger.info("Number of pages found: %s" % matchcount)
        
        for x in range(1,matchcount+1):
            coutput.contents = ""
            c.setopt(c.URL, "http://192.168.10.200/image.jbg?B=12&D=%s&P=%s&M=MV&RX=600&RY=600&Dummy=%s" % (doc_id, x, dummy))
            dummy += 1
            save_path = '/tmp/image_ram/%s.jbg' % x
            new_image = open(save_path, 'w')
            c.perform()
            logger.info("Writing page #%s" % x)
            new_image.write(coutput.contents)
            new_image.close()
            process_jbg.delay(jbg_path=save_path)
            # i think a new task should be fired to convert the image that's just
            # written here.
    
        # this would be where the delete request would go
        # confirm it.
        
        #client side loop checks the result of this task.
        
        c.close()
        return