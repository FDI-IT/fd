import re
import glob
import os
import csv
from collections import defaultdict

from xlrd import open_workbook

from access.models import *

flash_point_re = re.compile('flash',re.IGNORECASE)
number_re = re.compile('[0-9]+')
spg_re = re.compile('specific',re.IGNORECASE)

spec_re = re.compile('^([0-9]+)(\.[0-9]+)?(\s*\+\s*\/\s*\-\s*.+)?')

def search_for_spec(mtf, search_term):
    spec_rows = []
    
    search_re = re.compile(search_term, re.IGNORECASE)
        
    for sheet in mtf.sheets():
        for row in range(sheet.nrows):
            for cell in sheet.row_slice(row):
                try:
                    search_result = search_re.search(cell.value)
                except TypeError:
                    continue
                if search_result:
                    spec_rows.append((sheet.name, sheet.row_slice(row)))

    return spec_rows

# def search_mtf_for_specs(mtf, spec_search_list):
#     #return a dictionary containing spec search terms and all the possible values
#     #{ 'flash':[(sheet, point, range), ... ] 'spg':[(...)], ...}
#     spec_value_dict = {}
#     
#     for spec_search_term, user_friendly_term in spec_search_list:
#         
#         spec_rows = search_for_spec(mtf, spec_search_term)
#         
#         possible_spec_values = []
# 
#         
#         spec_value_dict[user_friendly_term] = {}
#         
#         for sheet, row in spec_rows:
# 
#             for cell in row:
#                 try:
#                     #the following only works as intended if there is only one result per cell.  it only gets the first result per cell
#                     #if there is more than one possible spec value in any given cell, need to change the regular expression 'spec_re'
#                     #and change the code below
#                     
#                     
#                     cell_result = spec_re.findall(cell.value)
# #                     for point, decimal, range in spec_re.findall(cell.value):
# 
#                     if len(cell_result) > 0:
#                         if sheet not in spec_value_dict[user_friendly_term]:
#                             #spec_value_dict[user_friendly_term][sheet] = [(point, range)]
#                             spec_value_dict[user_friendly_term][sheet] = ["".join(cell_result[0])]
#                         else:
#                             spec_value_dict[user_friendly_term][sheet].append("".join(cell_result[0]))
#                           
# #                         if (sheet, point, range) not in possible_spec_values:
# #                             possible_spec_values.append((sheet, point, range))
#                 except TypeError:
#                     print "TYPE ERROR IDK WHAT TO DO HERE"
#             
#         
#     return spec_value_dict
                           
                           

def search_mtfs_for_specs(mtf_list, spec_search_list): #make first argument list of flavors with the same formula
    #return a dictionary containing spec search terms and all the possible values
    #{ 'flash':[(sheet, point, range), ... ] 'spg':[(...)], ...}
    spec_value_dict = {}
     
    for spec_search_term, user_friendly_term in spec_search_list:
         
        possible_spec_values = []
        
        spec_value_dict[user_friendly_term] = {}
        #print mtf_list
        
        for mtf, flavor_number in mtf_list:
            
            spec_rows = search_for_spec(mtf, spec_search_term)
             
             
     
             
            
             
            for sheet, row in spec_rows:
                
                sheet = "%s: " % flavor_number + sheet
                    
                for cell in row:
                    try:
                        #the following only works as intended if there is only one result per cell.  it only gets the first result per cell
                        #if there is more than one possible spec value in any given cell, need to change the regular expression 'spec_re'
                        #and change the code below
                         
                         
                        cell_result = spec_re.findall(cell.value)
    #                     for point, decimal, range in spec_re.findall(cell.value):
     
                        if len(cell_result) > 0:
                            if sheet not in spec_value_dict[user_friendly_term]:
                                #spec_value_dict[user_friendly_term][sheet] = [(point, range)]
                                spec_value_dict[user_friendly_term][sheet] = ["".join(cell_result[0])]
                            else:
                                spec_value_dict[user_friendly_term][sheet].append("".join(cell_result[0]))
                               
    #                         if (sheet, point, range) not in possible_spec_values:
    #                             possible_spec_values.append((sheet, point, range))
                    except TypeError:
                        print "TYPE ERROR IDK WHAT TO DO HERE"
                 
         
    return spec_value_dict
    

def get_the_mtfs():
    for mtf_path in get_the_mtf_paths():
        yield open_workbook(mtf_path)
        
def get_the_mtf_paths(path="/home/matta/Master Template Files/*.[Xx][Ll][Ss]"):
    for mtf_path in glob.glob(path):
        yield mtf_path

def crunch_the_mtfs(all_the_mtfs):
    sheet_occurence = defaultdict(int)
    for mtf in all_the_mtfs:
        for s in mtf.sheets():
            sheet_occurence[s.name]+=1
            
def flash_search(mtf):
    for s in mtf.sheets():
        for row in range(s.nrows):
            for cell in s.row_slice(row):
                try:
                    sresult = flash_point_re.search(cell.value)
                except TypeError:
                    continue
                if sresult:
                    yield s.row_slice(row)
                    break
                
ignore_these_flashes = set((
    0,1,2,4,5,6,8,10,25,3,
)) 

def new_flash_search(mtf):
    flash_vals = set()
    for flash_row in flash_search(mtf):
        for flash in flash_row:
            try:
                for sresult in number_re.findall(flash.value):
                    flash_vals.add(sresult)
            except TypeError:
                flash_vals.add(flash.value)
    return { mtf_path: flash_vals - ignore_these_flashes } 

def aggregate_flash_search(all_the_mtf_paths):
    
    for mtf_path in all_the_mtf_paths:
        mtf = open_workbook(mtf_path)
        flash_vals = set()
        for flash_row in flash_search(mtf):
            for flash in flash_row:
                try:
                    for sresult in number_re.findall(flash.value):
                        flash_vals.add(int(sresult))
                except TypeError:
                    flash_vals.add(int(flash.value))
        
        base_path = os.path.basename(mtf_path).split('.')[0]
        try:
            f = Flavor.objects.get(number=base_path)
            db_flashpoint = f.flashpoint
        except:
            continue
       
        possible_flashes = flash_vals - ignore_these_flashes
        l = len(possible_flashes)
        
        if l == 1:
            if db_flashpoint in possible_flashes:
                continue
            else:
                yield [base_path,db_flashpoint] + list(possible_flashes)
        elif l > 1:
            if db_flashpoint in possible_flashes:
                possible_flashes.remove(db_flashpoint)
            yield [base_path,db_flashpoint] + list(possible_flashes)
        else:
            pass
            # flash_val contains one element that is the flash accorind go spec sheets
            
def flash_report_writer():
    reportwriter = csv.writer(open('flashes.csv','wb'),delimiter=",",quotechar='"')
    reportwriter.writerow(['number','flash1','flash2','flash3','flash4','flash5','flash6','flash7','flash8',])        
    for flash in aggregate_flash_search(get_the_mtf_paths()):
        reportwriter.writerow(flash)
    
def search_sheet(s,phrase):
    for row in range(s.nrows):
        for col in range(s.ncols):
            v = s.cell(row,col).value

def count_flash_occurences(all_the_mtfs):
    flash_occurence = defaultdict(int)
    
#sheets = {
#        ""
#}

