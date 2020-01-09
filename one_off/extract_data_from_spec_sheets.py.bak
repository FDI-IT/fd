import os, xlrd
import datetime
from access.models import Flavor, SpecSheetInfo
from newqc.models import Retain
from collections import namedtuple
from dateutil.relativedelta import relativedelta

def extract_data_from_spec_sheets(spec_sheet_directory='/srv/samba/tank/Master Template Files/'):
    #Create a data structure to include additional data we are interested in
    additional_info = {}
    #1. Workbooks that have product names filled out on both Liquid and Powder sheets
    additional_info['product_name_both'] = []
    #2. Workbooks that have no product name on either sheet
    additional_info['product_name_none'] = []
    #3. A set of all text values in the first column (possible fields)
    additional_info['possible_fields'] = {}
    #4. Workbooks that are missing an ingredient statement
    additional_info['no_ingredient_statement'] = []
    #5. Workbooks that are missing product numbers
    additional_info['no_product_number'] = []
    #5. Workbooks that correspond to flavors that no longer exist
    additional_info['flavor_does_not_exist'] = []
    #6. Workbooks that cannot be opened
    additional_info['cannot_be_opened'] = []
    #7. Total saved spec sheet count
    additional_info['saved_count'] = 0
    #8. Total spec sheets
    additional_info['total_count'] = 0
    #9. No date
    additional_info['no_date'] = []
    #10 Multiple spec sheets for the same product
    additional_info['completed_products'] = []
    additional_info['duplicate_products'] = []
    
    
    #iterate through all the files in master template files
    for file_name in file_walker(spec_sheet_directory):
        print file_name
        extract_data_from_spec_sheet(spec_sheet_directory, file_name, additional_info)
        
    return additional_info
        
def extract_data_from_spec_sheet(spec_sheet_directory, file_name, additional_info):
    product_type = None
    main_sheet = None
    
    spec_sheet_path = spec_sheet_directory + file_name
    try:
        workbook = xlrd.open_workbook(spec_sheet_path)
    except:
        additional_info['cannot_be_opened'].append(file_name)
        workbook = None

    if workbook != None:
        #only process excel files that actually contain spec sheets, do nothing with any other excel files    
        if 'Spec Sheet Liquid' in workbook.sheet_names() or 'Spec Sheet Powder' in workbook.sheet_names():
                        
            additional_info['total_count'] += 1
            
            # 1. Check for powder spec sheet
            # 2. If product name field is filled in, set product_type to powder
            # 3. If it is not, check for the liquid spec sheet
            # 4. If liquid product name filled in, set product_type to liquid
                
            if 'Spec Sheet Liquid' in workbook.sheet_names():
                liquid_sheet = workbook.sheet_by_name('Spec Sheet Liquid')
                if check_product_name_exists(liquid_sheet) == True:
                    product_type = 'Liquid'
                    main_sheet = liquid_sheet
            
            if 'Spec Sheet Powder' in workbook.sheet_names():
                powder_sheet = workbook.sheet_by_name('Spec Sheet Powder')
                if check_product_name_exists(powder_sheet) == True:
                    
                    #Here, if the product type is already liquid, then the product name exists on both sheets
                    if product_type == 'Liquid':
                        additional_info['product_name_both'].append(file_name)    
                                
                    product_type = 'Powder'
                    main_sheet = powder_sheet
            
            #If this point is reached and the main sheet is still none, there is no product name
            if main_sheet == None:#if there is no main sheet, neither liquid nor powder spec sheets are filled out
                additional_info['product_name_none'].append(file_name)
            else:
                #Now we have the main sheet, time to start extracting data!
                #First we need to figure out the product number so we know what flavor we're dealing with
                
                #For now, we'll create a dictionary containing all the fields we could possibly extract
                data_dictionary = extract_all_data(main_sheet)
                
                spec_sheet_mapping_dict = {
                    'aerobic plate count':'aerobic_plate_count',
                    'aw':'water_activity',
                    'bostwick consistometer':'bostwick_consistometer',
                    'brix':'brix',
                    'description':'description',
                    'date':'date',
                    'escherichia coli':'escherichia_coli',
                    'fat content':'fat_content',
                    'flash point':'flash_point',
                    'ingredient statement':'ingredient_statement',
                    'moisture':'moisture',
                    'mold':'mold',
                    'ph':'ph',
                    'product name':'product_name',
                    'product number':'product_number',
                    'salmonella':'salmonella',
                    'salt content':'salt_content',
                    'sieve': 'sieve',
                    'solubility':'solubility',
                    'specific gravity':'specific_gravity',
                    'specification code':'specification_code',
                    'supercedes':'supercedes',
                    'shelf life':'shelf_life',
                    'standard plate count':'standard_plate_count',
                    'storage':'storage',
                    'yeast':'yeast',
                    #the keys below are duplicates found in the MTF - consolidate them with the keys above
                    ' ingredient statement':'ingredient_statement',
                    'e.coli':'escherichia_coli',
                    'fat':'fat_content',
                    'fat content roese-gottlieb':'fat_content',
                    'fda /usda  ingredient statement':'ingredient_statement',
                    'non flavor ingredient statement':'ingredient_statement',
                    'salt':'salt_content',
                    'std. plate count':'standard_plate_count',
                    'water activity (aw)':'water_activity',

                }
                
                #create a SpecSheetInfo object 
                #iterate through the extracted data and process the information
                
                #1. Get the product number and check if there already exists a SpecSheetInfo objects for that product
                #2. If yes, edit that object
                #3. If no, create a new SpecSheetInfo object
                        
                try: #first we try to use the product number on the spec sheet
                    product_number = data_dictionary['product number'].split('-',1)[1] #split up the prefix-product number string
                    Flavor.objects.get(number=product_number)
                except: #if that does not work, try to use the product number in the file name
                    additional_info['no_product_number'].append(file_name)
                    try:
                        product_number = file_name.split('.',1)[0]
                        Flavor.objects.get(number=product_number)
                    except: #if even that does not work, set product number to None
                        additional_info['flavor_does_not_exist'].append(file_name)
                        product_number = None
                
                if product_number != None:
        
                    flavor = Flavor.objects.get(number=product_number)
                
                    #use existing SpecSheetInfo objects if they exist
                    if SpecSheetInfo.objects.filter(flavor=flavor).exists():
                        ssi = SpecSheetInfo.objects.get(flavor=flavor)
                    else:
                        ssi = SpecSheetInfo(flavor=flavor)
                    
                    for key, value in data_dictionary.iteritems():
                        #save all the extracted data into the SpecSheetInfo object
                        #if it is the date field, convert it from an xldate to datetime.date format
                        if key not in additional_info['possible_fields']:
                            additional_info['possible_fields'][key] = 1
                        else:
                            additional_info['possible_fields'][key] += 1
                        if key == 'date':
                            try:
                                converted_date = datetime.datetime(*xlrd.xldate_as_tuple(value, workbook.datemode)).date()
                                ssi.date = converted_date
                            except:
                                additional_info['no_date'].append(file_name)
                                ssi.date = None
                        else:
                            if key in spec_sheet_mapping_dict:
                                setattr(ssi,spec_sheet_mapping_dict[key],value)
                    
                    if ssi.ingredient_statement == None or ssi.ingredient_statement == '':
                        additional_info['no_ingredient_statement'].append(file_name)
#                     else:
#                         if ssi.date == None:
#                             ssi.verified = False
#                         else:
#                             twoyearsago = datetime.datetime.now().date() - relativedelta(years=2)
#                             if Retain.objects.filter(lot__flavor__in=ssi.flavor.loaded_renumber_list).filter(date__gte=twoyearsago).exists() and ssi.date > datetime.date(2014, 01, 01):
#                                 ssi.verified = True
#                             else:
#                                 ssi.verified = False
                    
                    ssi.source_path = spec_sheet_path
                    ssi.save()
                    additional_info['saved_count'] += 1
                    if flavor in additional_info['completed_products']:
                        additional_info['duplicate_products'].append(flavor)
                    else:
                        additional_info['completed_products'].append(flavor)
    
def extract_all_data(sheet):
    #This function will return a dictionary containing all relevant fields and values
    data_dict = {}
    
    #We must iterate through all rows and check the first column in each row for a field name
    num_rows = sheet.nrows - 1
    num_cells = sheet.ncols - 1
    
    #We can start at row 7 because all spec sheets have the same header for the first few rows
    current_row = 7
    
    while current_row < num_rows:
        #There are two possibilities when extracting field values:
        #1. The value is contained in the same row as the field name (product name, product number, etc)
        #2. The value is contained a variable number of rows below the field name (ingredient statement, description)
        
        #This is how we proceed
        #1. Check the first column of the row for a text value
        #2. If the value is not 'Ingredient Statement' or 'Description', check the remaining columns for a value
        #3. If the value IS 'Ingredient Statement' or Description', check the rows below for a value in the first column
        
        if sheet.cell_type(current_row, 0) == 1:
            #we remove the semicolon and anything after it from the end of the string, and force lowercase
            field_name = sheet.cell_value(current_row, 0).split(':', 1)[0].lower()
            
            #If description or ingredient statement, check rows below
            if any(term in field_name for term in ['description','ingredient statement','shelf life','storage']):
                #set the description/ingredient statement to None and change it if we find one
                val = None
                row_increment = 1
                #Check the next 4 rows for a value
                while row_increment <= 4:
                    if sheet.cell_type(current_row + row_increment, 0) == 1:
                        val = sheet.cell_value(current_row + row_increment, 0)
                        break
                    row_increment += 1
                
                data_dict[field_name] = val   
                
            #Otherwise, check the cells in the same row for the value
            else:
                current_cell = 1
                while current_cell < num_cells:
                    if sheet.cell_type(current_row, current_cell) in [1, 3]:
                        data_dict[field_name] = sheet.cell_value(current_row, current_cell)
                        break

                    current_cell += 1

        #Now we have to check the columns to the right for certain fields which are put in a separate column
        #Start at the second cell
        current_cell = 1

        #Iterate through all cells in the row
        while current_cell < num_cells:
            #If a string is found
            if sheet.cell_type(current_row, current_cell) in [1]:
                #get the string value
                cellval = sheet.cell_value(current_row, current_cell).split(':', 1)[0].lower()
                #check if it is one of the fields that exist in the second column of spec sheets
                if any(term in cellval for term in ['yeast','mold']):
                    #if it is, iterate through the fields to the right and set the first string/float found as the cellval
                    while current_cell < num_cells:
                        current_cell += 1
                        if sheet.cell_type(current_row, current_cell) in [1, 3]:
                            data_dict[cellval] = sheet.cell_value(current_row, current_cell)
                            break #exits the current while loop
                        current_cell += 1

            current_cell += 1

        current_row += 1

    return data_dict

def check_product_name_exists(sheet):
    num_rows = sheet.nrows - 1 #rows and columns are zero-based, so we subtract by 1
    num_cells = sheet.ncols - 1
    
    current_row = 0
    
    while current_row < num_rows:
        
        row = sheet.row(current_row)
        
        if 'Product Name' in sheet.cell_value(current_row, 0):
        
            #if we see 'Product Name' in the first cell, check the rest of the cells in the
            #same row to see if they are all empty or if a product name exists on this sheet
            current_cell = 1
            while current_cell < num_cells:
                #cell types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                #If we find a text value cell in the same row as 'Product Name', return True
                if sheet.cell_type(current_row, current_cell) == 1:
                    return True
                current_cell += 1
                
        current_row += 1
    
    #If no product name exists, return False
    return False    
    
def file_walker(walk_paths):
    """Iterates through walk_paths and returns the full file path of any
    jpg or png files.
    """
    for filename in os.listdir(walk_paths):
        if filename.endswith(".xls"):
            yield filename
    
#     for wp in walk_paths:
#         for root, dirnames, filenames in os.walk(wp):
#             for filename in filenames:
#                 if filename.lower().endswith(('jpg','png')):
#                     yield os.path.join(root,filename)