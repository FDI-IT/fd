from decimal import Decimal, ROUND_HALF_UP
from collections import deque
import re

from django.db.models import Q

from access.models import Formula, FormulaTree, LeafWeight
from access.models import Flavor, Ingredient, Customer

from salesorders.report_parser import SalesOrderGenerator
from salesorders.models import SalesOrderNumber, LineItem

from newqc.models import LotSOLIStamp


number_re = re.compile('^\d+')
def parse_orders(saved_report):
    """
    """
#    import pdb; pdb.set_trace()
    #LineItem.objects.all().delete()
    SalesOrderNumber.objects.all().delete()
    sog =  SalesOrderGenerator(saved_report)
    lis = []
    for row in sog:
        try:
            lis.append(sog.try_line_item(row))
        except Exception as e:
            continue
    for li in lis:
        so,socreated = SalesOrderNumber.objects.get_or_create(number=li['Num'])
        if socreated:
            so.create_date = li['Date']
            customer,ccreated = Customer.objects.get_or_create(companyname=li['Name'])
            so.customer = customer
            so.save()
            #so.customer=
        try:
            re_match = number_re.match(li['Item'])
            if re_match:
                flavor_number = re_match.group()
                flavor = Flavor.objects.get(number=flavor_number)
            else:
                continue
        except Flavor.DoesNotExist:
            continue
        except ValueError:
            continue

        # this part checks wheter a SOLI is covered by a lot already
        try:
            solistamp = LotSOLIStamp.objects.get(salesordernumber=so.number, quantity=li['Qty'])
            if solistamp:
                covered=True
        except:
            covered=False

        li = LineItem(
                salesordernumber=so,
                flavor=flavor,
                quantity=li['Qty'],
                unit_price=li['Sales Price'],
                quantity_price=li['Amount'],
                ship_date=li['Ship Date'],
                due_date=li['Due Date'],
                covered=covered,
            )
        li.save()
    return lis


#    summarized_orders = []        
#    for flavor, details in good_orders.items():
#        total = Decimal('0')
#        for detail in details:
#            total += detail.quantity
#        summarized_orders.append((flavor, 
#                                  total,
#                                  flavor.rawmaterialcost,
#                                  details))
#    summarized_orders = sorted(summarized_orders, key=itemgetter(1))
#    
#    for order in summarized_orders:
#        flavor_number = order[0]
#        total_weight = str(order[1])
#        order_list = ""
#        for li in order[3]:
#            order_list += "%s: %s lbs," % (li.salesordernumber.customer.companyname,
#                                           li.quantity)
#            
#    return summarized_orders, bad_orders


###########################3old

class UsageFinder:
    
    
    def cache_builder(self):
        self.flavor_valid = set()
        self.gazinta_lists = {}
        flavors = Flavor.objects.all()
        for f in flavors:
            fn = f.number
            if f.valid:
                self.flavor_valid.add(fn)
            
            try:
                inner_list = []
                for fr in f.gazinta.all()[0].formula_set.all():
                    inner_list.append(fr)
                self.gazinta_lists[fn] = inner_list
            except:
                pass
        return
    
    def find_usage(self,ingredient_pk):
       
        ingredient = Ingredient.objects.get(pk=ingredient_pk)
        edge_check = set()
        usage = {}
        formula_queue = deque()
        i = 0
        for fr in ingredient.formula_set.all():
            formula_queue.append(fr)
            
        while(formula_queue):
            i += 1
            print i
            print len(formula_queue)
            fr = formula_queue.popleft()
            my_flavor = fr.flavor
            fn = my_flavor.number
            if fn not in self.flavor_valid:
                continue
            try:
                usage[fn] += fr.amount
            except KeyError:
                usage[fn] = fr.amount
                
            try:
                for new_fr in self.gazinta_lists[fn]:
                    edge = (fn, new_fr.flavor.number)
                    if edge in edge_check:
                        continue
                    else:
                        edge_check.add(edge)
                     
                    #print "before: %s" % new_fr
                    new_fr.amount *= fr.amount / 1000
                    #print "after: %s" % new_fr
                    formula_queue.append(new_fr)
            except:
                pass
            
            if fn == 180030:
                print usage[fn]
    
        return usage



class FlavorOrder:
    hundredths = Decimal('0.00')
    def __init__(self, weight, rmc):
        self.rmc = rmc
        self.weight = weight
        self.count = 1
        
    def add_weight(self, weight):
        self.weight += weight.quantize(self.hundredths)
        self.count += 1
        
    def total_cost(self):
        return (self.rmc * self.weight).quantize(self.hundredths, rounding=ROUND_HALF_UP)
        
class IngredientCounterLI:
    thousandths = Decimal('0.000')
    def __init__(self, li_list):
        self.ingredients = {}
        self.li_list = li_list
        self.formula_qs = Formula.objects.all()
        
    def aggregate_ingredients(self):
        for li in self.li_list:
            relative_order_quantity = li.quantity / 1000
            for lw in LeafWeight.objects.filter(root_flavor=li.flavor).select_related():
                relative_weight = lw.weight * relative_order_quantity
                try:
                    self.ingredients[lw.ingredient].add_weight(relative_weight.quantize(self.thousandths))
                except KeyError:
                    self.ingredients[lw.ingredient] = FlavorOrder(relative_weight.quantize(self.thousandths), lw.ingredient.unitprice)
            
#            
#            for leaf in LeafWeight.objects.select_related().filter(root_flavor=li.flavor):
#                relative_weight = leaf.weight * li.quantity / 1000
#                ing = leaf.ingredient
#                try:
#                    self.ingredients[ing].add_weight(relative_weight.quantize(self.thousandths))
#                except KeyError:
#                    self.ingredients[ing] = FlavorOrder(relative_weight.quantize(self.thousandths), ing.unitprice)
#     
        
class GazintaCounterLI:
    def __init__(self, li_list):
        self.gazintas = {}
        self.li_list = li_list
        self.formula_qs = Formula.objects.all()
        
    def aggregate_gazintas(self):
        for li in self.li_list:
            for node in FormulaTree.objects.select_related().filter(
                        root_flavor=li.flavor).filter(
                        ~Q(node_flavor=None)):
                flavor = node.node_flavor
                relative_weight = node.weight * li.quantity / 1000
                try:
                    self.gazintas[flavor].add_weight(relative_weight)
                except KeyError:
                    self.gazintas[flavor] = FlavorOrder(relative_weight, flavor.rawmaterialcost)
            
#            
#            for formula_row in li.flavor.formula_traversal(Decimal(str(li.quantity/1000)), 
#                                                           formula_qs=self.formula_qs):
#                ing = formula_row[0]
#                rel_weight = ing.get_exploded_weight(
#                                formula_row[1]).quantize(Decimal('1.000'), rounding=ROUND_HALF_UP)
#                if ing.ingredient.is_gazinta:
#                    flavor = ing.gazinta()
#                    try:
#                        self.gazintas[flavor].add_weight(rel_weight)
#                    except KeyError:
#                        self.gazintas[flavor] = FlavorOrder(rel_weight, flavor.rawmaterialcost)