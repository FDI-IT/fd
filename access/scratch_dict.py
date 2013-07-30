import pdb
from operator import itemgetter
from decimal import Decimal, ROUND_HALF_UP
from collections import deque, defaultdict
from datetime import datetime, date

from django.db import transaction
from django.db.models import Q, F, Sum
from django.conf import settings

from access.models import Flavor, Ingredient, Formula, FormulaTree, LeafWeight, FormulaException

INGREDIENT_FORMULA_ROW = 0
INGREDIENT_WEIGHT_FACTOR = 1
INGREDIENT_ROW_ID = 2
INGREDIENT_PARENT_ID = 3

INGREDIENT_ID = 0
WEIGHT = 1

GAZINTA_ID = 1


THOUSANDTHS = Decimal('1.000')
LOWER_BOUND = Decimal('999.0')
UPPER_BOUND = Decimal('1001.0')
ONE_HUNDRED = Decimal('100')
ONE_THOUSAND = Decimal('1000')
ZERO = Decimal('0')
SD_COST = Decimal('2.60')
test_flavor = Flavor.objects.get(number=9700)


def get_flavor_keyed_formulae(flavor_list=Formula.objects.filter(flavor__valid=True).values_list('flavor_id',flat=True).distinct()):
    flavor_keyed_formulae = {}
    for f in flavor_list:
        flavor_keyed_formulae[f] = Formula.objects.filter(flavor__id=f).values_list('ingredient_id','amount')
    return flavor_keyed_formulae

def get_gazinta_lookup(gazinta_list=Ingredient.objects.filter(sub_flavor__isnull=False).filter(sub_flavor__indivisible=False).values_list('pk','sub_flavor_id')):
    gd = {}
    for g in gazinta_list:
        gd[g[INGREDIENT_ID]] = g[GAZINTA_ID]
    return gd

fkf = get_flavor_keyed_formulae()
gd = get_gazinta_lookup()     

def get_exploded_weight(formula_row,weight_factor ):
    return formula_row[WEIGHT] * weight_factor



def has_children(ingredient_list, parent_id):
    """Like get_num_children, but it returns True as soon as one child
    is found.
    """
    for ingredient in ingredient_list:
        if ingredient[INGREDIENT_PARENT_ID] == parent_id:
            return True
    return False

@transaction.commit_manually
def test_build_tree():
    FormulaTree.objects.all().delete()
    for f in fkf.keys()[:500]:
        build_tree(f)
    transaction.commit()
    
def build_leaf_weights(flavor):
    cls = flavor.consolidated_leafs
    for i,w in cls.iteritems():
        lw = LeafWeight(root_flavor=flavor,
                        ingredient=i,
                        weight=w)
        lw.save()

    
@transaction.commit_manually
def test_build_lws():
    LeafWeight.objects.all().delete()
    for f in fkf.keys()[:500]:
        build_leaf_weights(Flavor.objects.get(pk=f))
    transaction.commit()

def build_tree(root_flavor_id):
    """Given a root_flavor model instance, construct a more sane tree-like
    representation of the formula of root_flavor. In order to see the formula
    for a flavor model instance, many recursive queries may have to be 
    executed (encapsulated in the Flavor model instance method 
    formula_traversal()). This function uses formula_traversal() to create
    a new data structure using FormulaTree model instances to represent a 
    formula using modified-preorder tree traversal in such a way that 
    recursive queries won't be required to analyze a formula.
    """
    # initializing special values for the root flavor
    formula_root = FormulaTree(
        root_flavor_id=root_flavor_id,
        lft=0,
        weight=1000,
        weight_factor=1,
        node_flavor_id=root_flavor_id,
        row_id=0,
    )
    # this value caches an ingredient lookup that we may have to do later on
    # it finds the corresponding ingredient record for a flavor
    # 'gazinta' is a named foreign key. all() should have a count of 0 or 1.
#    if root_flavor_id in gd:
#        formula_root.node_ingredient_id = gd[root_flavor_id]
#    else:
#        formula_root.node_ingredient = None
    # we get the whole ingredient list first, so that it can be sliced
    # when passed to get_num_children.
    # formula_traversal() is a model instance method that does all of the
    # recursive queries to analyze a formula. it returns a tuple that 
    # represents one line item of a formula. 
    ingredient_list = []
    for ingredient in complete_formula_traversal(root_flavor_id):
        ingredient_list.append(ingredient)
    
    # this stack holds nodes which have children because their rgt values
    # are not known until their children are visited.
    parent_stack = []
    parent_stack.append(formula_root)

    # i is the left/right number of a node in our tree. the root node has a
    # left number of ZERO and a right number of 2n-1 where n is the number of
    # nodes.
    # i is incremented in the following for loop, always immediately
    # after it's current value is needed, so that it's the correct value
    # for the next step of the algorithm
    i = 1
    for ingredient in ingredient_list:
        # if the ingredient's parent id does not match the row id of the
        # ingredient on the parent stack, then we've gone back up the tree
        # and need to assign rgt values to nodes that we missed
        look_at_parent_stack = True
        while(1):
            if look_at_parent_stack == False:
                break
            try:
                if ingredient[INGREDIENT_PARENT_ID] != parent_stack[-1].row_id:
                    last_parent = parent_stack.pop()
                    last_parent.rgt = i
                    i += 1
                    last_parent.save()
                else:
                    
                    look_at_parent_stack = False
            except IndexError:
                break
        
        formula_row = ingredient[INGREDIENT_FORMULA_ROW]

        row_id = ingredient[INGREDIENT_ROW_ID]
        if formula_row[INGREDIENT_ID] in gd:
            node_flavor_id = gd[ formula_row[INGREDIENT_ID] ]
        else:
            node_flavor_id = None
        # build node details that are independent of tree structure
        
        my_node = FormulaTree(
            root_flavor_id=root_flavor_id,
            weight_factor=ingredient[INGREDIENT_WEIGHT_FACTOR],
            row_id=row_id,
            parent_id=ingredient[INGREDIENT_PARENT_ID],
            node_ingredient_id=formula_row[INGREDIENT_ID],
            node_flavor_id=node_flavor_id,
            weight=get_exploded_weight(formula_row,ingredient[INGREDIENT_WEIGHT_FACTOR]).quantize(THOUSANDTHS, rounding=ROUND_HALF_UP),            
            lft=i,
        )

        i += 1
        
        if has_children(ingredient_list[row_id:], row_id):
            parent_stack.append(my_node)
        else:
            my_node.rgt = i
            i += 1
            my_node.leaf = True
            my_node.save()
        
    # flush parent_stack and assign rgt numbers
    parent_stack.reverse()
    for remaining_parent_node in parent_stack:
        remaining_parent_node.rgt = i
        i += 1
        remaining_parent_node.save()
        
    formula_root.rgt = i
    formula_root.save()
    
    
def complete_formula_traversal(root_flavor_id, weight_factor=Decimal(1), row_id=1, 
                               parent_id=0,):
    """Yields a tuple:
    (ingredient, weight_factor, row_id, parent_id)
    
    This is the complete method for traversing a formula. It will account
    for percentage yield, and spray dry costs to produce the final bill
    of materials and costs.
    """  
    def inner_traversal(flavor_id, weight_factor, row_id,
                        parent_id):
        for formula_row in fkf[flavor_id]:
            """If an ingredient is a gazinta, first the gazinta itself
            is yielded, then formula_traversal is called on all the sub-
            ingredients. Else, the ingredient is simply yielded, 
            because it has no subs.
            
            Each time the function yields, the row_id increments.
            """
            if formula_row[0] in gd:
                yield (formula_row, weight_factor, row_id, parent_id)
                row_id += 1
                
                gaz = gd[formula_row[0]]
                new_weight_factor = weight_factor*formula_row[1]/1000
                    
                for sub_ingredient in inner_traversal(
                                        gaz,
                                        new_weight_factor,
                                        row_id,
                                        row_id - 1):
                    yield sub_ingredient
                    row_id += 1     
            else:
                yield (formula_row, weight_factor, row_id, parent_id)
                row_id += 1
    
    row_id = 1
    parent_id = 0
    
    for ingredient in inner_traversal(root_flavor_id, weight_factor, row_id, parent_id):
        yield ingredient

class FormulaTreeBuilder:
    def __init__(self, formula_root_id):
        self.root = FormulaTree(
            root_flavor_id=formula_root_id,
            lft=0,
            weight=1000,
            weight_factor=1,
            node_flavor_id=formula_root_id,
            row_id=0,
        )
 
 
class MPTTNode:
    def __init__(self, parent, id, l, r):
        self.parent = parent
        self.id = id
        self.l = l
        self.r = r



