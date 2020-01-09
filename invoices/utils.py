from decimal import Decimal, ROUND_HALF_UP
from collections import deque
from datetime import date
from django.db.models import Q, F
from csv import writer
import os
import glob

from access.models import FormulaException, Formula, FormulaTree, LeafWeight
from access.models import Flavor, Ingredient
from invoices.report_parser import InvoiceLineGenerator, InvoiceGenerator, TotalInvoiceReportParser
from invoices.models import Invoice, LineItem

def parse_report(report_file):
    ilog = InvoiceLineGenerator(report_file)
    flavor_orders = {}
    for row in ilog:
        try:
            flavor, weight = ilog.try_line_item(row)
            if flavor:
                try:
                    flavor_orders[flavor] += weight
                except KeyError:
                    flavor_orders[flavor] = weight
        except:
            pass

        
    total_rmc = 0
    for flavor, weight in flavor_orders.items():
        try:
            rmc = flavor.update_cost()
            relative_rmc = rmc * weight
            flavor_orders[flavor] = (weight, rmc, relative_rmc)
            total_rmc += relative_rmc
        except:
            import pdb; pdb.set_trace()
        
    return total_rmc, flavor_orders

def parse_total_reports(report_dir):
    os.chdir(report_dir)
    flavor_orders = {}
    for report_file in glob.glob('./*.csv'):
        ilog = TotalInvoiceReportParser(report_file)
        
        for row in ilog:
            try:
                flavor_orders[row['flavor']].append((row['Date'], row['Qty']))
                
            except:
                flavor_orders[row['flavor']] = [(row['Date'], row['Qty'])]
            
    summarized_orders = {}    
    for k, v in flavor_orders.items():
        d_2010 = date(2010,1,1)
        summary = {
            't_2007':0,
            'n_2007':0,
            't_2010':0,
            'n_2010':0,
        } 
        for x in v:
            if x[0] > d_2010:
                summary['t_2010'] += x[1]
                summary['n_2010'] += 1
            summary['t_2007'] += x[1]
            summary['n_2007'] += 1
        summarized_orders[k] = summary
    w = writer(open('report.csv','w'))
    w.writerow(['flavor','orders since 2010','quantity since 2010','orders since 2007','quantity since 2007'])
    for k,v in summarized_orders.items():
        w.writerow([k, v['n_2010'], v['t_2010'], v['n_2007'], v['t_2007']])

    return summarized_orders
#        
#    total_rmc = 0
#    for flavor, weight in flavor_orders.iteritems():
#        try:
#            rmc = flavor.update_cost()
#            relative_rmc = rmc * weight
#            flavor_orders[flavor] = (weight, rmc, relative_rmc)
#            total_rmc += relative_rmc
#        except:
#            import pdb; pdb.set_trace()
#        
#    return total_rmc, flavor_orders

F = 0
W = 1
def parse_report_lw(report_file):
    ilg = InvoiceLineGenerator(report_file)
    flavor_orders = {}
    for r in ilg:
        try:
            fo = ilg.try_line_item(r)
            if fo:
                try:
                    flavor_orders[fo[F]] += fo[W]
                except:
                    flavor_orders[fo[F]] = fo[W]
        except Exception as e:
#            print e
#            print r
            pass
    total_rmc = Decimal('0')
    for f, w in flavor_orders.items():
        rmc = f.leaf_cost
        rel_rmc = f.leaf_cost * w
        total_rmc += rel_rmc
        flavor_orders[f] = (w, rmc, rel_rmc)
                
    return total_rmc, flavor_orders

def parse_report_multi_day(report_file):
    LineItem.objects.all().delete()
    Invoice.objects.all().delete()
    ilg = InvoiceGenerator(report_file)
    for fo in ilg:
        i,created = Invoice.objects.get_or_create(number=fo['Num'], qb_date=fo['Date'])
        flavor = fo['flavor']
        rawmaterialcost = flavor.rawmaterialcost
        quantity = fo['Qty']
        if rawmaterialcost is None:
            rawmaterialcost = 0
        quantity_cost = quantity * rawmaterialcost
        ili = LineItem(invoice=i, flavor=flavor, quantity=quantity, rawmaterialcost=rawmaterialcost, quantity_cost=quantity_cost)
        ili.save()
        