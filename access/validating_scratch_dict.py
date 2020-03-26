import pdb
from decimal import Decimal
from collections import defaultdict, deque
from datetime import datetime, date
from itertools import groupby

from django.db.models import Q, F, Sum
from django.db import transaction

from access.models import Flavor, Ingredient, Formula, FormulaTree, LeafWeight, FormulaException


thousandths = Decimal('1.000')
decimal_one = Decimal(1)


def xfunc(x):
    return x['flavor_id']

def dictify_formulae():
    """Returns a dict with keys equal to flavor_id and values equal to
    a list of their formulae items.
    """
    d = {}
    for k, g in groupby(Formula.objects.filter(flavor__valid=True).values(), xfunc):
        d[k]=list(g)
    return d

def dictify_gaz():
    """Returns a dict with keys equal to ingredient ids and values equal to
    corresponding sub_flavor_id
    """
    d={}
    for i in Ingredient.objects.all().select_related():
        if (i.flavornum != 0) and i.sub_flavor.valid==True:
            d[i.pk] = (i.sub_flavor_id, i.sub_flavor.yield_field)
    return d


def validate_everything():
    """Executes in multiple passes, first attempting to elimate flavors that
    are computationally easy to exclude.
    """    
    # first pass: has ingredients that add to 1000
    # also happens to initially define valid_flavors
    valid_flavors = set( Flavor.objects.annotate(tw=Sum('formula__amount')).filter(tw=1000).values_list('id',flat=True) )
 
    # using the values found in the first pass, key those ids to a list of
    # their formulae
    d = {}
    for k,g in groupby(Formula.objects.filter(flavor__id__in=valid_flavors).values(), xfunc):
        d[k]=list(g)
    
    g = dictify_gaz()
       
    # second pass: checking for cycles using a depth first search
    flavors_to_cycle = d.keys()
    contains_no_cycles = {} # if contains_no_cycle[x] == True, x has none
    
#    def check_contains_no_cycles(g_id):
#        if g_id in contains_no_cycles:
#            return contains_no_cycles[g_id]
#        else:
#            validty = validate(f)
#            contains_no_cycles[g_id] = validty
#            return validty
#            
#    def validate(f):
#        if f in contains_no_cycles:
#            return contains_no_cycles[f]
#        for fr in d[f]:
#            if fr['ingredient_id'] in g:
#                g_id, g_yf = g[fr['ingredient_id']]
#     
#                if g_id not in contains_no_cycles:
#                    flavors_to_cycle.remove(g_id)
#                    result = validate(g_id)
#                    contains_no_cycles[g_id] = result
#                    if result == True:
#                        continue
#                    else:
#                        contains_no_cycles[f] = False
#                        return False
#        return True

    def validate(f,parent_list):
        if f in parent_list:
            handle_bad_list(parent_list)
        else:
            parent_list.append(f)
            for fr in d[f]:
                if fr['ingredient_id'] in g:
                    g_id, g_yf = g[fr['ingredient_id']]
                    if g_id in contains_no_cycles:
                        if contains_no_cycles[g_id] == True:
                            continue
                        else:
                            handle_bad_list(parent_list)
                            return False
                    else:
                        my_list = parent_list[:]
                        result = validate(g_id, my_list)
                        if result == False:
                            return False
                        
                
            contains_no_cycles[f] = True
            return True
                        
    def handle_bad_list(bad_list):
        """If we have a list of bad flavors, remove them from the queue
        and mark them false in contains_no_cycles.
        """
        for bad_f in bad_list:
            contains_no_cycles[bad_f] = False
            if bad_f in flavors_to_cycle:
                flavors_to_cycle.remove(bad_f)
                contains_no_cycles[bad_f] = False
                

    while(True):
        try:
            f = flavors_to_cycle.pop()
        except:
            break
        print f
        validate(f,[])
                    
    
    
    return contains_no_cycles
    
    # second pass: look for cycles.
    
    



#this is fast but weight isn't calculated yet just wf.
def traverse(d, gzs, k, wf, ):
    formula = []
    #print "Traversing %s..." % k
    for ingredient in d[k]:
        i = ingredient.copy()
        #print i
        if i['ingredient_id'] in gzs:
            g_id, g_yf = gzs[i['ingredient_id']] # the id and the yield field
            print g_yf
            new_wf = wf*(i['amount']/1000)
            print new_wf
            formula.extend(traverse(d, gzs, g_id, new_wf))
        else:
            i['amount'] = i['amount'] * wf
            formula.append(i)
    return formula
#
#
#class dictify_scanner:
#    g = dictify_gaz()
#    d = dictify_formulae()
#    
#    def traverse(self, k, wf, ):
#        formula = []
#        #print "Traversing %s..." % k
#        for ingredient in self.d[k]:
#            #i['wf'] = wf
#            i = ingredient.copy()
#            #print i
#            if i['ingredient_id'] in self.g:
#                g_id, g_yf = self.g[i['ingredient_id']] # the id and the yield field
#                print g_yf
#                new_wf = wf*(i['amount']/1000)
#                print new_wf
#                formula.extend(traverse(g_id, new_wf))
#            else:
#                i['amount'] = i['amount'] * wf
#                formula.append(i)
#        return formula
#    
#    def build_tree(self, root_flavor_id):
#        formula_root = FormulaTree(
#            root_flavor=root_flavor_id,
#            lft=0,
#            weight=1000,
#            weight_factor=1,
#            node_flavor=root_flavor_id,
#            row_id=0,
#        )
#        
#        if root_flavor_id in self.g:
#            formula_root.node_ingredient_id = self.g[root_flavor_id]
#        else:
#            formula_root.node_ingredient = None
#        
#        ingredient_list = []
#        for ingredient in root_flavor.complete_formula_traversal():
#            ingredient_list.append(ingredient)
