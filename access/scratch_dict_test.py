import pdb
from decimal import Decimal
from collections import defaultdict
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
    for k, g in groupby(Formula.objects.filter(flavor__valid=True).values('amount','flavor_id','id','ingredient_id'), xfunc):
        d[k]=list(g)
    return d

def dictify_gaz():
    """Returns a dict with keys equal to ingredient ids and values equal to
    corresponding sub_flavor_id
    """
    d={}
    for i in Ingredient.objects.exclude(sub_flavor=None).select_related():
        if (i.flavornum != 0) and i.sub_flavor.valid==True:
            d[i.pk] = (i.sub_flavor_id, i.sub_flavor.yield_field)
    return d

def dictify_gazintas():
    d = {}
    for i in Ingredient.objects.exclude(sub_flavor=None).values_list('pk','sub_flavor_id'):
        d[i[0]] = i[1]
    return d

#this is fast but weight isn't calculated yet just wf.
def traverse(d, gzs, k, wf, ):
    formula = []
    #print "Traversing %s..." % k
    for ingredient in d[k]:
        i = ingredient.copy()
        #print i
        if i['ingredient_id'] in gzs:
            g_id, g_yf = gzs[i['ingredient_id']] # the id and the yield field
            print(g_yf)
            new_wf = wf*(i['amount']/1000)
            print(new_wf)
            formula.extend(traverse(d, gzs, g_id, new_wf))
        else:
            i['amount'] = i['amount'] * wf
            formula.append(i)
    return formula  

def traverse_test(d=dictify_formulae(), gzs=dictify_gaz()):
    z=0
    t_list = {}
    for k in d:
        t_list[k] = traverse(d,gzs,k,1)

    return t_list

def get_formulae_dicts():
    flavors = Flavor.objects.filter(valid=True).values('id',
                                                        'unitprice',
                                                        'rawmaterialcost',
                                                        'spraydried')
    flavor_dict = {}
    "{flavor.id: flavor.values()}"
    for f in flavors:
        flavor_dict[f['id']] = f
    
    gazintas = Ingredient.objects.filter(
        ~Q(sub_flavor=None),
        
        Q(sub_flavor__yield_field=100)
        ).values(
            'sub_flavor','rawmaterialcode',
        )
    gazinta_dict = {}
    "{ingredient.rawmaterialcode: ingredient.sub_flavor_id}"
    sub_flavor_dict = {}
    "{flavor.pk: ingredient.rawmaterialcode}"
    
    for g in gazintas:
        rmc = g['rawmaterialcode']
        sub_flavor_id = g['sub_flavor']
        gazinta_dict[rmc] = sub_flavor_id
        
        if sub_flavor_id:
            sub_flavor_dict[sub_flavor_id] = rmc
    #
    ingredients = Ingredient.objects.filter(discontinued=False).values('id',
                                                                        'rawmaterialcode',
                                                                        'product_name',
                                                                        'unitprice')
    ingredient_dict = {}
    "{ingredient.rawmaterialcode: ingredient.values()}"
    for i in ingredients:
        ingredient_dict[i['rawmaterialcode']] = i

    formulae_qs = Formula.objects.all()    
    formulae_dict = {}
    "{flavor.pk: flavor.formula_set.all().values()}"
    
    #x = 0
    for flavor in flavors:
        #print x
        #x += 1
        flavor_id = flavor['id']
        formulae_dict[flavor_id] = formulae_qs.filter(flavor__id=flavor_id).values(
                                                                                  'id',
                                                                                  'ingredient_id',
                                                                                  'amount',
                                                                                  'flavor_id',
                                                                                  'id')
            
    return (flavor_dict, formulae_dict, gazinta_dict, ingredient_dict, sub_flavor_dict)
flavor_dict, formulae_dict, gazinta_dict, ingredient_dict, sub_flavor_dict = get_formulae_dicts()

def recursive_traversal(flavor_id):
    def inner_traversal(flavor_id, weight_factor, row_id, parent_id):
        for ingredient in formulae_dict[flavor_id]:
            """
            """
            
            new_weight_factor = weight_factor*ingredient['amount']/1000
            ingredient_id = ingredient['ingredient_id']
            if ingredient_id in gazinta_dict:
                yield (ingredient, weight_factor, row_id, parent_id)
                row_id += 1
                for sub_ingredient in inner_traversal(gazinta_dict[ingredient_id],
                                                      new_weight_factor,
                                                      row_id,
                                                      row_id-1):
                    yield sub_ingredient
                    row_id += 1
            else:
                yield (ingredient, weight_factor, row_id, parent_id)
                row_id += 1
    row_id = 1
    parent_id = 0
    
    for ingredient in inner_traversal(flavor_id, decimal_one, row_id, parent_id):
        yield ingredient
        
def recursive_traversal_lite(flavor_id=24712):
    try:
        for ingredient in formulae_dict[flavor_id]:
            yield ingredient
            ingredient_id = ingredient['ingredient_id']
            if ingredient_id in gazinta_dict:
                for ingredient in recursive_traversal_lite(gazinta_dict[ingredient_id]):
                    yield ingredient
    except Exception as e:
        pdb.set_trace()
        
def get_ing_list(test_flavor_id=24712):
    ing_list = []
    for ing in recursive_traversal(test_flavor_id):
        ing_list.append(ing)
    return ing_list
    
    
def get_for_list(test_flavor_id=24712):
    test_flavor = Flavor.objects.get(pk=test_flavor_id)
    for_list = []
    for ing in test_flavor.formula_traversal():
        for_list.append(ing)
    return for_list

def test_rt(test_flavor_id=24712):    
    ing_list = get_ing_list(test_flavor_id)
    for_list = get_for_list(test_flavor_id)
    return (len(ing_list) - len(for_list))


def objectify_ing_list(ing_list):
    new_ing_list = []
    for ing in ing_list:
        new_tuple = (
                     Formula.objects.get(pk=ing[0]['id']),
                     ing[1],
                     ing[2],
                     ing[3],
                     )
        new_ing_list.append(new_tuple)
    return new_ing_list

def objectified_ing_list(flavor):
    flavor_id = flavor.pk
    return objectify_ing_list(get_ing_list(flavor_id))


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


def build_tree(root_flavor_id):
    """Given a flavor, build the corresponding FormulaTree rows using
    Formula row dicts (from a ValuesQuerySet).
    """
    formula_root = FormulaTree(root_flavor_id=root_flavor_id,
                               lft=0,
                               weight=1000,
                               weight_factor=1,
                               node_flavor_id=root_flavor_id,
                               row_id=0)

    if root_flavor_id in sub_flavor_dict:
        formula_root.node_ingredient_id = sub_flavor_dict[root_flavor_id]
    
    # we get the whole ingredient list first, so that it can be sliced
    # when passed to get_children.
    ingredient_list = []
    # for ingredient in root_flavor.formula_traversal():
    for ingredient in recursive_traversal(root_flavor_id):
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
        ingredient_oh = ingredient[0]
        ingredient_one = ingredient[1]
        my_node = FormulaTree(root_flavor_id=root_flavor_id,
                              row_id=ingredient[2],
                              parent_id=ingredient[3],
                              formula_row_id=ingredient_oh['id'],
                              node_ingredient_id=ingredient_oh['ingredient_id'],
                              node_flavor_id=ingredient_oh['flavor_id'],
                              weight=ingredient_oh['amount'] * ingredient_one,
                              weight_factor=ingredient_one,
                              lft=i
                              )

        children = get_children(ingredient_list[ingredient[2]:], ingredient[2])
        i += 1
        if len(children) > 0:
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
        #import pdb; pdb.set_trace()
        remaining_parent_node.save()
        
    formula_root.rgt = i
    formula_root.save()
    
    del ingredient_list
    del parent_stack
    del i

@transaction.atomic
def build_all_trees():
    FormulaTree.objects.all().delete()
    for flavor_info in Flavor.objects.filter(valid=True).values_list('id'):
        root_flavor_id = flavor_info[0]
        print(root_flavor_id)
        
        
        formula_root = FormulaTree(root_flavor_id=root_flavor_id,
                                   lft=0,
                                   weight=1000,
                                   weight_factor=1,
                                   node_flavor_id=root_flavor_id,
                                   row_id=0)
    
        if root_flavor_id in sub_flavor_dict:
            formula_root.node_ingredient_id = sub_flavor_dict[root_flavor_id]
        
        # we get the whole ingredient list first, so that it can be sliced
        # when passed to get_children.
        ingredient_list = []
        # for ingredient in root_flavor.formula_traversal():
        for ingredient in recursive_traversal(root_flavor_id):
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
            ingredient_oh = ingredient[0]
            ingredient_one = ingredient[1]
            my_node = FormulaTree(root_flavor_id=root_flavor_id,
                                  row_id=ingredient[2],
                                  parent_id=ingredient[3],
                                  formula_row_id=ingredient_oh['id'],
                                  node_ingredient_id=ingredient_oh['ingredient_id'],
                                  node_flavor_id=ingredient_oh['flavor_id'],
                                  weight=ingredient_oh['amount'] * ingredient_one,
                                  weight_factor=ingredient_one,
                                  lft=i
                                  )
    
            children = get_children(ingredient_list[ingredient[2]:], ingredient[2])
            i += 1
            if len(children) > 0:
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
            #import pdb; pdb.set_trace()
            remaining_parent_node.save()
            
        formula_root.rgt = i
        formula_root.save()
        
        del ingredient_list
        del parent_stack
        del i
        
        
        
        
    transaction.commit()