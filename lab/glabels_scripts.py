from datetime import date
import os,errno
import tempfile, shlex, subprocess, codecs
import csv
from decimal import Decimal

# from PythonMagick import Image

from django.shortcuts import get_object_or_404

from access.models import Ingredient, Flavor, ExperimentalLog

from pluggable.unicode_to_ascii import unicode_to_ascii

hundredths = Decimal('0.00')

LABEL_PATH = "/var/www/django/dump/labels/"
try:
    os.makedirs(LABEL_PATH)
except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(LABEL_PATH):
        pass
    else:
        raise

def label_data_to_csv(label_data):
    ascii_data = []
    for element in label_data:
        u = unicode_to_ascii(element)
        if u == "":
            u = "-"
        ascii_data.append(u)
        
    input_file = codecs.open("/var/www/django/dump/labels/label.csv", 'w', 'utf-8')
    input_csv = csv.writer(input_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
    
    input_csv.writerow(ascii_data)
    input_file.close()

def solution_print():
    command_line = "lpr -d QL-570 /var/www/django/dump/labels/label.pdf"
    args = shlex.split(command_line)
    p = subprocess.Popen(args).wait()
    return True

# def solution_preview(pdf_file):
#     preview_file = '/var/www/django/preview.png'
#
#     i = Image(pdf_file)
#     i.rotate(90)
#     i.write(preview_file)

def rm_sample_label(receiving_log):
    template_path = '/var/www/django/fd/lab/rm_sample.glabels'
    label_data = []
    label_data.append("%s" % (receiving_log.r_number))
    label_data.append("%s" % (receiving_log.pin))
    label_data.append("%s" % (receiving_log.description))
    label_data.append("%s" % (receiving_log.supplier))
    label_data.append("%s" % (receiving_log.lot))
    label_data.append("%s" % (receiving_log.date))
    label_data_to_csv(label_data)
    output_file = "/var/www/django/dump/labels/label.pdf"
    command_line = "glabels-3-batch -o %s -i %s %s" % (output_file,
                                                     "/var/www/django/dump/labels/label.csv",
                                                     template_path)
    args = shlex.split(command_line)
    p = subprocess.Popen(args).wait()
    solution_preview(output_file)
    return output_file

def solution_label(request):
    # create tempfile with the csv values set from values array
    # compose command line using template_path and tempfile
    # return path of output file
    
    template_path = '/var/www/django/fd/lab/solution_continuous.glabels'
    label_data = []
    label_data.append(request.GET['pin'])
    label_data.append(request.GET['nat_art'])
    label_data.append(request.GET['pf'])
    label_data.append(request.GET['product_name'])
    label_data.append(request.GET['product_name_two'])
    label_data.append(request.GET['concentration'])
    label_data.append(request.GET['solvent'])
    label_data.append(date.today().isoformat(),)
    
    label_data_to_csv(label_data)
    
    output_file = "/var/www/django/dump/labels/label.pdf"
    
    command_line = "glabels-3-batch -o %s -i %s %s" % (output_file,
                                                     "/var/www/django/dump/labels/label.csv",
                                                     template_path)
    args = shlex.split(command_line)
    p = subprocess.Popen(args).wait()
    solution_preview(output_file)
    return output_file



def rm_label(number):
    # create tempfile with the csv values set from values array
    # compose command line using template_path and tempfile
    # return path of output file
    rm = Ingredient.get_obj_from_softkey(number)
    template_path = '/var/www/django/fd/lab/rm_product_continuous.glabels'
    label_data = []
    label_data.append("%s" % rm.id)
    label_data.append("%s" % (rm.short_prefixed_name))
    label_data.append("%s" % rm.short_remainder_name)
    label_data.append("$%s" % rm.unitprice.quantize(hundredths))
    label_data.append("%s" % rm.purchase_price_update.date().strftime('%b %y'))
    label_data.append("%s" % ", ".join(rm.supplier_list))
    label_data.append("%s" % rm.art_nati)
    label_data.append("%s" % rm.cas)
    label_data.append("%s" % rm.fema)
    label_data.append("%s" % rm.kosher)
    label_data.append("%s" % rm.sulfites_ppm)
    label_data.append("%s" % rm.prop65)
    label_data.append("%s" % rm.allergen)

    
    label_data_to_csv(label_data)
    
    output_file = "/var/www/django/dump/labels/label.pdf"
    
    command_line = "glabels-3-batch -o %s -i %s %s" % (output_file,
                                                    "/var/www/django/dump/labels/label.csv",
                                                     template_path)
    args = shlex.split(command_line)
    p = subprocess.Popen(args).wait()
    
    solution_preview(output_file)
    return output_file

def finished_product_label(number):
    # create tempfile with the csv values set from values array
    # compose command line using template_path and tempfile
    # return path of output file
    flavor = Flavor.objects.get(number=number)
    
    template_path = '/var/www/django/fd/lab/finished_product_continuous.glabels'
    label_data = []
    label_data.append("%s" % flavor.pinnumber)
    label_data.append("%s-%s" % (flavor.prefix, flavor.number))
    label_data.append("%s %s" % (flavor.natart, flavor.name))
    label_data.append(flavor.label_type)
    label_data.append(flavor.solvent)
    label_data.append("%s" % date.today())
    label_data.append("$%s" % flavor.rawmaterialcost.quantize(hundredths))
    label_data.append("%s" % flavor.lastspdate.date().strftime('%b %y'))
    label_data.append("%s" % flavor.flashpoint)
    label_data.append("%s" % flavor.allergen)
    label_data.append("%s" % flavor.sulfites_ppm)
    label_data.append("%s" % flavor.kosher)
    label_data.append("%s" % flavor.location_code)
    label_data.append("%s" % flavor.keywords)
    
    label_data_to_csv(label_data)
    
    output_file = "/var/www/django/dump/labels/label.pdf"
    
    command_line = "glabels-3-batch -o %s -i %s %s" % (output_file,
                                                     "/var/www/django/dump/labels/label.csv",
                                                     template_path)
    args = shlex.split(command_line)
    p = subprocess.Popen(args)
    p.wait()
    solution_preview(output_file)
    return output_file


def experimental_label(number):
    # create tempfile with the csv values set from values array
    # compose command line using template_path and tempfile
    # return path of output file
    template_path = '/var/www/django/fd/lab/experimental_product_continuous.glabels'
    experimental = ExperimentalLog.objects.get(experimentalnum=number)
    label_data = []
    if experimental.flavor is None:
        PINNUMBER = ""
        RMC = ""
        AS_OF = ""
        ALLERGEN = "UNKNOWN"
        SULFITES_PPM = "UNKNOWN"
        KOSHER = ""
        LOCATION_CODE = ""
        KEYWORDS = ""
    else:
        PINNUMBER = experimental.flavor.pinnumber
        RMC = experimental.flavor.rawmaterialcost.quantize(hundredths)
        AS_OF = experimental.flavor.lastspdate.date().strftime('%b %y')
        ALLERGEN = experimental.flavor.allergen
        SULFITES_PPM = experimental.flavor.sulfites_ppm
        KOSHER = experimental.flavor.kosher
        LOCATION_CODE = experimental.flavor.location_code
        KEYWORDS = experimental.flavor.keywords
    
    label_data.append("%s" % PINNUMBER)
    label_data.append("%s-%s" % (experimental.experimentalnum, experimental.initials))
    label_data.append(experimental.natart)
    label_data.append(experimental.product_name)
    label_data.append(experimental.label_type)
    label_data.append("%s" % date.today().isoformat())
    label_data.append("%s" % RMC)
    label_data.append("%s" % AS_OF)
    label_data.append("%s" % experimental.flash)
    label_data.append("%s" % ALLERGEN)
    label_data.append("%s" % SULFITES_PPM)
    label_data.append("%s" % KOSHER)
    label_data.append("%s" % LOCATION_CODE)
    label_data.append("%s" % KEYWORDS)

    label_data_to_csv(label_data)
    output_file = "/var/www/django/dump/labels/label.pdf"
    
    command_line = "glabels-3-batch -o %s -i %s %s" % (output_file,
                                                     "/var/www/django/dump/labels/label.csv",
                                                     template_path)
    args = shlex.split(command_line)
    
    p = subprocess.Popen(args).wait()
    
    return output_file
