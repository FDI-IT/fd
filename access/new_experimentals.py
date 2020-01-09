from datetime import date
import codecs
from datetime import datetime
from dateutil import parser
from access.models import ExperimentalLog
from newqc.models import ExperimentalRetain, next_experimental_retain_number
from pluggable.csv_unicode_wrappers import UnicodeWriter, UnicodeReader, unicode_csv_reader

def read_experimental_rows(new_experimentals_file):
    """Reads the file and generates row arrays.
    """
    f = open(new_experimentals_file, 'r')
    for l in f:
        yield l.rstrip().split(',')
    f.close()

def check_numbers(new_experimentals_file):
    """Checks to see if numbers are present in experimental log.
    """
    for new_experimental_row in read_experimental_rows(new_experimentals_file):
        parse_input_row(new_experimental_row)
        
def parse_numbers(new_experimentals_file):
    labels_csv_writer = UnicodeWriter(open('/tmp/%s_new_labels.csv' % date.today().isoformat(), 'wb'))
    retain_number = next_experimental_retain_number()
    for new_experimental_row in read_experimental_rows(new_experimentals_file):
        parsed_data = parse_input_row(new_experimental_row)
        if type(parsed_data) is str:
            print(parsed_data)
        else:
            parsed_data.append(retain_number)
            labels_csv_writer.writerow(list(map(str,parsed_data)))            
            retain_number += 1
            
def parse_input_row(input_row):
    experimental_num,initials,my_date,col,row = input_row
    try:
        el = ExperimentalLog.objects.get(experimentalnum=experimental_num)
        retain_experimental_num = el.experimentalnum
    except:
        return "%s - Unable to find experimental number." % experimental_num
        
    if initials.upper() != el.initials.upper():
        return "%s - Unable to match initials. %s %s" % (experimental_num, initials, el.initials)

    retain_product_name = el.product_name

    retain_initials = el.initials
    
    try:
        retain_date = date(my_date).isoformat()
    except:
        retain_date = el.datesent.date().isoformat()
        
    return [retain_experimental_num, retain_product_name, retain_initials, retain_date]

def parse_numbered_experimentals_csv(numbered_experimentals_csv_file):
    reader = UnicodeReader(open(numbered_experimentals_csv_file,'rb'))
    #reader = unicode_csv_reader(codecs.open(numbered_experimentals_csv_file,encoding='latin_1'))
    header_row = next(reader)
    experimental_log_index = header_row.index('experimental_log')
    retain_index = header_row.index('retain')
    date_index = header_row.index('date')
    for row in reader:
        my_experimental_log = row[experimental_log_index]
        my_retain = row[retain_index]

        try:
            el = ExperimentalLog.objects.get(experimentalnum=my_experimental_log)
        except ExperimentalLog.DoesNotExist as e:
            print(e)
            continue
        
        my_date_str = row[date_index]        
        my_date = parser.parse(row[date_index])
        if my_date == date.today():
            my_date = el.datesent
        
        existing_retains_with_my_retain = ExperimentalRetain.objects.filter(retain=my_retain)
        if existing_retains_with_my_retain.count() == 0:
            er = ExperimentalRetain(retain=my_retain,date=my_date,experimental_log=el)
            er.save()
        else:
            print(row)
            continue
        
def parse_undated_numbered_experimentals_csv(numbered_experimentals_csv_file):
    reader = UnicodeReader(open(numbered_experimentals_csv_file,'rb'))
    #reader = unicode_csv_reader(codecs.open(numbered_experimentals_csv_file,encoding='latin_1'))
    header_row = next(reader)
    experimental_log_index = header_row.index('experimental_log')
    retain_index = header_row.index('retain')
    today = date.today()
    for row in reader:
        my_experimental_log = row[experimental_log_index]
        my_retain = row[retain_index]

        try:
            el = ExperimentalLog.objects.get(experimentalnum=my_experimental_log)
        except ExperimentalLog.DoesNotExist as e:
            print(e)
            continue

        existing_retains_with_my_retain = ExperimentalRetain.objects.filter(retain=my_retain)
        if existing_retains_with_my_retain.count() == 0:
            er = ExperimentalRetain(retain=my_retain,date=today,experimental_log=el)
            er.save()
        else:
            print(row)
            continue
    