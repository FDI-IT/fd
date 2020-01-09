import pdb
from decimal import Decimal, ROUND_HALF_UP
from collections import deque

from django.db.models import Q, F

from access.models import Flavor, Ingredient, Formula, FormulaTree


class FormulaLite():
    def __init__(self, fr, weight_factor=1):
        self.flavor = fr.flavor
        self.flavor_number = self.flavor.number            
            
def find_usage(ingredient_pk, gazinta_lists, flavor_valid):
    ingredient = Ingredient.objects.get(pk=ingredient_pk)
    # edge_check = set()
    usage = {}
    formula_queue = deque()
            
    for fr in ingredient.formula_set.values('flavor_id','amount'):
        formula_queue.append(fr)
    
    i = 0
    l = len(formula_queue)
    while(formula_queue):
        i += 1
        print("iter count: %s | queue length: %s" % (i, l))
                
        fr = formula_queue.popleft()
        l -= 1
        
        
        flavor_id = fr['flavor_id']
        if flavor_id not in flavor_valid:
            continue
        try:
            usage[flavor_id].append(fr)
        except KeyError:
            usage[flavor_id] = [fr]

        # YOU KEEP MODIFYING THE SAME OBJS! stop it
        for new_fr in gazinta_lists.get(flavor_id,()):
            my_new_fr = new_fr.copy()
            my_new_fr['amount'] *= fr['amount'] / 1000
#            edge = (flavor_id, new_flavor_id)
#            if edge in edge_check:
#                continue
#            else:
#                edge_check.add(edge)
    
            formula_queue.append(my_new_fr)
            l += 1
            
    return usage

def update_cost(usage, delta):
    flavor_deltas = {}
    for f_id, ing_list in usage.items():
        sum = 0
        for x in ing_list:
            sum += x['amount']
        flavor_deltas[f_id] = sum * delta / 1000
    return flavor_deltas

def get_usage_and_update_cost(ingredient_pk, gazinta_lists, flavor_valid, delta):
    u = find_usage(ingredient_pk, gazinta_lists, flavor_valid)
    return update_cost(u, delta)

def get_children(ingredient_list, parent_id):
    """Given a parent id, return the rows in ingredient_list that have
    that parent_id. Typically a slice of ingredient_list is passed in 
    that does not include nodes closer to the root.
    """
    children = []
    for ingredient in ingredient_list:
        if ingredient[3] == parent_id:
            children.append(ingredient)
    return children

def build_tree(root_flavor):
    """Given a flavor, build the corresponding FormulaTree rows using
    Formula rows.
    """
    thousandths = Decimal('1.000')
    formula_root = FormulaTree(root_flavor=root_flavor)
    formula_root.lft = 0
    formula_root.weight = 1000
    formula_root.weight_factor = 1
    formula_root.node_flavor = root_flavor
    formula_root.row_id = 0
    try:
        formula_root.node_ingredient = root_flavor.gazinta.all()[0]
    except:
        pass
    
    # we get the whole ingredient list first, so that it can be sliced
    # when passed to get_children.
    ingredient_list = []
    for ingredient in root_flavor.formula_traversal():
        ingredient = list(ingredient)
        ingredient_list.append(ingredient)
    
    # i is incremented twice in the following for loop, always immediately
    # after it's current value is needed, so that it's the correct value
    # for the next step of the algorithm
    i = 1
    
    # this stack holds nodes which have children because their rgt values
    # are not known until their children are visited.
    parent_stack = []
    parent_stack.append(formula_root)
    
    #import pdb; pdb.set_trace()
    
    for ingredient in ingredient_list:
        # if the ingredient's parent id does not match the row id of the
        # ingredient on the parent stack, then we've gone back up the tree
        # and need to assign rgt values to nodes that we missed
        try:
            if ingredient[3] != parent_stack[-1].row_id:
                last_parent = parent_stack.pop()
                last_parent.rgt = i
                i += 1
                last_parent.save()
        except IndexError:
            pass
        
        # build node details that are independent of tree structure
        my_node = FormulaTree(root_flavor=root_flavor)
        my_node.row_id = ingredient[2]
        my_node.parent_id = ingredient[3]
        my_node.formula_row = ingredient[0]
        my_node.node_ingredient = ingredient[0].ingredient # not normalized, but probably saves an extra lookup
        my_node.node_flavor = ingredient[0].gazinta()
        my_node.weight = ingredient[0].get_exploded_weight(ingredient[1]).quantize(thousandths)
        my_node.weight_factor = ingredient[1]
        
        # assign lft and look at the children
        my_node.lft = i
        children = get_children(ingredient_list[ingredient[2]:], ingredient[2])
        i += 1
        if len(children) > 0:
            parent_stack.append(my_node)
        else:
            my_node.rgt = i
            i += 1
            my_node.save()
        
    # flush parent_stack and assign rgt numbers
    parent_stack.reverse()
    for remaining_parent_node in parent_stack:
        remaining_parent_node.rgt = i
        i += 1
        remaining_parent_node.save()
        
    formula_root.rgt = i
    formula_root.save()
    
    

"""
the below functions are all wrong because they are copied from the Flavor
model, before FormulaTree was modified to actually store a node explicitly
for the root flavor.
"""
def leaf_nodes(flavor):
    return FormulaTree.objects.filter(root_flavor=flavor).filter(rgt=F('lft') + 1)

def root_nodes(flavor):
    return FormulaTree.objects.filter(root_flavor=flavor).filter(parent_id=0)

def sum_nodes(nodes):
    sum = 0
    for n in nodes:
        sum += n.weight
    return sum

def analyze_subtrees(flavor):
    child_weights = {}
    parent_weights = {}
    nodes = FormulaTree.objects.filter(root_flavor=flavor).values('parent_id', 'row_id', 'weight')
    
    for node in nodes:
        try:
            child_weights[node['parent_id']] += node['weight']
        except:
            child_weights[node['parent_id']] = node['weight']
    del child_weights[None]
            
    for node in nodes:
        if node['row_id'] in child_weights:
            parent_weights[node['row_id']] = node['weight']
            
    return child_weights, parent_weights

def subtree_match(flavor):
    lhs, rhs = analyze_subtrees(flavor)
    return lhs == rhs
    
def find_characteristic_wrong_subtree():
    last_comparer = 1000
    for flavor in Flavor.objects.filter(valid=True):
        print(flavor)
        nodes = FormulaTree.objects.filter(root_flavor=flavor)
        if subtree_match(flavor):
            pass
        else:
            c = nodes.count()
            print(c)
            if nodes.count() < last_comparer:
                last_bad = flavor
                
    return last_bad 
            
    
    
    
    
    
    
    
    

#
#def find_usage(ingredient):
#    debug = False
#    specific_usages = {}
#    test_flavor = Flavor.objects.get(number=110805)
##    for gazinta, amount, row_id, parent_id in ingredient.gzl_traversal():
#    for gz in ingredient.gzl_traversal():
#        gazinta = gz[0]
#        if debug and gazinta == test_flavor:
#            pdb.set_trace()
#        try:
#            specific_usages[gazinta] = specific_usages[gazinta] + gz[1]
#        except:
#            specific_usages[gazinta] = gz[1]
#        
#    return specific_usages
#    visited_flavors = {}
#    formula_queue = []
#    for fr in ingredient.formula_set.all():
#        formula_queue.append(fr)
#    for fr in formula_queue:
#        my_flavor = fr.flavor
#        if not my_flavor.valid:
#            continue
#        if my_flavor in visited_flavors:
#            continue
#        else:
#            visited_flavors[my_flavor] = 1
#        my_key = my_flavor
#        try:
#            total_usage[my_key] = total_usage[my_key] + fr.amount
#        except:
#            total_usage[my_key] = fr.amount
#        
#        try:
#             for new_fr in my_flavor.gazinta.all()[0].formula_set.all():
#                 #print "before: %s" % new_fr
#                 new_fr.amount *= fr.amount / 1000
#                 #print "after: %s" % new_fr
#                 formula_queue.append(new_fr)
#        except:
#            pass
#        
#    return total_usage