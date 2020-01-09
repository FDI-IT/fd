# TODO Account for other types of files

import os
import subprocess
import shutil
import hashlib
from tempfile import NamedTemporaryFile
from itertools import chain
import sys, zlib
import glob
import time
import re

from datetime import datetime

from pyexiv2 import ImageMetadata
from pdftools import pdffile
from pyPdf import PdfFileReader
# from PythonMagick import Image

from django.contrib.auth.models import User
from django.core.files import File

from access.models import Flavor, Formula
from docvault import models

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
        print png_name

def process_jbg(jbg_path):
    # get the name for later
    jbg_name = jbg_path.split('/')[-1]
    
    # a copy is made before it's deleted...better that than lose anything
    cache_jbg_path = "/var/www/django/dump/imagecache/%s - %s" % (datetime.now(), jbg_name)
    shutil.copyfile(jbg_path, cache_jbg_path)
    process = subprocess.Popen(['echo'], shell=False)

    # a converted and rotated png on the ram disk
    png_path = ("/tmp/image_ram/%s" % jbg_name).replace('.jbg', '.png')
        
    subprocess_arglist = ['/usr/local/bin/convert', cache_jbg_path, '-rotate', '-90>', png_path]
    process = subprocess.Popen(subprocess_arglist, shell=False)
    process.wait()
    
def process_tmp_pngs(png_path='/tmp/image_ram/'):
    os.chdir(png_path)
    docs = {}
    user = User.objects.get(username='stachurski')
    for png_path in glob.glob('*.png'):
        png_id = png_path.split('-')[0]
        if png_id in docs:
            my_doc = docs[png_id]
        else:
            my_doc = models.Doc(user=user,mailbox=20)
            my_doc.save()
            docs[png_id] = my_doc
        f = File(open(png_path,'rb'))
        p = models.Page(doc=my_doc)
        p.image.save(png_path, f)
    
#    
#        f = File(t)
#                        p = models.Page(doc=doc)
#                        p.image.save(t.name, f)

# def process_batch(input_path, output_path):
#     os.chdir(input_path)
#     for pdf_path in glob.glob('*.pdf'):
#         print pdf_path
#         pypdf = PdfFileReader(file(pdf_path, 'rb'))
#         for x in range(pypdf.getNumPages()-1):
#             i = Image('%s[%s]' % (pdf_path, x))
#             i.write('%s/%s-%s.png' % (output_path, pdf_path, x))
            
def input_batch(input_path):
    os.chdir(input_path)
    user = User.objects.get(username='stachurski')
    for pdf_path in glob.glob('*.pdf'):
        print pdf_path
        convert_pdf(pdf_path)

        
def process_pdf(pdf_path):
    pypdf = PdfFileReader(file(pdf_path, 'rb'))    
    num_pages = pypdf.getNumPages()
    print num_pages
    
    
def barcode_scan(img_path):

    # the actualy bar code analaysis off the ram disk
    process = subprocess.Popen(
        ['/usr/bin/zbarimg', img_path], 
        shell=False, 
        stdout=subprocess.PIPE)
    process.wait()
    # just in case you need to convert to a cropped selection, increase
    # zbarimg success rated
    # convert /var/www/django/dump/scanbatch/image\(6\).png -crop 1100x1100+400+400 crop.png
    #
    # parsing the results
    scan_value = process.communicate()[0]
    return scan_value

def parse_scan_for_retain_pk(scan_value):
    retain_pk = scan_value.split(':')[1].split('-')[1]

    return retain_pk

#    for x in range(pypdf.getNumPages()-1):
#        i = Image('%s[%s]' % (pdf_path,x))
#        t = NamedTemporaryFile()
#        i.magick('PNG')
#        i.write(t.name)
#        f = File(t)
#        p = models.Page(doc=doc)
#        p.image.save(t.name, f)
#        #p.save()

# def convert_pdf(path, user=User.objects.get(username='stachurski')):
#     doc = models.Doc(user=user)
#     doc.save()
#     try:
#         document = pdffile.PDFDocument(path)
#         for i in range(document.count_pages()):
#             page = document.read_page(i + 1)
#             counter = 0
#             resources = document._dereference(page.page_dict["Resources"])
#             if not resources.has_key("XObject"):
#                 continue
#
#             for xobject in resources["XObject"].values():
#
#                 xdict, stream = document._dereference(xobject)
#
#                 try:
#                     if xdict["Subtype"].name != "Image":
#                         continue
#
#                     if xdict["Filter"].name == "DCTDecode":
#
#                         data = document.file[stream.start:stream.end]
#                         t = NamedTemporaryFile()
#                         t.file.write(data)
#                         md = ImageMetadata(t.name)
#                         md.read()
#                         md['Exif.Image.Orientation']=6
#                         md.write()
#                         f = File(t)
#                         p = models.Page(doc=doc)
#                         p.image.save(t.name, f)
#
#                     elif xdict["Filter"].name == "FlateDecode":
#
#                         if isinstance(xdict["ColorSpace"], pdffile.name) and \
#                             xdict["ColorSpace"].name == "DeviceRGB":
#
#                             data = zlib.decompress(document.file[stream.start:stream.end])
#                             image = Image.fromstring(
#                                 "RGB", (xdict["Width"], xdict["Height"]), data
#                                 )
#                             t = NamedTemporaryFile()
#                             image.save(t.name)
#                             md = ImageMetadata(t.name)
#                             md.read()
#                             md['Exif.Image.Orientation']=6
#                             md.write()
#                             f = File(t)
#                             p.models.Page(doc=doc)
#                             p.image.save(t.name,f)
#
#                     else:
#                         continue
#
#                     counter += 1
#
#                 except (KeyError, IOError):
#                     continue
#
#     except pdffile.PDFError:
#         sys.stderr.write("Failed to read the PDF file: %s\n" % path)
#         raise

# The following doesn't work with the new design, but the process is 
# the same. Get a jbg file, hash it, make a test card and delete the jbg.
#
#def scan_card():
#    card_file = get_card_file('/var/www/django/dump/scanbatch/')
#    
#    if card_file:
#        jbg_file = open(card_file, 'r')
#        sha = hashlib.sha256()
#        for chunk in iter(lambda: jbg_file.read(8192),''):
#            sha.update(chunk)
#        hash = sha.hexdigest()
#        if models.TestCard.objects.filter(image_hash=hash).count() == 0:
#            tc = process_jbg(card_file, hash)
#            return tc
#        else:
#            os.remove(card_file)
#    else:
#        pass
#    return False
