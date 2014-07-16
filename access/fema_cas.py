import xlrd



def create_CAS_FEMA_dict(path1):
    ##path1 is path to excel spread sheet with both the CAS and FEMA numbers
    ##path2 is the path to "IFRA/IOFI Labeling Manual 2013"
    workbook = xlrd.open_workbook(path1)
    sheet = workbook.sheets()[1]
    #workbook2 = xlrd.open_workbook(path2)
    #sheet2 = workbook2.sheets()[0]
    
    #get cell locations of FEMAs that have multiple instances
    ##WHYY????
#     loc_repeatedFEMAs = []
#     for pos in range(sheet.nrows - 1):
#         fema = sheet.cell_value(rowx=pos, colx=0)
#         next_fema = sheet.cell_value(rowx=pos+1, colx=0)
#         if fema == next_fema:
#             if pos not in loc_repeatedFEMAs:
#                 loc_repeatedFEMAs.append(pos)
#             if (pos+1) not in loc_repeatedFEMAs:
#                 loc_repeatedFEMAs.append(pos+1)
#             
    CAS_FEMA_dict = {}
    ##for pos in loc_repeatedFEMAs:
    for pos in range(sheet.nrows - 1)[1:]:               #excluding first row of headers.
        cas = sheet.cell_value(rowx=pos, colx=1)
        fema = sheet.cell_value(rowx=pos, colx=0)
        CAS_FEMA_dict[cas] = fema
        
    return CAS_FEMA_dict



def check_femas(path1):
    CAS_FEMA_dict=create_CAS_FEMA_dict(path1)
    
    for k,v in CAS_FEMA_dict.iteritems():
        ## This assigns a fema number to Ingredients with CAS#s but without a FEMA #
        ## It will print an error if the CAS,FEMA pair disagrees.
        ingredients =Ingredient.objects.filter(cas=k)
        for ing in ingredients:
            if float(ing.fema) != float(v):
                if ing.fema == '' or ing.fema== '0':
                    print "No previous fema information for CAS number %" %k + ". Fema number % filled in" %v
                    setattr(ing, 'fema', v)
                    ing.save()
                else:
                    ###INFORM THE USER THAT THERE IS A DISCREPANCY
                    print "Ingredients with the same CAS number (%s) have different FEMA numbers" %k
        ## If an ingredient has an empty cas number, but a fema number, it will assign a CAS number
        ingredients2 = Ingredient.objects.filter(fema=v)
        for ing in ingredients2:
            if ing.cas=='':
                print "fema number %" %v + " previously had no CAS number. It will be filled in with CAS number %" %k
                setattr(ing, 'cas', k)
                ing.save()
    for ing in Ingredient.objects.all():
        if ing.cas=='' and ing.fema == '':
            print "Ingredient: %s has no cas or fema information" %ing.product_name
                
                
            
    
    
        
            