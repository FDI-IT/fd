import pdb
from operator import itemgetter
from decimal import Decimal, ROUND_HALF_UP
from collections import deque, defaultdict
from datetime import datetime, date
import copy
from reversion import revision
from django.db import transaction
from django.db.models import Q, F, Sum
from django.conf import settings
from django.db import connection
import operator
from access.models import Flavor, Ingredient, Formula, FormulaTree, LeafWeight, IndivisibleLeafWeight, FormulaException, DIACETYL_PKS, PG_PKS, SOLVENT_NAMES
ones = Decimal('1')
tenths = Decimal('0.0')
hundredths = Decimal('0.00')
thousandths = Decimal('0.000')
ONE_THOUSAND = Decimal('1000')
ONE_HUNDRED = Decimal('100')
TEN = Decimal('10')
        
INGREDIENT_FORMULA_ROW = 0
INGREDIENT_WEIGHT_FACTOR = 1
INGREDIENT_ROW_ID = 2
INGREDIENT_PARENT_ID = 3

THOUSANDTHS = Decimal('1.000')
LOWER_BOUND = Decimal('999.0')
UPPER_BOUND = Decimal('1001.0')
TEN = Decimal('10')
ONE_HUNDRED = Decimal('100')
ONE_THOUSAND = Decimal('1000')
ZERO = Decimal('0')
SD_COST = Decimal('2.60')


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
        print "iter count: %s | queue length: %s" % (i, l)
                
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
    for f_id, ing_list in usage.iteritems():
        sum = 0
        for x in ing_list:
            sum += x['amount']
        flavor_deltas[f_id] = sum * delta / 1000
    return flavor_deltas

def get_usage_and_update_cost(ingredient_pk, gazinta_lists, flavor_valid, delta):
    u = find_usage(ingredient_pk, gazinta_lists, flavor_valid)
    return update_cost(u, delta)

def get_num_children(ingredient_list, parent_id):
    """Given a parent id, return the rows in ingredient_list that have
    that parent_id. Typically a slice of ingredient_list is passed in 
    that does not include nodes closer to the root.
    """
    num_children = 0
    #print "PARENT ID: %s" % parent_id
    for ingredient in ingredient_list:
        # print ingredient[3]
        if ingredient[3] == parent_id:
            num_children += 1
    
    return num_children

@transaction.commit_manually
def build_tree(root_flavor):
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
        root_flavor=root_flavor,
        lft=0,
        weight=1000,
        weight_factor=1,
        node_flavor=root_flavor,
        row_id=0,
    )
    # this value caches an ingredient lookup that we may have to do later on
    # it finds the corresponding ingredient record for a flavor
    # 'gazinta' is a named foreign key. all() should have a count of 0 or 1. 
    try:
        formula_root.node_ingredient = root_flavor.gazinta.all()[0]
    except IndexError:
        formula_root.node_ingredient = None
    
    # we get the whole ingredient list first, so that it can be sliced
    # when passed to get_num_children.
    # formula_traversal() is a model instance method that does all of the
    # recursive queries to analyze a formula. it returns a tuple that 
    # represents one line item of a formula. 
    ingredient_list = []
    for ingredient in root_flavor.complete_formula_traversal():
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
        weight_factor = ingredient[INGREDIENT_WEIGHT_FACTOR]
        row_id = ingredient[INGREDIENT_ROW_ID]
        parent_id = ingredient[INGREDIENT_PARENT_ID]
        node_ingredient=formula_row.ingredient
        
        # build node details that are independent of tree structure       
        my_node = FormulaTree(
            root_flavor=root_flavor, 
            formula_row=formula_row, 
            weight_factor=weight_factor,
            row_id=row_id,
            parent_id=parent_id,
            node_ingredient=node_ingredient,
            node_flavor=node_ingredient.gazinta(),
            weight=formula_row.get_exploded_weight(weight_factor).quantize(THOUSANDTHS, rounding=ROUND_HALF_UP),            
            lft=i,
        )

        i += 1
        
        if get_num_children(ingredient_list[row_id:], row_id) > 0:
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
    transaction.commit()
    
def build_trees(flavors, start, end):
    x = start
    while (x < end):
        f = flavors[x]
        
        build_tree(f)
        x += 1
        


def test_gc():
    import gc
    print gc.collect()
    print gc.collect()
    SAMPLE_SIZE = 1000
    flavors = Flavor.objects.filter(valid=True)
    
    start = 0
    end = 2
    
    while (start < SAMPLE_SIZE):
        print " ****************************************** "
        print "Start: %s, End: %s" % (start, end)
        build_trees(flavors, start, end)
        start = end + 1
        end = end * 2
        print gc.collect()
         
    
    
def build_all_trees():
    FormulaTree.objects.all().delete()
    for f in Flavor.objects.filter(valid=True):
        print f
        build_tree(f)
    
def prep_test():
    LeafWeight.objects.all().delete()
    FormulaTree.objects.all().delete()
        
def test_slice():
    flavors = Flavor.objects.filter(valid=True).filter(name__icontains="lor")
    for f in flavors:
        print f
        build_tree(f)
    for f in flavors:
        print f
        build_leaf_weights(f)
        

        
def synchronize_price(f, verbose=False):
    if verbose:
        print f
    rmc = 0
    lastspdate = datetime(1990,1,1)
    for leaf in f.leaf_weights.all():
        sub_flavor = leaf.ingredient.sub_flavor
        adjustment = 1
        if sub_flavor is not None:
            y = ONE_HUNDRED.__copy__()
            y = sub_flavor.yield_field
            
            if y == 0:
                y = 100
            
            adjustment = y/ONE_HUNDRED
            if adjustment == ZERO:
                adjustment = 1
        
        cost_diff = leaf.weight * leaf.ingredient.unitprice / adjustment
        rmc += cost_diff
        if verbose:
            print '"%s","%s","%s"' % (leaf.ingredient.id, leaf.ingredient.product_name, cost_diff)
        ing_ppu = leaf.ingredient.purchase_price_update
        if lastspdate < ing_ppu:
            lastspdate = ing_ppu
    
    y = ONE_HUNDRED.__copy__()
    
    y = f.yield_field
    
    adjustment = y/ONE_HUNDRED
    if adjustment == ZERO:
        adjustment = 1
    # print adjustment
    if f.spraydried:
        f.rawmaterialcost = rmc / 1000 / adjustment + SD_COST
    else:
        f.rawmaterialcost = rmc / 1000 / adjustment
    f.lastspdate = lastspdate
    f.save()
        
def synchronize_all_prices():
    sd_price = Decimal('2.90')
    update_time = datetime.now()
    for f in Flavor.objects.select_related().filter(valid=True):
        synchronize_price(f)
        

"""
the below functions are all wrong because they are copied from the Flavor
model, before FormulaTree was modified to actually store a node explicitly
for the root flavor.
"""
def leaf_nodes(flavor):
    return FormulaTree.objects.filter(root_flavor=flavor).filter(rgt=F('lft') + 1)

def root_nodes(flavor):
    return FormulaTree.objects.filter(root_flavor=flavor).filter(parent_id=0)

def leaf_node_tester():
    ceil = Decimal('1000.01')
    floor = Decimal('999.99')
    for f in Flavor.objects.filter(valid=True):
        sum = 0
        
        for leaf in leaf_nodes(f):
            sum += leaf.weight
            
        if sum > ceil or sum < floor:
            print "%s -- %s" % (f, sum)

def consolidated_leafs(flavor):
    leaf_ingredients = leaf_nodes(flavor)
    cons_leafs = {}
    for leaf in leaf_ingredients:
        cons_leafs[leaf.node_ingredient] = cons_leafs.get(leaf.node_ingredient, 0) + leaf.weight
        
    return cons_leafs

def build_leaf_weights(flavor):
    cls = flavor.consolidated_leafs
    for i,w in cls.iteritems():
        lw = LeafWeight(root_flavor=flavor,
                        ingredient=i,
                        weight=w)
        lw.save()
        
def build_all_leaf_weights(): 
    LeafWeight.objects.all().delete()
    bad_total_flavors = []
    for f in Flavor.objects.filter(valid=True):
        print f
        try:
            build_leaf_weights(f)
        except FormulaException:
            bad_total_flavors.append(f)
    print "bad total flavors"
    print bad_total_flavors


        
def build_indivisible_leaf_weights(flavor):
    indivisible_leafs = flavor.consolidated_indivisible_leafs
    for i, w in indivisible_leafs.iteritems():
        ilw = IndivisibleLeafWeight(root_flavor=flavor,
                                   ingredient=i,
                                   weight=w)
        ilw.save()

def build_all_indivisible_leaf_weights():
    IndivisibleLeafWeight.objects.all().delete()
    bad_total_flavors = []
    for f in Flavor.objects.filter(valid=True):
        print f
        try:
            build_indivisible_leaf_weights(f)
        except FormulaException:
            bad_total_flavors.append(f)
        print "finished"
    print "bad_total_flavors"
    print bad_total_flavors

def deep_flavor_search():
    formulas = {}
    formulas_by_length = defaultdict(list)
    formula_pairs = []
    for f in Flavor.objects.filter(valid=True):
        print f
        formula = LeafWeight.objects.filter(root_flavor=f).values_list('ingredient_id','weight').order_by('ingredient__pk')
        formula_len = len(formula)
        formulas_by_length[formula_len].append(f)
        formulas[f] = formula
        
    for k, v in formulas_by_length.iteritems():
        print k
        v = sorted(v, key=lambda f: formulas[f][0])
        formulas_by_length[k]=v
        for i in range(0, len(v)-2):
            print v[i]
            lf = formulas[v[i]]
            rf = formulas[v[i+1]]
            formula_match = True
            for j in range(0, k-1):
                if lf[j] == rf[j]:
                    print "match: %s" % repr(lf[j])
                else:
                    formula_match = False
                    break
            if formula_match:
                formula_pairs.append((v[i], v[i+1]))
    
    
    return (formulas, formulas_by_length, formula_pairs)    
    # find all the formulae that are the same length
    # find all the formulae that start with the same ingredient
    # find the ones that are the same length and start with the same ingredient
    
    # return formulas

def dfs_sanity_check():
    weird_flavors = []
    for f in Flavor.objects.filter(valid=True):
        if f.formula_set.all().count() == 1:
            if f.productmemo[:7] != "Same as":
                print "%s: %s" % (f, f.productmemo)
                ing = f.formula_set.all()[0]
                print ing.gazinta()
                weird_flavors.append(f)
                
    return weird_flavors
    

# check the ith ingredient of formula
# for each formula of length x:
#    for i=0,x:
#        
#    for i=1,max_formula_length:
#        repartitioned_list = []
#        for sub_list in formulas_by_len[i]:
#        sub_list is the list of all formulas that share the same length i
#                

def same_len_formula_search(formulas):
    """Given a list of formulas of the same length, sorted in ascending
    order of ingredient__pk, compare them ingredient by ingredient
    to find formulas that are the same.
    """
    return

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

def degree_of_error(flavor):
    """Returns the sum of the (absolute) differences between leaf nodes and
    root nodes.
    """
    child_weights, parent_weights = analyze_subtrees(flavor)
    child_keys = set(child_weights.keys())
    parent_keys = set(parent_weights.keys())
    
    if child_keys != parent_keys:
        import pdb; pdb.set_trace()
    
    error = 0
    for k in child_keys:
        error += abs(child_weights[k] - parent_weights[k])
        
    error = int(error*1000)
    return error

def subtree_match(flavor):
    lhs, rhs = analyze_subtrees(flavor)
    return lhs == rhs
    
def find_characteristic_wrong_subtree():
    last_comparer = 1000
    for flavor in Flavor.objects.filter(valid=True):
        # print flavor
        nodes = FormulaTree.objects.filter(root_flavor=flavor)
        if subtree_match(flavor):
            pass
        else:
            c = nodes.count()
            # print c
            if nodes.count() < last_comparer:
                last_bad = flavor
                
    return last_bad 

    
def get_complete_ingredient_list(flavor):
    ingredients = {}
    for node in leaf_nodes(flavor):
        try:
            ingredients[node.node_ingredient] += node.weight
        except:
            ingredients[node.node_ingredient] = node.weight
            
    return ingredients
    
    
def make_current_cost_update():
    now = datetime.now()
    def cost_update(flavor):
        total_rmc = 0
        for formula_row in flavor.formula_set.all():
            ingredient = formula_row.ingredient
            g = ingredient.gazinta()
            if g:
                if g.lastspdate == now:
                    ingredient_rmc = g.yield_adjusted_rmc * formula_row.amount
                else:
                    ingredient_rmc = cost_update(g) * formula_row.amount
            else:
                ingredient_rmc = ingredient.unitprice * formula_row.amount
            total_rmc += ingredient_rmc
        
        flavor.rawmaterialcost = total_rmc / ONE_THOUSAND
        flavor.lastspdate = now
        flavor.save()
        return flavor.yield_adjusted_rmc
    return cost_update

    
def update_all_costs(verbose=False):
    """
    Add up all the weighted costs of the ingredients to find unit cost of
    flavor.
    
    Does the flavor have any stale gazintas?
        Recursively update gazintas
    Else:
        Add all the weighted costs of ingredients.
        Set the last price update.
        Save the flavor.
        
    Let's try the closure make_current_cost_update, defined above
    """
    flavors_updated = {}
    
    def make_current_cost_update():
        now = datetime.now()
        def cost_update(flavor):
            if flavor in flavors_updated:
                return flavors_updated[flavor.id]
            if verbose:
                print flavor
            total_rmc = 0
            for formula_row in flavor.formula_set.all():
                ingredient = formula_row.ingredient
                g = ingredient.gazinta()
                if g:
                    if g.id in flavors_updated:
                        ingredient_rmc = flavors_updated[g.id] * formula_row.amount
                    else:
                        if g.lastspdate == now:
                            ingredient_rmc = g.yield_adjusted_rmc * formula_row.amount
                        else:
                            ingredient_rmc = cost_update(g) * formula_row.amount
                else:
                    ingredient_rmc = ingredient.unitprice * formula_row.amount
                total_rmc += ingredient_rmc
            
            flavor.rawmaterialcost = total_rmc / ONE_THOUSAND
            flavor.lastspdate = now
            flavor.save()
            yarmc = flavor.yield_adjusted_rmc
            flavors_updated[flavor.id] = yarmc
            return yarmc
        return cost_update
    
    
    
    cost_update = make_current_cost_update()
    for flavor in Flavor.objects.filter(valid=True):
        cost_update(flavor)
        

def test():
    build_all_trees()
    build_all_leaf_weights()
     
aller_attrs = [
        'crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
    ]

aller_query = [
        'crustacean',
        'eggs',
        'fish',
        'milk',
        'peanuts',
        'soybeans',
        'treenuts',
        'wheat',
        'sunflower',
        'sesame',
        'mollusks',
        'mustard',
        'celery',
        'lupines',
        'yellow_5',
    ]

i_aller_dict = { 
 u'Yes-Cereals (Gluten)': 'wheat',
 u'Yes-Crustacean Shellfish': 'crustacean',
 u'Yes-Crustaceans': 'crustacean',
 u'Yes-Eggs': 'eggs',
 u'Yes-Fish': 'fish',
 u'Yes-Milk': 'milk',
 u'Yes-Peanuts': 'peanuts',
 u'Yes-Peanuts/Legumes': 'peanuts',
 u'Yes-Soy/Legumes': 'soybeans',
 u'Yes-Soybeans': 'soybeans',
 u'Yes-Sulfites': 'sulfites',
 u'Yes-Tree Nuts': 'treenuts',
 u'Yes-Wheat(Gluten)': 'wheat',}

aller_dict = {
    u'': None,
    u'Non': None,
    u'None': None,
    u'Yes-Cereals (Gluten)': 'wheat',
    u'Yes-Crustacean Shellfish': 'crustacean',
    u'Yes-Crustaceans': 'crustacean',
    u'Yes-Eggs': 'eggs',
    u'Yes-Fish': 'fish',
    u'Yes-Milk': 'milk',
    u'Yes-Multiple-see comments': "CHECK ALLERGENS.",
    u'Yes-Peanuts': 'peanuts',
    u'Yes-Peanuts/Legumes': 'peanuts',
    u'Yes-Seeds': 'sesame',
    u'Yes-Soy/Legumes': 'soybeans',
    u'Yes-Soybeans': 'soybeans',
    u'Yes-Sulfites': 'sulfites',
    u'Yes-Tree Nuts': 'treenuts',
    u'Yes-Wheat(Gluten)': 'wheat',
    u'no': None,
    u'none': None,
    u'yes': "CHECK ALLERGENS.",
    u'CHECK ALLERGENS.': "CHECK ALLERGENS."}
#setattr(model_instance,
#                        model_field.attname,
#                        parsed_csv_field)
    
def set_allergen_bools_from_text_field():
    for i in Ingredient.objects.all():
        if i.allergen in aller_dict:
            allergen_value = aller_dict[i.alergen]
            mutated = False
            if allergen_value is "CHECK ALLERGENS.":
                i.allergen = "CHECK ALLERGENS."
                mutated = True
            if allergen_value is None and verify_none_allergens(i):
                i.allergen = ""
                i.has_allergen_text = False
                mutated = True
            
            #setattr(i,i_aller_dict[i.allergen],True)
            
            if mutated:
                i.save()

def verify_none_allergens(i):
    # return True if all allergen bools are False
    for aller in aller_attrs:
        if getattr(i, aller) is True:
            return False
    return True

def verify_single_allergens(i, allergen):
    # return False if more than the indicated allergen text is checked
    for aller in aller_attrs:
        if aller==allergen:
            if getattr(i,aller) is False:
                return False
        else:
            if getattr(i, aller) is True:
                return False
    return True 
@transaction.commit_manually
def parse_ingredient_allergens():
    cursor = connection.cursor()
    cursor.execute("UPDATE access_integratedproduct SET crustacean=false, eggs=false, fish=false, milk=false, peanuts=false, soybeans=false, treenuts=false, wheat=false, sunflower=false, sesame=false,mollusks=false,mustard=false,celery=false,lupines=false,yellow_5=false,allergen='NONE';")
    allergenic_flavors = []
    for allergen in aller_attrs:
        print allergen
        for i in Ingredient.objects.filter(**{allergen:True}):
            print i
            for lw in LeafWeight.objects.filter(ingredient=i).select_related():
                print lw.root_flavor
                setattr(lw.root_flavor, allergen, True)
                lw.root_flavor.save()
                allergenic_flavors.append(lw.root_flavor)
                
    for allergenic_flavor in allergenic_flavors:
        print allergenic_flavor
        flavor_allergens = []
        for allergen in aller_attrs:
            if getattr(allergenic_flavor, allergen):
                flavor_allergens.append(allergen)
        allergenic_flavor.allergen = "Yes: %s" % ','.join(flavor_allergens)
        allergenic_flavor.save()
    
    transaction.commit()
    
@transaction.commit_manually
def parse_rm_allergens():
    for i in Ingredient.objects.all():
        i_allergens = []
        for allergen in aller_attrs:
            if getattr(i, allergen):
                i_allergens.append(allergen)
        if len(i_allergens) > 0:
            i.allergen = "Yes: %s" % ','.join(i_allergens)
        else:
            i.allergen = "None"
        i.save()
    transaction.commit()
        
    
@transaction.commit_manually
def parse_sulfites():
    cursor = connection.cursor()
    cursor.execute("UPDATE access_integratedproduct SET sulfites=false,sulfites_ppm=0,sulfites_usage_threshold=0;")
    changed_flavors = []
    for i in Ingredient.objects.filter(sulfites_ppm__gt=0):
        for lw in LeafWeight.objects.filter(ingredient=i).select_related():
            print lw
            lw.root_flavor.sulfites_ppm = (i.sulfites_ppm * lw.weight / ONE_THOUSAND) + lw.root_flavor.sulfites_ppm
            changed_flavors.append(lw.root_flavor)
    for f in changed_flavors:
        if f.sulfites_ppm > 10:
            f.sulfites=True
            f.sulfites_usage_threshold = ONE_HUNDRED / (f.sulfites_ppm / TEN)
            
        f.save()
        
    
    transaction.commit()


def parse_diacetyl():
    
    for lw in LeafWeight.objects.filter(ingredient__pk__in=DIACETYL_PKS):
        if lw.root_flavor.diacetyl == True:
            print "FALSE NEGATIVE"
            print lw.root_flavor
            lw.root_flavor.diacetyl = False
            #lw.root_flavor.save()





def get_col_info(model):
    field_names= []
    col_names = []
    for field in model._meta.fields:
        field_names.append(field.name)
        col_names.append(field.db_column)
    return field_names, col_names

def synchronize_prices():
    for f in Flavor.objects.filter(valid=True):
        print f.leaf_cost



@transaction.commit_manually
def build_experimental_tree(root_experimental):
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
    formula_root = ExperimentalFormulaTree(
        root_flavor=root_flavor,
        lft=0,
        weight=1000,
        weight_factor=1,
        node_flavor=root_flavor,
        row_id=0,
    )
    # this value caches an ingredient lookup that we may have to do later on
    # it finds the corresponding ingredient record for a flavor
    # 'gazinta' is a named foreign key. all() should have a count of 0 or 1. 
    try:
        formula_root.node_ingredient = root_flavor.gazinta.all()[0]
    except IndexError:
        formula_root.node_ingredient = None
    
    # we get the whole ingredient list first, so that it can be sliced
    # when passed to get_num_children.
    # formula_traversal() is a model instance method that does all of the
    # recursive queries to analyze a formula. it returns a tuple that 
    # represents one line item of a formula. 
    ingredient_list = []
    for ingredient in root_flavor.complete_formula_traversal():
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
        weight_factor = ingredient[INGREDIENT_WEIGHT_FACTOR]
        row_id = ingredient[INGREDIENT_ROW_ID]
        parent_id = ingredient[INGREDIENT_PARENT_ID]
        node_ingredient=formula_row.ingredient
        
        # build node details that are independent of tree structure       
        my_node = FormulaTree(
            root_flavor=root_flavor, 
            formula_row=formula_row, 
            weight_factor=weight_factor,
            row_id=row_id,
            parent_id=parent_id,
            node_ingredient=node_ingredient,
            node_flavor=node_ingredient.gazinta(),
            weight=formula_row.get_exploded_weight(weight_factor).quantize(THOUSANDTHS, rounding=ROUND_HALF_UP),            
            lft=i,
        )

        i += 1
        
        if get_num_children(ingredient_list[row_id:], row_id) > 0:
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
    transaction.commit()
    

@revision.create_on_success
def recalculate_guts(flavor):
    old_flavor_dict = copy.copy(flavor.__dict__)
    
    FormulaTree.objects.filter(root_flavor=flavor).delete()
    LeafWeight.objects.filter(root_flavor=flavor).delete()
    
    my_valid = True
    my_amount = 0
    for fr in flavor.formula_set.all():
        my_amount += fr.amount
        gazinta = fr.ingredient.gazinta()
        if gazinta is None:
            continue
        if gazinta.valid == False:
            my_valid = False
            break
    if my_amount != Decimal(1000):
        my_valid=False
    flavor.valid = my_valid
    
    build_tree(flavor)
    build_leaf_weights(flavor)
    my_leaf_weights = LeafWeight.objects.filter(root_flavor=flavor).select_related()
    
    sulfites = Decimal('0')
    allergens = {}
    my_prop_65 = False
    my_diacetyl = False
    my_pg = False
    my_solvents = {}
    sorted_solvent_string_list = []
    
    
    
    for lw in my_leaf_weights:
        
        sulfites += lw.ingredient.sulfites_ppm * lw.weight / ONE_THOUSAND
        
        for allergen in Ingredient.aller_attrs:
            if getattr(lw.ingredient, allergen):
                allergens[allergen]=1
                
        if lw.ingredient.prop65 == True:
            my_prop_65 = True
        if lw.ingredient.pk in DIACETYL_PKS:
            my_diacetyl = True
        if lw.ingredient.pk in PG_PKS:
            my_pg = True
            
        if lw.ingredient.id in SOLVENT_NAMES:
            my_solvents[lw.ingredient.id] = lw.weight
        
    flavor.sulfites_ppm = sulfites.quantize(tenths)
    if sulfites > 10:
        flavor.sulfites = True
        flavor.sulfites_usage_threshold = ONE_HUNDRED / (sulfites / TEN)    
    else:
        flavor.sulfites = False
        flavor.sulfites_usage_threshold = 0
        
    allergens = allergens.keys()
    if len(allergens) > 0:
        flavor.allergen = "Yes: %s" % ','.join(allergens)
        flavor.ccp2 = True
        flavor.ccp4 = True
    else:
        flavor.allergen = "None"

    flavor.prop_65 = my_prop_65
    flavor.diacetyl = not my_diacetyl
    flavor.no_pg = not my_pg

    solvents_by_weight = sorted(my_solvents.iteritems(), key=operator.itemgetter(1))
    solvents_by_weight.reverse()
    for solvent_number, solvent_amount in solvents_by_weight:
        if solvent_amount > 0:
            relative_solvent_amount = (solvent_amount / 10).quantize(ones)
            sorted_solvent_string_list.append("%s %s%%" % (SOLVENT_NAMES[solvent_number], relative_solvent_amount))
    solvent_string = "; ".join(sorted_solvent_string_list)
    flavor.solvent = solvent_string[:50]
        
    synchronize_price(flavor)
    flavor.rawmaterialcost = flavor.rawmaterialcost.quantize(thousandths)
    revision.comment = "Recalculated"
    flavor.save()    
    
    old_new_attrs = [
                     
            ('Raw Material Cost',old_flavor_dict['rawmaterialcost'],flavor.rawmaterialcost),
            ('Sulfites PPM',old_flavor_dict['sulfites_ppm'],flavor.sulfites_ppm),
            ('Allergen',old_flavor_dict['allergen'],flavor.allergen),
            ('Solvent',old_flavor_dict['solvent'],flavor.solvent),    
            ('Prop 65',old_flavor_dict['prop65'],flavor.prop65),
            ('NO Diacetyl',old_flavor_dict['diacetyl'],flavor.diacetyl),
            ('NO PG',old_flavor_dict['no_pg'],flavor.no_pg),
            ('Valid',old_flavor_dict['valid'],flavor.valid)          
        ]
    return (old_new_attrs,flavor)
    
"""
ALTER TABLE "ExperimentalLog" ADD COLUMN flavor_id integer;
ALTER TABLE "ExperimentalLog ADD CONSTRAINT "ExperimentalLog_flavor_id_fkey" FOREIGN KEY (flavor_id) REFERENCES access_integratedproduct(id) DEFERRABLE INITIALLY DEFERRED;
"""