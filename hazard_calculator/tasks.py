import xlrd  # @UnresolvedImport
import re

#use regular expressions to match tokens with expected hazards


#LD50 RE: covers ATI, ATO, and ATD; returns category and ld50
#examples: ATI 5(300), ATO 3(300), ATI 4(3350 ppm), 

#NEED TO ALSO RETURN THE HAZARD (HOW WILL YOU KNOW IF IT'S INHALATION/ORAL/DERMAL??)
ld50_re = re.compile('AT([IOD])[^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*')

#the above will match '#anything ATI #anything (digit) #anything ( #anything digits #anything )



        
        
#EH RE: covers EH A and EH C; returns chronic/acute and category

#in the re below, there must be ONE SPACE between 'EH' and either 'A' or 'C' and no space between A/C and the category
eh_re = re.compile('EH ([AC])(\d)')




#this file defines the main function of this application
#it takes the path to the labels file, calculates the hazards, execute the callback function if it is defined,
#and return a dictionary of calculated hazards

def calculate_hazards(path_to_labels, callback_function = None):
    
    parsed_data = parse_hazards(path_to_labels)
    
    if callback_function != None:
        callback_function(parsed_data)
        
    
    
def parse_hazards(path_to_labels):
    
    
    labels = xlrd.open_workbook(path_to_labels)
    
    #pseudocode
    
    token_dict = {
                  ''
                  
                  
                  }
    
    def ld50_hazard(token):
        #determine hazard from token characters
        #find ld50 from token
        
        #save hazard and ld50 to GHSIngredient - need cas number to do that
        pass
    
    hazard_re = re.compile('([^(,\n]*(?:(?:\([^)]*\))*[^,(\n]*)*)[,\n]?')
    
    token_list = set()
    sheet = labels.sheets()[0]
    
    for row in range(sheet.rows):
        contents = sheet.cell(row, 3).value
        for token in hazard_re.findall(contents):
            token_list.add(token)
    
    ingredient_tokens = {}
    
    for row in range(sheet.rows):
        
        cas_number = sheet.cell(row, 0).value
        ingredient_tokens[cas_number] = []
        
        contents = sheet.cell(row, 3).value
        
        ingredient_tokens[cas_number] = hazard_re.findall(contents)
        
#         for token in hazard_re.findall(contents):
#             ingredient_tokens[cas_number].append(token)
    
    
    dictionary = {
                  'ld50_hazard':'AT[IOD][^\d]*(\d)[^(\d]*\([^\d]*([\d]+)[^)]*',
                  }
    
    
    def parse_token(token):
        #input is a token
        #output tells us what parser we should use on the token
        

        if ld50_re.search(token):
            return ['ld50_hazard', ld50_re.findall(token)[0]]
        

        
        if eh_re.search(token):
            if eh_re.findall(token)[0][0] == 'A':
                return ['acute_aquatic_toxicity_hazard', eh_re.findall(token)[0]]
            elif eh_re.findall(token)[0][0] == 'C':
                return ['chronic aquatic toxicity hazard', eh_re.findall(token)[0]]
        
