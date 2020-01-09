# import pdb
# from operator import itemgetter
# from decimal import Decimal, ROUND_HALF_UP
# from collections import deque, defaultdict
# from datetime import datetime, date
#
# from django.db import transaction
# from django.db.models import Q, F, Sum
# from django.conf import settings
#
# from access.models import Flavor, Ingredient, Formula, FormulaTree, LeafWeight, FormulaException
#
# from one_off.migration_utils import formulae, gazinta_index
#
# INGREDIENT_FORMULA_ROW = 0
# INGREDIENT_WEIGHT_FACTOR = 1
# INGREDIENT_ROW_ID = 2
# INGREDIENT_PARENT_ID = 3
#
# THOUSANDTHS = Decimal('1.000')
# LOWER_BOUND = Decimal('999.0')
# UPPER_BOUND = Decimal('1001.0')
# ONE_HUNDRED = Decimal('100')
# ONE_THOUSAND = Decimal('1000')
# ZERO = Decimal('0')
# SD_COST = Decimal('2.60')
# test_flavor = Flavor.objects.get(number=9700)
#
#
# def complete_formula_traversal(root_flavor, weight_factor=Decimal(1), row_id=1,
#                                parent_id=0,):
#     """Yields a tuple:
#     (ingredient, weight_factor, row_id, parent_id)
#
#     This is the complete method for traversing a formula. It will account
#     for percentage yield, and spray dry costs to produce the final bill
#     of materials and costs.
#     """
#     def inner_traversal(flavor, weight_factor, row_id,
#                         parent_id):
#         for formula_row_dict in formulae[flavor.number].values():
#             """If an ingredient is a gazinta, first the gazinta itself
#             is yielded, then formula_traversal is called on all the sub-
#             ingredients. Else, the ingredient is simply yielded,
#             because it has no subs.
#
#             Each time the function yields, the row_id increments.
#             """
#             if formula_row_dict['ingredient_id'] in gazinta_index:
#                 yield (formula_row_dict, weight_factor, row_id, parent_id)
#                 row_id += 1
#
#                 gaz = gazinta_index[formula_row_dict['ingredient_id']]
#                 if gaz.yield_field != 100:
#                     new_weight_factor = (weight_factor / (Decimal(gaz.yield_field) / 100)) * formula_row_dict['amount']/1000
#                 else:
#                     new_weight_factor = weight_factor*formula_row_dict['amount']/1000
#
#                 for sub_ingredient in inner_traversal(
#                                         gaz,
#                                         new_weight_factor,
#                                         row_id,
#                                         row_id - 1):
#                     yield sub_ingredient
#                     row_id += 1
#             else:
#                 yield (formula_row_dict, weight_factor, row_id, parent_id)
#                 row_id += 1
#
#     row_id = 1
#     parent_id = 0
#     try:
#         if root_flavor.yield_field != 100:
#             weight_factor = weight_factor / (Decimal(root_flavor.yield_field) / 100)
#     except:
#         pass
#     for ingredient in inner_traversal(root_flavor, weight_factor, row_id, parent_id):
#         yield ingredient
#
# def find_usage(ingredient_pk, gazinta_lists, flavor_valid):
#     ingredient = Ingredient.objects.get(pk=ingredient_pk)
#     # edge_check = set()
#     usage = {}
#     formula_queue = deque()
#
#     for fr in ingredient.formula_set.values('flavor_id','amount'):
#         formula_queue.append(fr)
#
#     i = 0
#     l = len(formula_queue)
#     while(formula_queue):
#         i += 1
#         print "iter count: %s | queue length: %s" % (i, l)
#
#         fr = formula_queue.popleft()
#         l -= 1
#
#
#         flavor_id = fr['flavor_id']
#         if flavor_id not in flavor_valid:
#             continue
#         try:
#             usage[flavor_id].append(fr)
#         except KeyError:
#             usage[flavor_id] = [fr]
#
#         # YOU KEEP MODIFYING THE SAME OBJS! stop it
#         for new_fr in gazinta_lists.get(flavor_id,()):
#             my_new_fr = new_fr.copy()
#             my_new_fr['amount'] *= fr['amount'] / 1000
# #            edge = (flavor_id, new_flavor_id)
# #            if edge in edge_check:
# #                continue
# #            else:
# #                edge_check.add(edge)
#
#             formula_queue.append(my_new_fr)
#             l += 1
#
#     return usage
#
# def update_cost(usage, delta):
#     flavor_deltas = {}
#     for f_id, ing_list in usage.iteritems():
#         sum = 0
#         for x in ing_list:
#             sum += x['amount']
#         flavor_deltas[f_id] = sum * delta / 1000
#     return flavor_deltas
#
# def get_usage_and_update_cost(ingredient_pk, gazinta_lists, flavor_valid, delta):
#     u = find_usage(ingredient_pk, gazinta_lists, flavor_valid)
#     return update_cost(u, delta)
#
#
#
# def get_num_children(ingredient_list, parent_id):
#     """Given a parent id, return the rows in ingredient_list that have
#     that parent_id. Typically a slice of ingredient_list is passed in
#     that does not include nodes closer to the root.
#     """
#     num_children = 0
#     #print "PARENT ID: %s" % parent_id
#     for ingredient in ingredient_list:
#         # print ingredient[3]
#         if ingredient[3] == parent_id:
#             num_children += 1
#
#     return num_children
#
# def has_children(ingredient_list, parent_id):
#     """Like get_num_children, but it returns True as soon as one child
#     is found.
#     """
#     for ingredient in ingredient_list:
#         if ingredient[3] == parent_id:
#             return True
#     return False
#
# def get_exploded_weight(formula_row,weight_factor ):
#     return formula_row['amount'] * weight_factor
#
# @transaction.atomic
# def build_tree(root_flavor):
#     """Given a root_flavor model instance, construct a more sane tree-like
#     representation of the formula of root_flavor. In order to see the formula
#     for a flavor model instance, many recursive queries may have to be
#     executed (encapsulated in the Flavor model instance method
#     formula_traversal()). This function uses formula_traversal() to create
#     a new data structure using FormulaTree model instances to represent a
#     formula using modified-preorder tree traversal in such a way that
#     recursive queries won't be required to analyze a formula.
#     """
#     # initializing special values for the root flavor
#     formula_root = FormulaTree(
#         root_flavor=root_flavor,
#         lft=0,
#         weight=1000,
#         weight_factor=1,
#         node_flavor=root_flavor,
#         row_id=0,
#     )
#     # this value caches an ingredient lookup that we may have to do later on
#     # it finds the corresponding ingredient record for a flavor
#     # 'gazinta' is a named foreign key. all() should have a count of 0 or 1.
#     gazintas = root_flavor.gazinta.all()
#     if gazintas.count() > 0:
#         formula_root.node_ingredient = gazintas[0]
#     else:
#         formula_root.node_ingredient = None
#
#     # we get the whole ingredient list first, so that it can be sliced
#     # when passed to get_num_children.
#     # formula_traversal() is a model instance method that does all of the
#     # recursive queries to analyze a formula. it returns a tuple that
#     # represents one line item of a formula.
#     ingredient_list = []
#     for ingredient in complete_formula_traversal(root_flavor):
#         ingredient_list.append(ingredient)
#
#     # this stack holds nodes which have children because their rgt values
#     # are not known until their children are visited.
#     parent_stack = []
#     parent_stack.append(formula_root)
#
#     # i is the left/right number of a node in our tree. the root node has a
#     # left number of ZERO and a right number of 2n-1 where n is the number of
#     # nodes.
#     # i is incremented in the following for loop, always immediately
#     # after it's current value is needed, so that it's the correct value
#     # for the next step of the algorithm
#     i = 1
#     for ingredient in ingredient_list:
#         # if the ingredient's parent id does not match the row id of the
#         # ingredient on the parent stack, then we've gone back up the tree
#         # and need to assign rgt values to nodes that we missed
#         look_at_parent_stack = True
#         while(1):
#             if look_at_parent_stack == False:
#                 break
#             try:
#                 if ingredient[INGREDIENT_PARENT_ID] != parent_stack[-1].row_id:
#                     last_parent = parent_stack.pop()
#                     last_parent.rgt = i
#                     i += 1
#                     last_parent.save()
#                 else:
#
#                     look_at_parent_stack = False
#             except IndexError:
#                 break
#
#         formula_row = ingredient[INGREDIENT_FORMULA_ROW]
#
#         row_id = ingredient[INGREDIENT_ROW_ID]
#         if formula_row['ingredient_id'] in gazinta_index:
#             node_flavor = gazinta_index[ formula_row['ingredient_id'] ]
#         else:
#             node_flavor = None
#         # build node details that are independent of tree structure
#         my_node = FormulaTree(
#             root_flavor=root_flavor,
#             formula_row_id=formula_row['id'],
#             weight_factor=ingredient[INGREDIENT_WEIGHT_FACTOR],
#             row_id=row_id,
#             parent_id=ingredient[INGREDIENT_PARENT_ID],
#             node_ingredient_id=formula_row['ingredient_id'],
#             node_flavor=node_flavor,
#             weight=get_exploded_weight(formula_row,ingredient[INGREDIENT_WEIGHT_FACTOR]).quantize(THOUSANDTHS, rounding=ROUND_HALF_UP),
#             lft=i,
#         )
#
#         i += 1
#
#         if has_children(ingredient_list[row_id:], row_id):
#             parent_stack.append(my_node)
#         else:
#             my_node.rgt = i
#             i += 1
#             my_node.leaf = True
#             my_node.save()
#
#     # flush parent_stack and assign rgt numbers
#     parent_stack.reverse()
#     for remaining_parent_node in parent_stack:
#         remaining_parent_node.rgt = i
#         i += 1
#         remaining_parent_node.save()
#
#     formula_root.rgt = i
#     formula_root.save()
#     #transaction.commit()
#
# def build_trees(flavors, start, end):
#     x = start
#     while (x < end):
#         f = flavors[x]
#
#         build_tree(f)
#         x += 1
#
# def test_gc():
#     import gc
#     print gc.collect()
#     print gc.collect()
#     SAMPLE_SIZE = 1000
#     flavors = Flavor.objects.filter(valid=True)
#
#     start = 0
#     end = 2
#
#     while (start < SAMPLE_SIZE):
#         print " ****************************************** "
#         print "Start: %s, End: %s" % (start, end)
#         build_trees(flavors, start, end)
#         start = end + 1
#         end = end * 2
#         print gc.collect()
#
#
# # time 900s
# @transaction.atomic
# def build_all_trees():
#     FormulaTree.objects.all().delete()
#     for f in Flavor.objects.filter(valid=True):
#         print f
#         build_tree(f)
#
#
# def synchronize_price(f, verbose=False):
#     print f
#     rmc = 0
#     lastspdate = datetime(1990,1,1)
#     for leaf in f.leaf_weights.all():
#         sub_flavor = leaf.ingredient.sub_flavor
#         adjustment = 1
#         if sub_flavor is not None:
#             y = ONE_HUNDRED.__copy__()
#             y = sub_flavor.yield_field
#
#             if y == 0:
#                 y = 100
#
#             adjustment = y/ONE_HUNDRED
#             if adjustment == ZERO:
#                 adjustment = 1
#
#         cost_diff = leaf.weight * leaf.ingredient.unitprice / adjustment
#         rmc += cost_diff
#         if verbose:
#             print '"%s","%s","%s"' % (leaf.ingredient.id, leaf.ingredient.product_name, cost_diff)
#         ing_ppu = leaf.ingredient.purchase_price_update
#         if lastspdate < ing_ppu:
#             lastspdate = ing_ppu
#
#     y = ONE_HUNDRED.__copy__()
#
#     y = f.yield_field
#
#     adjustment = y/ONE_HUNDRED
#     if adjustment == ZERO:
#         adjustment = 1
#     # print adjustment
#     if f.spraydried:
#         f.rawmaterialcost = rmc / 1000 / adjustment + SD_COST
#     else:
#         f.rawmaterialcost = rmc / 1000 / adjustment
#     f.lastspdate = lastspdate
#     f.save()
#
# def synchronize_all_prices():
#     sd_price = Decimal('2.90')
#     update_time = datetime.now()
#     for f in Flavor.objects.select_related().filter(valid=True):
#         synchronize_price(f)
#
#
# """
# the below functions are all wrong because they are copied from the Flavor
# model, before FormulaTree was modified to actually store a node explicitly
# for the root flavor.
# """
# def leaf_nodes(flavor):
#     return FormulaTree.objects.filter(root_flavor=flavor).filter(rgt=F('lft') + 1)
#
# def root_nodes(flavor):
#     return FormulaTree.objects.filter(root_flavor=flavor).filter(parent_id=0)
#
# def leaf_node_tester():
#     ceil = Decimal('1000.01')
#     floor = Decimal('999.99')
#     for f in Flavor.objects.filter(valid=True):
#         sum = 0
#
#         for leaf in leaf_nodes(f):
#             sum += leaf.weight
#
#         if sum > ceil or sum < floor:
#             print "%s -- %s" % (f, sum)
#
# def consolidated_leafs(flavor):
#     leaf_ingredients = leaf_nodes(flavor)
#     cons_leafs = {}
#     for leaf in leaf_ingredients:
#         cons_leafs[leaf.node_ingredient] = cons_leafs.get(leaf.node_ingredient, 0) + leaf.weight
#
#     return cons_leafs
#
# def build_leaf_weights(flavor):
#     cls = flavor.consolidated_leafs
#     for i,w in cls.iteritems():
#         lw = LeafWeight(root_flavor=flavor,
#                         ingredient=i,
#                         weight=w)
#         lw.save()
#
# def build_all_leaf_weights():
#     LeafWeight.objects.all().delete()
#     bad_total_flavors = []
#     for f in Flavor.objects.filter(valid=True):
#         print f
#         try:
#             build_leaf_weights(f)
#         except FormulaException:
#             bad_total_flavors.append(f)
#     print "bad total flavors"
#     print bad_total_flavors
#
#
# def deep_flavor_search():
#     formulas = {}
#     formulas_by_length = defaultdict(list)
#     formula_pairs = []
#     for f in Flavor.objects.filter(valid=True):
#         print f
#         formula = LeafWeight.objects.filter(root_flavor=f).values_list('ingredient_id','weight').order_by('ingredient__pk')
#         formula_len = len(formula)
#         formulas_by_length[formula_len].append(f)
#         formulas[f] = formula
#
#     for k, v in formulas_by_length.iteritems():
#         print k
#         v = sorted(v, key=lambda f: formulas[f][0])
#         formulas_by_length[k]=v
#         for i in range(0, len(v)-2):
#             print v[i]
#             lf = formulas[v[i]]
#             rf = formulas[v[i+1]]
#             formula_match = True
#             for j in range(0, k-1):
#                 if lf[j] == rf[j]:
#                     print "match: %s" % repr(lf[j])
#                 else:
#                     formula_match = False
#                     break
#             if formula_match:
#                 formula_pairs.append((v[i], v[i+1]))
#
#
#     return (formulas, formulas_by_length, formula_pairs)
#     # find all the formulae that are the same length
#     # find all the formulae that start with the same ingredient
#     # find the ones that are the same length and start with the same ingredient
#
#     # return formulas
#
# def dfs_sanity_check():
#     weird_flavors = []
#     for f in Flavor.objects.filter(valid=True):
#         if f.formula_set.all().count() == 1:
#             if f.productmemo[:7] != "Same as":
#                 print "%s: %s" % (f, f.productmemo)
#                 ing = f.formula_set.all()[0]
#                 print ing.gazinta()
#                 weird_flavors.append(f)
#
#     return weird_flavors
#
#
# # check the ith ingredient of formula
# # for each formula of length x:
# #    for i=0,x:
# #
# #    for i=1,max_formula_length:
# #        repartitioned_list = []
# #        for sub_list in formulas_by_len[i]:
# #        sub_list is the list of all formulas that share the same length i
# #
#
# def same_len_formula_search(formulas):
#     """Given a list of formulas of the same length, sorted in ascending
#     order of ingredient__pk, compare them ingredient by ingredient
#     to find formulas that are the same.
#     """
#     return
#
# def sum_nodes(nodes):
#     sum = 0
#     for n in nodes:
#         sum += n.weight
#     return sum
#
# def analyze_subtrees(flavor):
#     child_weights = {}
#     parent_weights = {}
#     nodes = FormulaTree.objects.filter(root_flavor=flavor).values('parent_id', 'row_id', 'weight')
#
#     for node in nodes:
#         try:
#             child_weights[node['parent_id']] += node['weight']
#         except:
#             child_weights[node['parent_id']] = node['weight']
#     del child_weights[None]
#
#     for node in nodes:
#         if node['row_id'] in child_weights:
#             parent_weights[node['row_id']] = node['weight']
#
#     return child_weights, parent_weights
#
# def degree_of_error(flavor):
#     """Returns the sum of the (absolute) differences between leaf nodes and
#     root nodes.
#     """
#     child_weights, parent_weights = analyze_subtrees(flavor)
#     child_keys = set(child_weights.keys())
#     parent_keys = set(parent_weights.keys())
#
#     if child_keys != parent_keys:
#         import pdb; pdb.set_trace()
#
#     error = 0
#     for k in child_keys:
#         error += abs(child_weights[k] - parent_weights[k])
#
#     error = int(error*1000)
#     return error
#
# def subtree_match(flavor):
#     lhs, rhs = analyze_subtrees(flavor)
#     return lhs == rhs
#
# def find_characteristic_wrong_subtree():
#     last_comparer = 1000
#     for flavor in Flavor.objects.filter(valid=True):
#         # print flavor
#         nodes = FormulaTree.objects.filter(root_flavor=flavor)
#         if subtree_match(flavor):
#             pass
#         else:
#             c = nodes.count()
#             # print c
#             if nodes.count() < last_comparer:
#                 last_bad = flavor
#
#     return last_bad
#
#
# def get_complete_ingredient_list(flavor):
#     ingredients = {}
#     for node in leaf_nodes(flavor):
#         try:
#             ingredients[node.node_ingredient] += node.weight
#         except:
#             ingredients[node.node_ingredient] = node.weight
#
#     return ingredients
#
#
# def make_current_cost_update():
#     now = datetime.now()
#     def cost_update(flavor):
#         total_rmc = 0
#         for formula_row in flavor.formula_set.all():
#             ingredient = formula_row.ingredient
#             g = ingredient.gazinta()
#             if g:
#                 if g.lastspdate == now:
#                     ingredient_rmc = g.yield_adjusted_rmc * formula_row.amount
#                 else:
#                     ingredient_rmc = cost_update(g) * formula_row.amount
#             else:
#                 ingredient_rmc = ingredient.unitprice * formula_row.amount
#             total_rmc += ingredient_rmc
#
#         flavor.rawmaterialcost = total_rmc / ONE_THOUSAND
#         flavor.lastspdate = now
#         flavor.save()
#         return flavor.yield_adjusted_rmc
#     return cost_update
#
#
# def update_all_costs(verbose=False):
#     """
#     Add up all the weighted costs of the ingredients to find unit cost of
#     flavor.
#
#     Does the flavor have any stale gazintas?
#         Recursively update gazintas
#     Else:
#         Add all the weighted costs of ingredients.
#         Set the last price update.
#         Save the flavor.
#
#     Let's try the closure make_current_cost_update, defined above
#     """
#     flavors_updated = {}
#
#     def make_current_cost_update():
#         now = datetime.now()
#         def cost_update(flavor):
#             if flavor in flavors_updated:
#                 return flavors_updated[flavor.id]
#             if verbose:
#                 print flavor
#             total_rmc = 0
#             for formula_row in flavor.formula_set.all():
#                 ingredient = formula_row.ingredient
#                 g = ingredient.gazinta()
#                 if g:
#                     if g.id in flavors_updated:
#                         ingredient_rmc = flavors_updated[g.id] * formula_row.amount
#                     else:
#                         if g.lastspdate == now:
#                             ingredient_rmc = g.yield_adjusted_rmc * formula_row.amount
#                         else:
#                             ingredient_rmc = cost_update(g) * formula_row.amount
#                 else:
#                     ingredient_rmc = ingredient.unitprice * formula_row.amount
#                 total_rmc += ingredient_rmc
#
#             flavor.rawmaterialcost = total_rmc / ONE_THOUSAND
#             flavor.lastspdate = now
#             flavor.save()
#             yarmc = flavor.yield_adjusted_rmc
#             flavors_updated[flavor.id] = yarmc
#             return yarmc
#         return cost_update
#
#
#
#     cost_update = make_current_cost_update()
#     for flavor in Flavor.objects.filter(valid=True):
#         cost_update(flavor)
#
#
# def test():
#     build_all_trees()
#     build_all_leaf_weights()
#
#
#
#
#
#
#
#
# aller_attrs = [
#         'crustacean',
#         'eggs',
#         'fish',
#         'milk',
#         'peanuts',
#         'soybeans',
#         'treenuts',
#         'wheat',
#         'sulfites',
#         'sunflower',
#         'sesame',
#         'mollusks',
#         'mustard',
#         'celery',
#         'lupines',
#         'yellow_5',
#     ]
#
# i_aller_dict = {
#  u'Yes-Cereals (Gluten)': 'wheat',
#  u'Yes-Crustacean Shellfish': 'crustacean',
#  u'Yes-Crustaceans': 'crustacean',
#  u'Yes-Eggs': 'eggs',
#  u'Yes-Fish': 'fish',
#  u'Yes-Milk': 'milk',
#  u'Yes-Peanuts': 'peanuts',
#  u'Yes-Peanuts/Legumes': 'peanuts',
#  u'Yes-Soy/Legumes': 'soybeans',
#  u'Yes-Soybeans': 'soybeans',
#  u'Yes-Sulfites': 'sulfites',
#  u'Yes-Tree Nuts': 'treenuts',
#  u'Yes-Wheat(Gluten)': 'wheat',}
#
# #setattr(model_instance,
# #                        model_field.attname,
# #                        parsed_csv_field)
#
#
# def iter_ingredients():
#     for i in Ingredient.objects.all():
#         if i.allergen in i_aller_dict:
#             setattr(i,i_aller_dict[i.allergen],True)
#             i.save()
#
#
# def parse_ingredient_allergens():
#
#     allergenic_ingredients = Ingredient.objects.filter(
#         Q(crustacean=True) |
#         Q(eggs=True) |
#         Q(fish=True) |
#         Q(milk=True) |
#         Q(peanuts=True) |
#         Q(treenuts=True) |
#         Q(soybeans=True) |
#         Q(wheat=True) |
#         Q(sulfites=True) |
#         Q(sunflower=True) | 
#         Q(sesame=True) |
#         Q(mollusks=True) |
#         Q(mustard=True) |
#         Q(celery=True) |
#         Q(lupines=True) |
#         Q(yellow_5=True)
#     )
#     n= datetime.now()
#     f_list = []
#     for i in allergenic_ingredients:
#         if not i.is_gazinta:
#             for lw in LeafWeight.objects.filter(ingredient=i).select_related():
#                 f = lw.root_flavor
#
#                 for allergen in aller_attrs:
#                     i_aller = getattr(i, allergen)
#                     if i_aller:
#                         print "%s - %s" % (f, allergen)
#                         f_list.append(f)
#                     setattr(f, allergen, i_aller)
#                 f.save()
#
#     for f in f_list:
#         aller_list = []
#         for allergen in aller_attrs:
#             f_aller = getattr(f, allergen)
#             if f_aller:
#                 aller_list.append(allergen)
#         f.allergen = ','.join(aller_list)
#         f.save()
#
# DIACETYL_PKS = [262,]
# def parse_diacetyl():
#
#     for lw in LeafWeight.objects.filter(ingredient__pk__in=DIACETYL_PKS):
#         if lw.root_flavor.diacetyl == True:
#             print "FALSE NEGATIVE"
#             print lw.root_flavor
#             lw.root_flavor.diacetyl = False
#             #lw.root_flavor.save()
#
# #    def parse_leafweights(f):
# #        begin_val = f.diacetyl
# #
# #        for lw in f.leaf_weights.all():
# #            if lw.ingredient_id == DIACETYL_PK:
# #                if begin_val == True:
# #                    print "False Negative -- bad kind"
# #                    print f
# #                    f.diacetyl = False
# #                    f.save()
# #                    return
# #        if begin_val == False:
# #            #print "False positive -- ok"
# #            f.diacetly = True
# #            f.save()
# #            #print f
# #            return
# #
# #    for f in Flavor.objects.all():
# #        parse_leafweights(f)
# #
# #def parse_haccp_plans():
# #
# #    haccp = {}
# #    haccp[101] = {
# #            'sd':True,
# #            'microtest':True,
# #            'allergen':False,
# #        }
# #    haccp[102] = {
# #            '':,
# #        }
# #    haccp[103] = {
# #            '':,
# #        }
# #    haccp[104] = {
# #            '':,
# #        }
# #    haccp[106] = {
# #            '':,
# #        }
# #    haccp[107] = {
# #            '':,
# #        }
# #    haccp[108] = {
# #            '':,
# #        }
# #    haccp[109] = {
# #            '':,
# #        }
# #    haccp[113] = {
# #            '':,
# #        }
# #    haccp[114] = {
# #            '':,
# #        }
#
#
#
# # LOG THIS STUFF!
# #
# #no_psi = []
# #has_psi = []
# #for f in Flavor.objects.all():
# #    try: psi = f.productspecialinformation; has_psi.append(f)
# #    except: print f; no_psi.append(f)
# #
# #for f in no_psi:
# #    f.productspecialinformation = ProductSpecialInformation(flavornumber=f.number, productid=f.pk, flavor=f, entered=n)
# #    f.productspecialinformation.save()
# #    f.save()
# #    print f
# #
# #for f in no_psi:
# #    f.productspecialinformation = ProductSpecialInformation(flavornumber=f.number, productid=f.pk, flavor=f, entered=n)
# #    f.productspecialinformation.save()
# #    f.save()
# #    print f
# #
# #no_psi = []
# #has_psi = []
# #for f in Flavor.objects.all():
# #    try: psi = f.productspecialinformation; has_psi.append(f)
# #    except: print f; no_psi.append(f)
# #
# #no_psi
# #len(has_psi)
# #Flavor.objects.all().count9)
# #Flavor.objects.all().count()
# #ProductSpecialInformation.objects.all().count()
# #for psi in ProductSpecialInformation.objects.all():
# #    print psi.flavor
# #
# #ProductSpecialInformation.objects.all().count()
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.flavor == None:
# #        print psi
# #
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.flavor != None:
# #        print psi
# #
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.flavor == None:
# #        print psi.flavornumber
# #
# #%hist
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.flavor == None:
# #        print psi.flavornumber
# #        psi.delete()
# #
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.flavor == None:
# #        print psi.flavornumber
# #        psi.delete()
#
# #for psi in ProductSpecialInformation.objects.all():
# #    psi.productid = psi.flavor.pk
# #    psi.save()
# #    print psi
# #
# #
# #for psi in ProductSpecialInformation.objects.all():
# #    if psi.productid != psi.flavor.pk:
# #        print psi
#
#
# #for e in ExperimentalLog.objects.all():
# #    if e.product_number is not None:
# #        try:
# #            f = Flavor.objects.get(number=e.product_number)
# #            if e.organic != f.organic:
# #                print f.number
# #        except Flavor.DoesNotExist:
# #            print "experimntal -> product number, no product exists for this experimental: %s" % e.number
#
# #
# #for e in ExperimentalLog.objects.all():
# #    if e.product_number is not None:
# #        try:
# #            f = Flavor.objects.get(number=e.product_number)
# #            f.spg = e.spg; f.save()
# #        except Flavor.DoesNotExist:
# #            pass
# #
# #for e in ExperimentalLog.objects.all():
# #    if e.product_number is not None:
# #        try:
# #            f = Flavor.objects.get(number=e.product_number)
# #            ## JUST FIND THE DISCREPANCY AND REPORT IT,
# #            ## no need to change anything because we are dropping e record
# #        except Flavor.DoesNotExist:
# #            pass
# #
#
#  #TESTS
# #In [1]: from access.models import ExperimentalLog, Flavor
# #
# #In [2]: f = set()
# #
# #In [3]: e = set()
# #
# #In [4]: for field in ExperimentalLog._meta.fields:
# #   ...:     e.add(field.db_column)
# #   ...:
# #   ...:
# #
# #In [5]: for field in Flavor._meta.fields:
# #   ...:     f.add(field.db_column)
# #   ...:
# #   ...:
# #
# #In [6]: f & e
# #Out[6]: set([None])
# ##################################################
# # SELECT COUNT(*) from psitest ;
# # select count(*) from "ExperimentalLog";
# # select count(*) from psitest FULL OUTER JOIN "ExperimentalLog" ON "ExperimentalLog"."ProductNumber" = psitest."FlavorNumber" ;
#
# #
# #from access.models import Formula, EPSIFormula, EPSITest
# #
# #for f in Formula.objects.all():
# #    print f
# #    try:
# #        et = EPSITest.objects.get(number=f.flavor.number)
# #    except:
# #        break
# #    newf = EPSIFormula(flavor=et, ingredient=f.ingredient, amount=f.amount, totalweight=f.totalweight,flavorextendedprice=f.flavorextendedprice, price=f.price, discontinued=f.discontinued, machinebatch=f.machinebatch, rawmaterialcode=f.rawmaterialcode)
# #    newf.save()
# #
# #
# #
# #
# #
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# #
# #fd_test=# DROP COL^C
# #fd_test=# ALTER TABLE "Products - Special Information" DROP COLUMN "ProductID";
# #ALTER TABLE
# #fd_test=# create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
# #ERROR:  column name "FlavorNumber" specified more than once
# #fd_test=# ALTER TABLE "Products - Special Information" DROP CONSTRAINT PR
# #
# #fd_test=# ALTER TABLE "Products - Special Information" DROP CONSTRAINT
# #
# #fd_test=# ALTER TABLE "Products - Special Information" DROP CONSTRAINT^C
# #fd_test=# \d "Products - Special Information"
# #fd_test=#  ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
# #ERROR:  syntax error at or near "PRIMARY"
# #LINE 1: ... "Products - Special Information" DROP CONSTRAINT PRIMARY KE...
# #                                                             ^
# #fd_test=#  ALTER TABLE "Products - Special Information" DROP CONSTRAINT PRIMARY KEY ("FlavorNumber");
# #ERROR:  syntax error at or near "PRIMARY"
# #LINE 1: ... "Products - Special Information" DROP CONSTRAINT PRIMARY KE...
# #                                                             ^
# #fd_test=#  ALTER TABLE "Products - Special Information" DROP CONSTRAINT "Products - Special Information_pkey";
# #ALTER TABLE
# #fd_test=# ALTER TABLE "Products - Special Information" ADD COLUMN id integer not null;
# #ERROR:  column "id" contains null values
# #fd_test=# ALTER TABLE "Products - Special Information" ADD COLUMN psi_id integer not null^C
# #fd_test=# create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
# #ERROR:  column name "FlavorNumber" specified more than once
# #fd_test=# ALTER TABLE "Products - Special Information" DROP COLUMN "FlavorNumber";
# #ALTER TABLE
# #fd_test=# create table psitest as select * from "Products - Special Information", "Products" where "Products - Special Information"."flavor_id" = "Products"."ProductID";
# #SELECT
# #fd_test=# \d psitest
# #fd_test=# \d "Products - Special Information"
# #fd_test=# ALTER TABLE "Products - Special Information" DROP COLUMN flavor_id;
# #ALTER TABLE
# #fd_test=# ALTER TABLE psitest DROP COLUMN flavor_id;
# #ALTER TABLE
# #fd_test=# \d psitest
# #fd_test=# \d "Products - Special Information"
# #fd_test=# \d psitest
# #fd_test=# ALTER TABLE psitest OWNER TO www-data;
# #ERROR:  syntax error at or near "-"
# #LINE 1: ALTER TABLE psitest OWNER TO www-data;
# #                                        ^
# #fd_test=# ALTER TABLE psitest OWNER TO "www-data";
# #ALTER TABLE
# #fd_test=# \q
# #postgres@testserver:/home/stachurski$ \d "Pro^C
# #postgres@testserver:/home/stachurski$ psql -d fd_test
# #psql (8.4.8)
# #Type "help" for help.
# #
# #fd_test=# \d "Products"
# #fd_test=# \d "Products
# #unterminated quoted string
# #fd_test=# \d "Products"
# #fd_test=# ALTER TABLE "Products" DROP COLUMN formulagraph;
# #ALTER TABLE
# #fd_test=# ALTER TABLE psitest DROP COLUMN formulagraph ;
# #ALTER TABLE
# #fd_test=#
#
# # ALTER TABLE "ExperimentalLog" RENAME COLUMN "ProductName" TO "ExperimentalProductName";
# # ALTER TABLE "ExperimentalLog" DROP COLUMN "Organic";
# # ALTER TABLE "ExperimentalLog" DROP COLUMN "SpG";
#
#
#
#
#
# #
# #
# #ALTER TABLE "access_ingredient"
# #ADD COLUMN "eggs" boolean,
# #ADD COLUMN "fish" boolean,
# #ADD COLUMN "milk" boolean,
# #ADD COLUMN "peanuts" boolean,
# #ADD COLUMN "soybeans" boolean,
# #ADD COLUMN "treenuts" boolean,
# #ADD COLUMN "wheat" boolean,
# #ADD COLUMN "sulfites" boolean,
# #ADD COLUMN "sunflower" boolean,
# #ADD COLUMN "sesame" boolean,
# #ADD COLUMN "mollusks" boolean,
# #ADD COLUMN "mustard" boolean,
# #ADD COLUMN "celery" boolean,
# #ADD COLUMN "lupines" boolean,
# #ADD COLUMN "yellow_5" boolean,
# #ADD COLUMN "crustacean" boolean,
# #ADD COLUMN "has_allergen_text" boolean;
#
# #ALTER TABLE "Products - Special Information"
# #ADD COLUMN "sunflower" boolean,
# #ADD COLUMN "sesame" boolean,
# #ADD COLUMN "mollusks" boolean,
# #ADD COLUMN "mustard" boolean,
# #ADD COLUMN "celery" boolean,
# #ADD COLUMN "lupines" boolean,
# #ADD COLUMN "yellow_5" boolean;
#
# def get_col_info(model):
#     field_names= []
#     col_names = []
#     for field in model._meta.fields:
#         field_names.append(field.name)
#         col_names.append(field.db_column)
#     return field_names, col_names
#
#
