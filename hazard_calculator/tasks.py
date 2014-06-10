
#this file defines the main function of this application
#it takes the path to the labels file, calculates the hazards, execute the callback function if it is defined,
#and return a dictionary of calculated hazards

def calculate_hazards(path_to_labels, callback_function = None):
    
    parsed_data = parse_hazards(path_to_labels)
    
    if callback_function != None:
        callback_function(parsed_data)
        
    
    