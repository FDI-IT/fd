from decimal import Decimal
from copy import deepcopy

from django.db.models import Count, Sum, Avg

from access.models import ExperimentalLog, FormulaTree
from newqc.models import Lot

class AverageAccumulator():
    def __init__(self):
        self.accumulator = Decimal('0')
        self.range = Decimal('0')
        
    def get_result(self):
        try:
            return self.accumulator / self.range
        except:
            return ""
    
    def add_element(self, element):
        if element != 0:
            try:
                self.accumulator += element
                self.range += 1
            except:
                try:
                    self.accumulator += Decimal(str(element))
                    self.range += 1
                except:
                    pass
            
    def __repr__(self):
        return str(self.get_result())
    
    def __float__(self):
        return float(self.get_result())
        
class SumAccumulator():
    def __init__(self):
        self.accumulator = Decimal('0')
        
    def get_result(self):
        return self.accumulator
    
    def add_element(self, element):
        try:
            self.accumulator += element
        except:
            pass      
          
    def __repr__(self):
        return str(self.get_result())
    
    def __float__(self):
        return float(self.get_result())
    
def collect_special_aggregates(els):  
    totals = els.exclude(exclude_from_reporting=True).aggregate(
            num_lots=Count('flavor__lot'),
            total_weight=Sum('flavor__lot__amount'),
            avg_lot_amount=Avg('flavor__lot__amount'),
            avg_rmc=Avg('flavor__rawmaterialcost'),
            avg_unitprice=Avg('flavor__unitprice'),
        )
    totals.update({
            'count_converted':SumAccumulator(),
            'avg_profit_ratio':AverageAccumulator(),
            'avg_unit_profit':AverageAccumulator(),
            'avg_gross_profit':AverageAccumulator(),
            'total_gross_profit':SumAccumulator(),
        })
    
    aggregated_data = {}
    aggregated_by_initials_template = {
            'num_lots':SumAccumulator(),
            'total_weight':SumAccumulator(),
            'avg_lot_amount':AverageAccumulator(),
            'avg_rmc':AverageAccumulator(),
            'avg_unitprice':AverageAccumulator(),
             'count_converted':SumAccumulator(),
             'avg_profit_ratio':AverageAccumulator(),
             'avg_unit_profit':AverageAccumulator(),
             'avg_gross_profit':AverageAccumulator(),
             'total_gross_profit':SumAccumulator(),
        }
    for initials in els.order_by('initials').values_list('initials', flat=True).distinct():
        aggregated_data[initials] = deepcopy(aggregated_by_initials_template)
    
    for e in els:
        if not e.exclude_from_reporting and e.flavor:
            aggregated_data[e.initials]['num_lots'].add_element(e.flavor.lot_set.count())
            aggregated_data[e.initials]['total_weight'].add_element(e.flavor.lot_set.aggregate(s=Sum('amount'))['s'])
            aggregated_data[e.initials]['avg_lot_amount'].add_element(e.flavor.lot_set.aggregate(a=Avg('amount'))['a'])
            aggregated_data[e.initials]['avg_rmc'].add_element(e.flavor.rawmaterialcost)
            aggregated_data[e.initials]['avg_unitprice'].add_element(e.flavor.unitprice)
            
            totals['count_converted'].add_element(1)
            aggregated_data[e.initials]['count_converted'].add_element(1)
            
            totals['avg_profit_ratio'].add_element(e.profit_ratio)
            aggregated_data[e.initials]['avg_profit_ratio'].add_element(e.profit_ratio)
            
            totals['avg_unit_profit'].add_element(e.unit_profit)
            aggregated_data[e.initials]['avg_unit_profit'].add_element(e.unit_profit)
            
            totals['avg_gross_profit'].add_element(e.gross_profit)
            aggregated_data[e.initials]['avg_gross_profit'].add_element(e.gross_profit)
            
            totals['total_gross_profit'].add_element(e.gross_profit)
            aggregated_data[e.initials]['total_gross_profit'].add_element(e.gross_profit)

    for initials in els.order_by('initials').values_list('initials', flat=True).distinct():
            aggregated_data[initials]['percent_total_gross'] = aggregated_data[initials]['total_gross_profit'].get_result()/totals['total_gross_profit'].get_result()*100
            
    aggregated_data = {
            'totals':totals,
            'initials':aggregated_data,               
        }
    return aggregated_data

def annotate_experimental_log_object(e):
    try:
        e.count_lots = e.flavor.lot_set.count()
    except:
        e.count_lots = 0
    try:
        e.sum_lot_amount = e.flavor.lot_set.aggregate(s=Sum('amount'))['s']
    except:
        e.sum_lot_amount = 0
    try:
        e.avg_lot_amount = Decimal(str(e.flavor.lot_set.aggregate(a=Avg('amount'))['a']))
    except:
        e.avg_lot_amount = 0
    try:
        e.profit_ratio = e.flavor.unitprice / e.flavor.rawmaterialcost
        e.profit_ratio = e.profit_ratio                                                         
    except:
        e.profit_ratio = 0
    try:
        e.unit_profit = e.flavor.unitprice - e.flavor.rawmaterialcost
        e.unit_profit=e.unit_profit
    except:
        e.unit_profit = 0
    try:
        e.gross_profit = e.sum_lot_amount * e.unit_profit
        e.gross_proft=e.gross_profit
    except:
        e.gross_profit = 0
#     try:
#         if e.flavor is not None:
#             e.deep_count = Lot.objects.filter(
#                     flavor__pk__in=FormulaTree.objects.filter(
#                             node_flavor=e.flavor).exclude(
#                             root_flavor=e.flavor).values_list(
#                             'root_flavor__pk',flat=True
#                         )
#                 ).count()
#         else:
#             e.deep_count = 0
#     except:
#         e.deep_count = 0
#     try:
#         if e.flavor is not None:
#             e.deep_weight = Lot.objects.filter(
#                     flavor__pk__in=FormulaTree.objects.filter(
#                             node_flavor=e.flavor).exclude(
#                             root_flavor=e.flavor).values_list(
#                             'root_flavor__pk',flat=True
#                         )
#                 ).aggregate(s=Sum('amount'))['s']
#         else:
#             e.deep_weight = 0
#     except:
#         e.deep_weight = 0
    
        
def toggle_exclude_from_reporting(e, new_val):
    if new_val == "false":
        e.exclude_from_reporting = False
    else:
        e.exclude_from_reporting = True
    e.save()
