import xlrd  # @UnresolvedImport
import re

path_to_labels = '/home/matta/label.xls'

#use regular expressions to match tokens with expected hazards

hazard_re = re.compile('([^(,\n]*(?:(?:\([^)]*\))*[^,(\n]*)*)[,\n]?')


'''
LD50 RE: covers ATI, ATO, and ATD; returns category and ld50
examples: ATI 5(300), ATO 3(300), ATI 4(3350 ppm), 

will match '#anything ATI #anything (digit) #anything ( #anything digits #anything )
'''

ld50_re = re.compile('AT([IOD])[^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*')


        
'''        
EH RE: covers EH A and EH C; returns chronic/acute and category

there must be ONE SPACE between 'EH' and either 'A' or 'C' and no space between A/C and the category
'''

eh_re = re.compile('EH ([AC])(\d)')



'''
flammable_re: covers FL, FS, and FG

will find the first digit after either fl, fg, or fs
will not match if it does not contain fl fg or fs, or if there are no digits afterward
'''
flammable_re = re.compile('F([LGS])[^\d]*(\d)')


'''
tost_re: covers STO - SE and STO - RE

will find the first digit after SE or SR
will match '#ANYTHING STO #ANYTHING - #ANYTHING (S or R) E #ANYTHING digit

'''

tost_re = re.compile('STO[^-]-[^SR]([SR])E[^\d]*(\d)')

'''
These are the re's for SCI, EDI, and CAR
These are simpler to parse since each re covers one hazard, only need to find the category
'''

sci_re = re.compile('SCI[^\d]*(\d)')
edi_re = re.compile('EDI[^\d]*(\d)')
car_re = re.compile('CAR[^\d]*(\d)')


#this file defines the main function of this application
#it takes the path to the labels file, calculates the hazards, execute the callback function if it is defined,
#and return a dictionary of calculated hazards

def calculate_hazards(path_to_labels, callback_function = None):
    
    parsed_data = parse_hazards(path_to_labels)
    
    if callback_function != None:
        callback_function(parsed_data)
        
'''

PARSE_HAZARDS

input: labels.xls

result: dictionary with cas numbers as keys, hazard info as values

#is there a point in returning a dictionary instead of just saving them to the GHSIngredients?

Example:

have dictionary of cas numbers/tokens

token is 'ATI 4(7300)'

'''

def parse_hazards(path_to_labels):
    
    
    labels = xlrd.open_workbook(path_to_labels)
    sheet = labels.sheets()[0]
    
    complete_hazard_dict = {}
    
    '''
    ex: complete_hazard_dict = { 8851: 
                                    {
                                        'acute_aquatic_toxicity_hazard': 1
                                        'acute_hazard_oral': 3
                                        'oral_ld50': 100
                                    },
                                ...
                               }
    '''
    for row in range(sheet.nrows):
        
        cas_number = sheet.cell(row, 0).value
        
        #each cas number should only appear once in the document
        #if not, have to change this code to account for a cas number appearing twice;
        #    currently, if a cas number appears twice, the hazards from the first occurence will be erased
        
        complete_hazard_dict[cas_number] = {}    
        ingredient_hazards = complete_hazard_dict[cas_number]  #easier to understand
        
        contents = sheet.cell(row, 3).value
        
        for token in hazard_re.findall(contents):
            for hazard, value in parse_token(token): #a single token may represent multiple fields
                ingredient_hazards[hazard] = value        #namely, ld50 hazards correspond to ld50 field and hazard field
            
            
    return complete_hazard_dict
          

   
    
re_dict = {
                ld50_re:
                    {
                        'O': ('acute_hazard_oral', 'oral_ld50'),
                        'D': ('acute_hazard_dermal', 'dermal_ld50'),
                        'I': ('acute_hazard_inhalation', 'inhalation_ld50')
                     },
                eh_re: 
                    {
                        'A': 'acute_aquatic_toxicity_hazard',
                        'C': 'chronic_aquatic_toxicity_hazard'
                     },
                flammable_re:
                    {
                        'L': 'flammable_liquid_hazard',
                        'G': 'emit_flammable_hazard',
                        'S': 'flammable_solid_hazard'
                     },
                tost_re:
                    {
                        'S': 'tost_single_hazard',
                        'R': 'tost_repeat_hazard'
                    },
                sci_re: 'skin_corrosion_hazard',
                edi_re: 'eye_damage_hazard',
                car_re: 'carcinogenicty_hazard,'
                
                
          }

def parse_token(token):
    
    '''
    input: a token
    output: a list of (hazard, value) tuples 
    
    the output will most likely be a single tuple
    instances where there will be multiple tuples:
        - the token corresponds to an ld50 hazard
        - for some reason there are multiple hazards in the same token
            (this might happen if a typo caused two hazards to not be separated by comma)
            ex. token = 'ATO 5(4700) ATI 3(1000)'
    '''

    hazard_list = []

    '''
    
    First option: This is the 'less redundant' implementation, which uses the dictionary 're_dict' above.
    
    It can be hard to understand and uses a confusing data structure...
    
    for re in re_dict:
               
    
    '''
    
    for re in re_dict:
        if re.search(token):
            re_results = re.findall(token)
            
            if len(re_results[0]) == 3: #ld50 hazards
                
                for hazard, category, ld50 in re_results:
                    for hazard_letter in re_dict[re]:
                        if hazard == hazard_letter:
                            hazard_list.append((re_dict[re][hazard_letter][0], category))
                            hazard_list.append((re_dict[re][hazard_letter][1], ld50))
                            
            elif len(re_results[0]) == 2: #tost, eh, flammable hazards
                
                for hazard, category in re_results:
                    for hazard_letter in re_dict[re]:
                        if hazard == hazard_letter:
                            hazard_list.append((re_dict[re][hazard_letter], category))
                            
            elif len(re_results[0]) == 1: #sci, edi, car hazards
                
                category = re_results[0]
                
                hazard_list.append((re_dict[re], category))
            
    return hazard_list
            
    '''
    
    This implementation, while easier to understand, uses many similar if statements and takes a lot
        more space than the previous implementation.

    if ld50_re.search(token):
        re_results = ld50_re.findall(token) #
        for hazard, category, ld50 in re_results: #result will be in the form ('D', '5', '4700')

            if hazard == 'O':
                hazard_list.append(('acute_hazard_oral', category))
                hazard_list.append(('oral_ld50', ld50))
            elif hazard == 'D':
                hazard_list.append(('acute_hazard_dermal', category))
                hazard_list.append(('dermal_ld50', ld50))
            elif hazard == 'I':
                hazard_list.append(('acute_hazard_inhalation', category))
                hazard_list.append(('inhalation_ld50', ld50)) #currently no inhalation ld50 in database
            
    
    if eh_re.search(token):
        re_results = eh_re.findall(token)
        
        for hazard, category in re_results:
            
            if hazard == 'A':
                hazard_list.append(('acute_aquatic_toxicity_hazard', category))
            elif hazard == 'C':
                hazard_list.append(('chronic_aquatic_toxicity_hazard', category))

    if flammable_re.search(token):
        re_results = flammable_re.findall(token)
        
        for hazard, category in re_results:
            if hazard == 'L':
                hazard_list.append(('flammable_liquid_hazard', category))
            elif hazard == 'G':
                hazard_list.append(('emit_flammable_hazard', category))
            elif hazard == 'S':
                hazard_list.append(('flammable_solid_hazard', category))
    
    if tost_re.search(token):
        re_results = tost_re.findall(token)
        
        for hazard,_category in re_results:
            if hazard == 'R':
                hazard_list.append(('tost_single_hazard', category))
            elif hazard == 'S':
                hazard_list.append(('tost_repeat_hazard', category))
    
    if len(sci_re.findall(token)) > 0:
        category = sci_re.findall(token)[0] #only one
        
        hazard_list.append(('skin_corrosion_hazard', category))
    
    if len(edi_re.findall(token)) > 0:
        category = edi_re.findall(token)[0]
        
        hazard_list.append(('eye_damage_hazard', category))
        
    if len(car_re.findall(token)) > 0:
        category = car_re.findall(token)[0]
        
        hazard_list.append(('carcinogenicty_hazard', category)) 
        
    return hazard_list

    '''        
        
        
        
        
        
        

