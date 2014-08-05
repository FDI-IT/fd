from access.models import Ingredient
from access.forms import CasFemaSpreadsheetsFileForm
import xlrd
from datetime import datetime  

##called in preview view, data presented in success template
def makeSelectedChanges(formset):
    listOfPairs = []
    for form in formset.forms:
        if form.cleaned_data['Checkbox'] == True:
            pk = form.cleaned_data['ing_pk']
            ing = Ingredient.objects.get(pk=pk) 
            dicold = {'age':'old', 'ingredient':ing.name, 'FEMA':ing.fema, 'CAS':ing.cas}
            fema = form.cleaned_data['FEMA']
            cas = form.cleaned_data['CAS']
            setattr(ing, 'fema', fema)
            ing.save()
            setattr(ing, 'cas', cas)
            ing.save()
            dicnew = {'age':'new', 'ingredient':ing.name, 'FEMA':ing.fema, 'CAS':ing.cas}
            listOfPairs.append((dicold,dicnew))
    return listOfPairs


##called in upload view, data presented in preview template        
def find_pending_changes_from_cas_fema_file(uploadedFile):
    file = '/tmp/' + str(datetime.now())
    destination = open(file, 'wb+')
    for chunk in uploadedFile.chunks():
        destination.write(chunk)
    destination.close()
    return find_fema_changes(file)
   
    
## called above
def find_fema_changes(path1):
    CAS_FEMA_dict=create_CAS_FEMA_dict(path1)
    
    ingredientz = Ingredient.objects.all()
    changed_ings = []
    evaluated_ings = []
    for k,v in CAS_FEMA_dict.iteritems():
        ## This assigns a fema number to Ingredients with CAS#s but without a FEMA #
        ## It will print an error if the CAS,FEMA pair disagrees.
        ingredients = ingredientz.filter(cas=k)
        for ing in ingredients:
            if ing.fema == '':
                ing.fema = '0'
                ing.save()
            if float(ing.fema) != float(v) or ing.fema =='':
                if ing.fema == '' or ing.fema== '0':
                    print "No previous fema information for CAS number %s. Fema number %s filled in" %(k,v)
                    setattr(ing, 'fema', v)
                    changed_ings.append(ing)

                else:
                    ###INFORM THE USER THAT THERE IS A DISCREPANCY
                    print "Ingredients with the same CAS number (%s) have different FEMA numbers" %k
        ## If an ingredient has an empty cas number, but a fema number, it will assign a CAS number
        ingredients2 = ingredientz.filter(fema=v)
        for ing in ingredients2:
            if ing.cas=='' or ing.cas=='0':
                print "fema number %s previously had no CAS number. It will be filled in with CAS number %s" %(v,k)
                setattr(ing, 'cas', k)
                changed_ings.append(ing)
    for ing in ingredientz:
        if ing.cas=='' and ing.fema == '':
            print "Ingredient: %s has no cas or fema information" %ing.product_name
    return changed_ings
 
                
##called above
def create_CAS_FEMA_dict(path1):
    ##path1 is path to excel spread sheet with both the CAS and FEMA numbers
    ##path2 is the path to "IFRA/IOFI Labeling Manual 2013"
    workbook = xlrd.open_workbook(path1)
    sheet = workbook.sheets()[1]
    
    CAS_FEMA_dict = {}
    ##for pos in loc_repeatedFEMAs:
    for pos in range(sheet.nrows - 1)[1:]:               #excluding first row of headers.
        cas = sheet.cell_value(rowx=pos, colx=1)
        fema = sheet.cell_value(rowx=pos, colx=0)
        CAS_FEMA_dict[cas] = fema
    return CAS_FEMA_dict
















######Below considers 2 input files, more precise results ############

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

# from django.core.files import File
# def find_pending_changes_from_cas_fema_files(formset):
#     lst=[]
#     for form in formset.forms:             #file1 is "primary names"
#         file = form.cleaned_data['file']
#         newfile = '/tmp/' + str(datetime.now())
#         destination = open(newfile, 'wb+')
#         for chunk in file.chunks():
#             destination.write(chunk)
#             destination.close()
#         lst.append(newfile)
#     return find_changes(lst[0], lst[1])




class ProductLookup():
    def __init__(self, path1, path2):                 #path1 to "Primary Names"
        self.cas_dict = {}                            #path2 to "label_changed.xls"
        self.fema_dict = {}
        self.ingredientName_dict = {}
        
        wb1 = xlrd.open_workbook(path1)
        sht1a = wb1.sheets()[0]                     #sht1a is "Primary Names & Synonyms
        sht1b = wb1.sheets()[1]
        wb2 = xlrd.open_workbook(path2)
        sht2 = wb2.sheets()[0]
        
        ##check sht1a
        for pos in range(sht1a.nrows-1)[1:]:
            cas = sht1a.cell_value(rowx=pos, colx=1)
            ingName = sht1a.cell_value(rowx=pos, colx=2)
            fema = str(int(sht1a.cell_value(rowx=pos, colx=0)))
            
            if cas in self.cas_dict.keys():
                ingOptions = self.cas_dict[cas]['ing']
            else:
                ingOptions=[]
            if ingName not in ingOptions:
                ingOptions.append(ingName)  
            self.cas_dict[cas] = {'ing':ingOptions, 'fema':fema}
            
            if fema in self.fema_dict.keys():
                ingOptions = self.fema_dict[fema]['ing']
                casOptions = self.fema_dict[fema]['cas']
            else:
                ingOptions = []
                casOptions = []
            if ingName not in ingOptions:
                ingOptions.append(ingName)
            if cas not in casOptions:    
                casOptions.append(cas)
            self.fema_dict[fema] = {'cas': casOptions, 'ing': ingOptions}
            
            if ingName in self.ingredientName_dict.keys():
                casOptions = self.ingredientName_dict[ingName]['cas']
            else:
                casOptions = []
            if cas not in casOptions:
                casOptions.append(cas)
            self.ingredientName_dict[ingName]= {'cas':casOptions, 'fema':fema}
            
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
            
            if ingName in self.ingredientName_dict.keys():
                casOptions = self.ingredientName_dict[ingName]['cas']
            else:
                casOptions=[]
            if cas not in casOptions:
                casOptions.append(cas)
            self.ingredientName_dict[ingName] = {'cas':casOptions, 'fema': fema}
            
        #check sht2
        for pos in range(sht2.nrows-1)[2:1603]:                 ##length okay??????
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
        
#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}       
def findFlaws_casDict(ing, lookup, returnDict):
    dict_oneCas = lookup.lookup_by_cas(ing.cas)
    if ing.fema == '0' or ing.fema == '':
        if dict_oneCas['fema']!='unknown':       #we don't wnt to change empty fema numbers to 'unknown'
            ing.fema = dict_oneCas['fema']
            print "Fema number for cas number %s, previously blank, changed to %s" %(ing.cas,dict_oneCas['fema'])
            returnDict['changed_ings'].append([ing])
        else:
            print "Unknown Fema Number for ingredient with cas number %s"%ing.cas
            returnDict['unknownFema'].append(ing)
    elif (ing.fema != dict_oneCas['fema']):
        print "Disagreement of Fema Numbers for ingredient %s by cas_dict"%ing.product_name
        returnDict['disagreements'].append([ing, dict_oneCas['fema'], 'fema'])
    if ing.product_name not in dict_oneCas['ing']:
        #print "Disagreement of Ingredient Name for cas number %s"%ing.cas
        returnDict['disagreements'].append([ing, dict_oneCas['ing'], "Ingredient Name"])
    return returnDict

#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}  
def findFlaws_femaDict(ing, lookup, returnDict):
    dict_oneFema = lookup.lookup_by_fema(ing.fema)
    if ing.cas=='0':
        options=[]
        for cas in dict_oneFema['cas']:
            ing.cas = cas
            options.append(ing)
        returnDict['changed_ings'].append(options)
        print "Empty cas number can be one of the following %s"%dict_oneFema['cas']
    elif(ing.cas not in dict_oneFema['cas']):
        print "Disagreement of Cas Numbers for ingredient %s by fema_dict"%ing.product_name
        returnDict['disagreements'].append([ing, dict_oneFema['cas'], "Cas Number"])
    if ing.product_name not in dict_oneFema['ing']:
        #print "Disagreement of Ingredient Name for Fema Number %s"%ing.fema
        returnDict['disagreements'].append([ing, dict_oneFema['ing'], "Ingredient Name"])
    return returnDict

#inputs: ingredient, ProductLookup (group of dicts ^), {4 lists that classify cas/fema errors in DB}    
def findFlaws_nameDict(ing, lookup, returnDict):
    dict_oneName = lookup.lookup_by_name(ing.product_name) 
    if ing.cas=='0':
        options=[]
        for cas in dict_oneName['cas']:
            ing.cas = cas
            options.append(ing)
        returnDict['changed_ings'].append(options) 
    elif ing.cas not in dict_oneName['cas']:
        print "Disagreement of Cas Numbers for ingredient %s"%ing.product_name
        returnDict['disagreements'].append([ing, dict_oneName['cas'], "Cas Number"]) 
    if ing.fema=='0' or fema=='':
        if dict_oneName['fema']!='unknown':
            ing.fema = dict_oneName['fema']
            print "Fema number for ingredient %s, previously blank, changed to %s" %(ing.product_name, dict_oneName['fema'])
            returnDict['changed_ings'].append([ing])
        else:
            print "Unknown Fema Number for ingredient %s"%ing.product_name
            returnDict['unknownFema'].append(ing)                    
    elif ing.fema != dict_oneName['fema']:
        print "Disagreement of Fema Numbers for ingredient %s"%ing.product_name
        returnDict['disagreements'].append([ing, dict_oneName['fema'], "Fema Number"]) 
    return returnDict


def find_changes(path1, path2):
    lookup = ProductLookup(path1, path2)
    
    changed_ings = []
    disagreements = []
    no_info =[]
    unknownFema=[]
    returnDict={'changed_ings':changed_ings, 'disagreements':disagreements, 'no_info':no_info, 'unknownFema':unknownFema}
    ingredientz = Ingredient.objects.all()
    for ing in ingredientz:
        #if cas# is in cas_dict, verify fema and ingName
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
    
    ##return a dictionary including change options
    ## 'changes' is a list of lists. These sublists contain change options.
    return returnDict

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
                                     'error' : ''
                                     })
    return initialFormData

def initialFormData_errors(errorsList): 
    initialFormData=[]
    for ingPair in errorsList:
        ing = ingPair[0]
        error=ingPair[1]
        area = ingPair[2]
        initialFormData.append({
                                'Checkbox': False,
                                'ing_pk' : ing.pk,
                                'error' : "There is a disagreement between the %s, which should be %s"%(area,error),
                                'FEMA' : ing.fema,
                                'CAS' : ing.cas,
                                'ing_name' : ing.name
                                
                                })
def initialFormData(ingList):
    initialFormData = []
    for ing in ingList:
        initialFormData.append({
                                'Checkbox': False,
                                 'ing_pk' : ing.pk,
                                'FEMA' : ing.fema,
                                'CAS' : ing.cas,
                                'ing_name' : ing.name,
                                'error': ''
                                })
    return initialFormData



# 
# def initialFormData_preview_view(returnDict):
#     initialFormData_changes = []
#     initialFormData = []
#     for classification in returnDict.keys():
#         if classification == 'changed_ings':
#             for ingList in returnDict['changed_ings']:
#                 for ing in ingList:
#                     initialFormData_changes.append({
#                                             'classification': classification,
#                                             'Checkbox': False,
#                                             'ing_pk' : ing.pk,
#                                             'FEMA' : ing.fema,
#                                             'CAS' : ing.cas,
#                                             'ing_name' : ing.name,
#                                             'delete': False 
#                                             })
#         elif classification == 'errors':
#             pass
# #             for ingPair in returnDict['errors']:
# #                 ing = ingPair[0]
# #                 initialFormData.append({
# #                                         'classification': classification,
# #                                         'Checkbox': False,
# #                                         'ing_pk' : ing.pk,
# #                                         'FEMA' : ing.fema,
# #                                         'CAS' : ing.cas,
# #                                         'ing_name' : ing.name,
# #                                         'delete': False 
# #                                         })
#         else: 
#             for ing in returnDict[classification]:
#                 print type(ing)
#                 initialFormData.append({
#                                         'classification': classification,
#                                         'Checkbox': False,
#                                         'ing_pk' : ing.pk,
#                                         'FEMA' : ing.fema,
#                                         'CAS' : ing.cas,
#                                         'ing_name' : ing.name,
#                                         'delete': False
#                                          })         
#     return {'changes' : initialFormData_changes, 'other':initialFormData }  
#                 
#                 
                
                          
                
                                            



# #working with both spreadsheets to fill in all fema #s           
# def create_cas_fema_ing_dict(path1, path2):                        ##path2=label_changed.xls
#     wb1 = xlrd.open_workbook(path1)
#     sht1a = wb1.sheets()[1]
#     sht1b = wb1.sheets()[0]
#     wb2 = xlrd.open_workbook(path2)
#     sht2 = wb2.sheets()[0]
#       
#     #from path2 spreadsheet, has no fema #
#     dict = {}
#     for pos in range(sht2.nrows - 1)[2:]:
#         if sht2.cell_value(rowx=pos, colx=0) == '':
#             break
#         cas = sht2.cell_value(rowx=pos, colx=0)
#         ing = sht2.cell_value(rowx=pos, colx=2)
#         dict[ing] = cas
#     
#     #from path1 spreadsheet --> sht1a includes list of synonymous ing names    
#     cas_fema_ingredientNameOptions_dict={}
#     for pos in range(sht1b.nrows-1)[2:]:
#         cas = sht1b.cell_value(rowx=pos, colx=1)
#         ingName = sht1b.cell_value(rowx=pos, colx=2)
#         fema = sht1b.cell_value(rowx=pos, colx=0)
#         if cas in cas_fema_ingredientNameOptions_dict.keys():
#             ingOptions = cas_fema_ingredientNameOptions_dict[cas]['ing']     
#         else:
#             ingOptions = []      
#         ingOptions.append(ingName)
#         cas_fema_ingredientNameOptions_dict[cas] = {'ing': ingOptions, 'fema': fema}
#     
#     #checks cas and ingredients from path1
#     for ing in dict.keys():
#         if ing not in cas_fema_ingredientNameOptions_dict[cas]['ing']:
#             cas_fema_ingredientNameOptions_dict[cas] = {'ing':[ing], 'fema':'unknown'}
#             
#     #somehow, there's one cas# in "primary names only" but not in "primary names&synonyms
#     for pos in range(sht1a.nrows-1)[1:]:
#         cas = sht1a.cell_value(rowx=pos, colx=1)
#         if cas not in cas_fema_ingredientNameOptions_dict.keys():
#             ing = sht1a.cell_value(rowx=pos, colx=2)
#             fema = sht1a.cell_value(rowx=pos, colx=0)
#             cas_fema_ingredientNameOptions_dict[cas] = {'ing':[ing], 'fema':fema}
#         
#     return cas_fema_ingredientNameOptions_dict
            
    
           
    






