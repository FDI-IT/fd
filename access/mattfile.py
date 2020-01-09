from django.db import models
from decimal import Decimal
from access.models import Formula, Flavor, Ingredient


def CalculateAllCosts(flavor_list):
    
    #validFlavors = Flavor.objects.filter(valid=True)
    
    for x in flavor_list:
        new_costs = calculateCost(flav = x)
        
    return new_costs
        
    
def calculateCost(flav, checklist = None, saved_flavors = {}):
      
    if flav.number in saved_flavors:
        return saved_flavors 
    
    if checklist is None:
        checklist = []
    
    if flav.valid == False:
        raise ValidityError('Flavor number %s is invalid.' % flav.number)
        
    total_cost = 0;
    
    if flav.number in checklist:
        #error stuff
        checklist.append(flav.number)
        first_index = checklist.index(flav.number)
        cycle_list = checklist[first_index:] #cycle_list removes the unnecessary product numbers from checklist
        cycle_list = list(map(str, cycle_list))  #turns all the integers into strings (to prepare for concatenation)
        checklist_str = ", ".join(cycle_list)  #join cycle_list into one string
        
        raise CycleError('Product number %s is an ingredient of itself.  The following cycle occurs: \n %s' % (flav.number, checklist_str))
        
    else:
        #append number to checklist
        checklist.append(flav.number)
        
    #get all formulas where flav is root, this list should never be empty
    #because all valid flavors will have a formula
    ingredient_list = Formula.objects.filter(flavor = flav)
    
    for x in ingredient_list:
        
        amt = x.amount
            
        if x.ingredient.sub_flavor is None: #ingredient is lowest-level
            cost = x.ingredient.unitprice            
        else: #ingredient is a flavor
            cost_dict = calculateCost(flav = x.ingredient.sub_flavor, checklist = checklist, saved_flavors = saved_flavors)
            saved_flavors.update(cost_dict)
            cost = cost_dict[x.ingredient.sub_flavor.number]
            
        weighted_cost = cost*amt/1000
        total_cost += weighted_cost
    
    #if cost_dict is not None:
    #   saved_flavors.update(cost_dict)
    
    #if flav.number not in saved_flavors:
    saved_flavors[flav.number] = total_cost        
    
    checklist.remove(flav.number)
    
    return saved_flavors
            
def updateValidity():
    
    totalAmount = 0
    
    distinctRoots = []
    allFormulas = Formula.objects.all()
    
    #add all distinct root flavors to distinctRoots
    for x in allFormulas:
        if x.flavor.number not in distinctRoots:
            distinctRoots.append(x.flavor.number)
    
    #for every distinct root, set valid to false
    for x in distinctRoots:
        flav = Flavor.objects.get(number = x)
        flav.valid = False
        
        #get all formulas where flav is root
        ingredient_list = Formula.objects.filter(flavor = flav)
            
        #sum the amounts, and if sum is 1000, set valid to true (for that flavor)
        for x in ingredient_list:
            totalAmount += x.amount
            
        if totalAmount == 1000:
            flav.valid = True
            
class CycleError(Exception):
    pass

class ValidityError(Exception):
    pass
