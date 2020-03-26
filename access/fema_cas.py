from django import forms
from access.models import Ingredient
from access.forms import CasFemaSpreadsheetsFileForm
import xlrd
from datetime import datetime  

## This page includes all functions that collectively read in 2 input spreadsheets with cas/fema data
## and compares it with the Ingredient info in the database
## It presents all suggested changes and errors to the user 
## and makes those changes upon user permission

##called in preview view, data presented in success template
def makeSelectedChanges(listOfFormsets):
    listOfPairs = []
    for formset in listOfFormsets:
        for form in formset.forms:
            if form.cleaned_data['Checkbox'] == True:                    ##only change ingredient if checked
                #get ingredient's old information
                pk = form.cleaned_data['ing_pk']
                ing = Ingredient.objects.get(pk=pk) 
                dicold = {'age':'old', 'ingredient':unicode(ing.product_name), 'FEMA':unicode(ing.fema), 'CAS':unicode(ing.cas)}
                #find ingredient information in form submission
                fema = form.cleaned_data['FEMA']
                cas = form.cleaned_data['CAS']
                ing_name = form.cleaned_data['ing_name']
                ## evaluate the disagreements table
                if formset.prefix=='errors':
                    if form.cleaned_data['ingName_errors'] != '':       ## if no choice was made, it must have previously been 'no error'
                        ing_name = form.cleaned_data['ingName_errors']
                    if form.cleaned_data['cas_error']!='no error':
                        cas = form.cleaned_data['cas_error']
                    if form.cleaned_data['fema_error'] != 'no error':
                        fema = form.cleaned_data['fema_error']
                        
                    ing.synonyms = form.error_synonyms
                    ing.save()         ## add all ingName options to ingredient_synonyms field
                    #synonyms are not added to ingredients table previously because name disagreements means they may not be synonyms
                    
                ing.fema = fema
                ing.cas = cas
                ing.product_name = ing_name
                ing.save()
                dicnew = {'age':'new', 'ingredient':ing.product_name, 'FEMA':ing.fema, 'CAS':ing.cas}
                listOfPairs.append((dicold,dicnew))
    #return pair of 2 dictionaries with ingredient's old info, and new info            
    return listOfPairs


#translates data to be analyzed by find_changes below
def find_pending_changes_from_cas_fema_files(uploadedFile1, uploadedFile2):
    file1 = '/tmp/' + str(datetime.now())
    destination = open(file1, 'wb+')
    for chunk in uploadedFile1.chunks():
        destination.write(chunk)
    destination.close()
    file2 = '/tmp/' + str(datetime.now())
    destination = open(file2, 'wb+')
    for chunk in uploadedFile2.chunks():
        destination.write(chunk)
    destination.close()
    return find_changes(file1, file2)


#immediately called by find_changes --> 3 dictionaries with cas-fema-name information according to the attached files
class ProductLookup():
    def __init__(self, path1, path2):                 #path1 to "Primary Names"   #path2 to "label_changed.xls"
        #The keys in each dictionary below will be the other two classifications
        # for example cas_dict={'fema': _____, 'ingredient_name': [_________]}        
        #this way when we are given the cas number, we can easily find the fema number or ingredient name

        self.cas_dict = {}
        self.fema_dict = {}
        self.ingredientName_dict = {}
        
        wb1 = xlrd.open_workbook(path1)
        sht1a = wb1.sheets()[0]                     #sht1a is "Primary Names & Synonyms"
        sht1b = wb1.sheets()[1]                     #sht2 is "Att. I: Chemicals, UN GHA classifications"
        wb2 = xlrd.open_workbook(path2)
        sht2 = wb2.sheets()[0]
        
        ##check sht1a
        for pos in range(sht1a.nrows-1)[1:]:
            cas = sht1a.cell_value(rowx=pos, colx=1)
            ingName = sht1a.cell_value(rowx=pos, colx=2) 
            fema = str(int(sht1a.cell_value(rowx=pos, colx=0)))
            
            #each cas number should have several potential ingredient names
            #if the cas number is in cas_dict, look to append the already existing list of ingredient names
            if cas in self.cas_dict.keys():
                ingOptions = self.cas_dict[cas]['ing']
            else:
                ingOptions=[]
            if ingName not in ingOptions:
                ingOptions.append(ingName)  
            self.cas_dict[cas] = {'ing':ingOptions, 'fema':fema}
            #same as above, each fema number can have several ingredient names
            if fema in self.fema_dict.keys():
                ingOptions = self.fema_dict[fema]['ing']
            else:
                ingOptions = []
            if ingName not in ingOptions:
                ingOptions.append(ingName)
            self.fema_dict[fema] = {'cas': cas, 'ing': ingOptions}
            #each ingredient name has one associated pair of cas/fema numbers
            self.ingredientName_dict[ingName]= {'cas':cas, 'fema':fema}
            
        #check sht1b 
        #there is only one cas# in sht1b that isn't in sht1a
        #there are a few ingredient names in sht1b that aren't in sht1a
        #All fema numbers in sht1b are in sht1a
        for pos in range(sht1b.nrows-1)[1:]:
            cas = sht1b.cell_value(rowx=pos, colx=1)
            ingName = sht1b.cell_value(rowx=pos, colx=2)
            fema = str(int(sht1b.cell_value(rowx=pos, colx=0)))
            if cas not in self.cas_dict.keys():
                self.cas_dict[cas] = {'ing': ingName, 'fema': fema}
            if ingName not in self.ing_dict_keys():
                self.ingredientName_dict[ingName] = {'cas':cas, 'fema': fema}
            
        #check sht2
        for pos in range(sht2.nrows-1)[2:1603]:             ##the end of my file had inappropraite info so i had manually find cell row to stop at
            cas = sht2.cell_value(rowx=pos, colx=0)
            ingName = sht2.cell_value(rowx=pos, colx=2)
            if cas not in self.cas_dict.keys():
                self.cas_dict[cas] = {'ing': ingName, 'fema': 'unknown'}
            if ingName not in self.ingredientName_dict.keys():
                self.ingredientName_dict[ingName] = {'cas': cas, 'fema': 'unknown'}
                
    def cas_dict_keys(self):
        return self.cas_dict.keys()   
    def fema_dict_keys(self):
        return self.fema_dict.keys()
    def ing_dict_keys(self):
        return self.ingredientName_dict.keys()
    
    def lookup_by_cas(self, cas):
        return self.cas_dict[cas]
    def lookup_by_fema(self,fema):
        return self.fema_dict[fema]
    def lookup_by_name(self, ingName):
        return self.ingredientName_dict[ingName]


##takes 2 spreadsheets with cas/fema info and forms a ProductLookup (class of 3 dicts comparing cas/fema/ingredient_name info
## according to the attached files
#find_changes checks each ingredient in the database to see if the ProductLookup conatins info about the ingredient cas/fema/name
def find_changes(path1, path2):
    lookup = ProductLookup(path1, path2)
    
    changed_ings = []   #list of ingredients with empty cas or fema numbers who's info is documented in ProductLookup
    disagreements = []  #list of ingredients in database who's information disagrees with info in ProdctLookup
    no_info =[]         #
    unknownFema=[]
    synonyms={}
    returnDict={'synonyms': synonyms, 'changed_ings':changed_ings, 'disagreements':disagreements, 'no_info':no_info, 'unknownFema':unknownFema}
    ingredientz = Ingredient.objects.all()
    for ing in ingredientz:
        #if cas# is in cas_dict, verify fema and ingName or modify the above lists in returnDict
        if ing.cas in lookup.cas_dict:
            returnDict= findFlaws_casDict(ing, lookup, returnDict)
        
        #ELSE, do the same for fema_dict
        elif(ing.fema in lookup.fema_dict):
            returnDict= findFlaws_femaDict(ing, lookup, returnDict)
        
        #ELSE do the same for name_dict
        elif(ing.product_name in lookup.ingredientName_dict):
            returnDict = findFlaws_nameDict(ing, lookup, returnDict)
        #ELSE the ingredient is not in the attached files so present it to the user         
        else:
            returnDict['no_info'].append(ing)
        
        #Silently add synonyms to ingredient_synonyms field (doesn't work for disagreements yet)
        if ing in returnDict['synonyms']:
            ing.synonyms = returnDict['synonyms'][ing]
            ing.save()
    
    ##return a dictionary including change options
    ## 'changes' is a list of lists. These sublists contain change options.
    del returnDict['synonyms']
    return returnDict



#called by find_changes above       
#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}
#returnDict explained above in find_changes      
def findFlaws_casDict(ing, lookup, returnDict):
    dict_oneCas = lookup.lookup_by_cas(ing.cas)
    error_dict = {'fema': 'no error', 'cas': 'no error', 'name': ['no error']}
    if ing.fema == '0' or ing.fema == '':
        if dict_oneCas['fema']!='unknown':       #we don't want to change empty fema numbers to 'unknown' (fema can be unknown because one of attached files has no fema info)
            ing.fema = dict_oneCas['fema']
            print "Fema number for cas number %s, previously blank, changed to %s" %(ing.cas,dict_oneCas['fema'])
            returnDict['changed_ings'].append([ing])
        else:
            ## ingredient fema number is empty and its not in the attached files
            print "Unknown Fema Number for ingredient with cas number %s"%ing.cas
            returnDict['unknownFema'].append(ing)
    elif (ing.fema != dict_oneCas['fema']):
        print "Disagreement of Fema Numbers for ingredient %s by cas_dict"%ing.product_name
        error_dict['fema']=dict_oneCas['fema']
        returnDict['disagreements'].append([ing, error_dict])
    if ing.product_name not in dict_oneCas['ing']:
        error_dict['name'] = dict_oneCas['ing']
        returnDict['disagreements'].append([ing, error_dict])
    else:
        returnDict['synonyms'][ing] = dict_oneCas['ing']  #all ingredient names used for given cas number
    return returnDict

#called by find_changes above
#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}  
def findFlaws_femaDict(ing, lookup, returnDict):
    dict_oneFema = lookup.lookup_by_fema(ing.fema)
    error_dict = {'fema': 'no error', 'cas': 'no error', 'name': ['no error']}
    if ing.cas=='0' or ing.cas == '':
        ing.cas = dict_oneFema['cas']
        returnDict['changed_ings'].append([ing])
        print "Empty cas number can be one of the following %s"%dict_oneFema['cas']
    elif(ing.cas != dict_oneFema['cas']):
        print "Disagreement of Cas Numbers for ingredient %s by fema_dict"%ing.product_name
        error_dict['cas'] = dict_oneFema['cas']
        returnDict['disagreements'].append([ing, error_dict])
    if ing.product_name not in dict_oneFema['ing']:
        #print "Disagreement of Ingredient Name for Fema Number %s"%ing.fema
        error_dict['name'] = dict_oneFema['ing']
        returnDict['disagreements'].append([ing, error_dict])
    else:
        returnDict['synonyms'][ing] = (dict_oneFema['ing'])   #all ingredient names used for given fema number
    return returnDict

#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}  
#will rarely be utilized because it's the 3rd else in the if statement of find_changes above  
def findFlaws_nameDict(ing, lookup, returnDict):
    dict_oneName = lookup.lookup_by_name(ing.product_name)
    error_dict = {'fema': 'no error', 'cas': 'no error', 'name': ['no error']} 
    if ing.cas=='0' or ing.cas=='':
        ing.cas = dict_oneName['cas']
        returnDict['changed_ings'].append([ing]) 
    elif ing.cas != dict_oneName['cas']:
        print "Disagreement of Cas Numbers for ingredient %s"%ing.product_name
        error_dict['cas']=dict_oneName['cas']
        returnDict['disagreements'].append([ing, error_dict]) 
    if ing.fema=='0' or fema=='':
        if dict_oneName['fema']!='unknown':
            ing.fema = dict_oneName['fema']
            print "Fema number for ingredient %s, previously blank, changed to %s" %(ing.product_name, dict_oneName['fema'])
            returnDict['changed_ings'].append([ing])
    elif ing.fema != dict_oneName['fema']:
        print "Disagreement of Fema Numbers for ingredient %s"%ing.product_name
        error_dict['fema']= dict_oneName['fema']
        returnDict['disagreements'].append([ing, error_dict])

    else:
        print "Unknown Fema Number for ingredient %s"%ing.product_name
        returnDict['unknownFema'].append(ing)                    
    return returnDict


##the 3 functions below (excluding helper function 'combine_errors_...') fill initial data for the 4 forms to present on preview view
def initialFormData_changes(changesList):
    initialFormData = []
    for ingList in changesList:
        for ing in ingList:
            initialFormData.append({
                                    'Checkbox': False,
                                    'ing_pk' : ing.pk,
                                    'FEMA' : ing.fema,
                                    'CAS' : ing.cas,
                                     'ing_name' : ing.name,
                                     })
    return initialFormData

#rid of any repeated ingredient names with multiple disagreements
def combine_errors_with_same_ingredient(errorsList):
    unique_ing_errors =[]
    if errorsList==[]:
        pass
    else:
        ings = [pair[0] for pair in errorsList]
        for i in range(len(ings)-1):
            if ings[i]==ings[i+1]:
                pass
            else:
                unique_ing_errors.append(errorsList[i])
        unique_ing_errors.append(errorsList[len(ings)-1])
    ## in the code above, the errorsList yields a list of pairs --> (ing, error_dict)
    ## if there are 2 errors for one ingredient, the error_dict will merely update for the second occurence of ing
    return unique_ing_errors
        
def initialFormData_errors(errorsList): 
    initialFormData=[]
    errorsList_condensed = combine_errors_with_same_ingredient(errorsList)
    for ingPair in errorsList_condensed:
        ing = ingPair[0]
        errorDict=ingPair[1]
        
        cas_error=errorDict['cas']
        fema_error=errorDict['fema']
        ingredient_name_errors_list=errorDict['name']
        if ingredient_name_errors_list != ['no error']:
            ingName_error_choices = []
            for item in ingredient_name_errors_list:
                ingName_error_choices.append((item, item))     ##ChoiceField
        else:
            ingName_error_choices = [('no error', 'no error')]
        initialFormData.append({
                                'Checkbox': False,
                                'ing_pk' : ing.pk,
                                'ingName_error_choices' : ingName_error_choices,
                                "cas_error" : cas_error,
                                "fema_error": fema_error, 
                                'FEMA' : ing.fema,
                                'CAS' : ing.cas,
                                'ing_name' : ing.name,
                                'ingName_synonyms' : ingredient_name_errors_list
                                #"ingName_noError": ingName_noError,
                                })
    return initialFormData
    
    
def initialFormData(ingList):
    initialFormData = []
    for ing in ingList:
        initialFormData.append({
                                'Checkbox': False,
                                 'ing_pk' : ing.pk,
                                'FEMA' : ing.fema,
                                'CAS' : ing.cas,
                                'ing_name' : ing.name,
                                })
    return initialFormData

## easy way to scramble info in database so that it displays errors and changes when functions above are called
def scramble_ingredients_in_DB():
    ing_names = ['wrong ingredient name', 'wrong name', 'Billy b ingredient']
    for i in range(3):
        ing = Ingredient.objects.all()[i]
        ing.product_name = ing_names[i]
        ing.synonyms = ''
        ing.save()
    cas = ['','0', 'wrong number']
    for i in range(3):
        ing = Ingredient.objects.all()[i+4]
        ing.cas = cas[i]
        ing.synonyms = ''
        ing.save()
    ing = Ingredient.objects.all()[8]
    ing.fema = ''
    ing.save()



from decimal import Decimal    
def create_ingredient(name='no name', cas='', fema=''):
    
    new_ing = Ingredient(product_name=name,
                         cas=cas,
                         fema=fema,
                         art_nati = "N/A",
                         unitprice = Decimal('540.36'),
                         sulfites_ppm = 1,
                         package_size = Decimal('0.00'),
                         minimum_quantity = Decimal('0.00'),
                         fob_point = 'unknown',
                         lead_time = '0',
                         )
    new_ing.save() 
    return new_ing   
    
        
        
        
        
        
        
        
        
        
        