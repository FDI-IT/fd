import xlrd



def create_CAS_FEMA_dict(path1, path2):
    ##path1 is path to excel spread sheet with both the CAS and FEMA numbers
    ##path2 is the path to "IFRA/IOFI Labeling Manual 2013"
    workbook = xlrd.open_workbook(path1)
    sheet = workbook.sheets()[1]
    workbook2 = xlrd.open_workbook(path2)
    sheet2 = workbook2.sheets()[0]
    
    #get cell locations of FEMAs that have multiple instances
    loc_repeatedFEMAs = []
    for pos in range(sheet.nrows - 1):
        fema = sheet.cell_value(rowx=pos, colx=0)
        next_fema = sheet.cell_value(rowx=pos+1, colx=0)
        if fema == next_fema and fema:
            if pos not in loc_repeatedFEMAs:
                loc_repeatedFEMAs.append(pos)
        if (pos+1) not in loc_repeatedFEMAs:
            loc_repeatedFEMAs(pos+1)
            
    CAS_FEMA_dict = {}
    for pos in loc_repeatedFEMAs:
        cas = sheet.cell_value(rowx=pos, colx=1)
        fema = sheet.cell_value(rowx=pos, colx=0)
        CAS_FEMA_dict[cas] = fema
        
    return CAS_FEMA_dict


def check_femas(path1, path2):
    CAS_FEMA_dict=create_CAS_FEMA_dict(path1, path2)
    CAS_FEMA_dict[''] = 'Unknown'
    for k,v in CAS_FEMA_dict.iteritems():
        ingredients =Ingredient.objects.filter(cas=k)
        for ing in ingredients:
            if ing.fema != v:
                if ing.fema == '':
                    setattr(ing, 'fema', v)   ########????????????????
                    ing.save()
                else:
                    ###INFORM THE USER THAT THERE IS A DISCREPANCY
                    print "Ingredients with the same CAS number (%s) have different FEMA numbers" %k
    
    
    ##what id cas='' --> input corrext cas# from FEMA#
                
            
    
    
        
            