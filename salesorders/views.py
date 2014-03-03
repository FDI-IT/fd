from decimal import Decimal, ROUND_HALF_UP
from operator import itemgetter

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.utils.functional import wraps
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required

from django.views.generic import list_detail


from reversion import revision


from access.models import Flavor, Customer

from salesorders.utils import GazintaCounterLI, IngredientCounterLI, parse_orders
from salesorders.models import SalesOrderNumber, LineItem
from salesorders.forms import SalesOrderSearch, SalesOrderFilterSelectForm, SalesOrderReportFileForm, ColorActivationForm

# TODO alter these from newqc to salesorders
STATUS_BUTTONS =  {
    'repeat_link': 'javascript:ajax_retain_status_change("Resample")',
    'repeat_link_alt': 'Resample',
    'pause_link': 'javascript:ajax_retain_status_change("Hold")',
    'pause_link_alt': 'Hold',
    'accept_link': 'javascript:ajax_retain_status_change("Passed")',
    'accept_link_alt': 'Pass',
    'del_link': 'javascript:ajax_retain_status_change("Rejected")',
    'del_link_alt': 'Reject',
}


@permission_required('access.view_flavor')
def upload_report(request):
    if request.method =='POST':
        form = SalesOrderReportFileForm(request.POST, request.FILES)
        if form.is_valid():
            parse_orders(request.FILES['file'])
        return HttpResponseRedirect('/django/salesorders/')
    else:
        form = SalesOrderReportFileForm()
    return render_to_response('salesorders/upload_report.html', 
                              {'form':form},
                              context_instance=RequestContext(request))


def sales_order_info_wrapper(view):
    @wraps(view)
    def inner(request, sales_order_number, *args, **kwargs):
        sales_order = get_object_or_404(SalesOrderNumber, number=sales_order_number)
        return view(request, sales_order, *args, **kwargs)
    return inner

@permission_required('access.view_flavor')
def sales_order_report(request):
    sales_orders = []
    so_by_due_date = {}
    for so in SalesOrderNumber.objects.all():
        try:
            li = so.lineitem_set.all().order_by('due_date')[0]
            so_by_due_date[li.due_date].append(so)
        except:
            so_by_due_date[li.due_date] = [so,]
    
    due_dates = so_by_due_date.keys()
    due_dates.sort()
    for dd in due_dates:
        sales_orders.extend(so_by_due_date[dd])
        
    return render_to_response('salesorders/sales_order_report.html',
                              {
                               'page_title':"Sales Orders",
                               'sales_orders': sales_orders,
                               'window_title':"Sales Order Report"
                               },
                              context_instance=RequestContext(request))

@permission_required('access.view_flavor')
def customer_report(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    sales_orders = SalesOrderNumber.objects.filter(customer=customer)
    return render_to_response('salesorders/customer_report.html',
                              {
                               'page_title':customer,
                               'sales_orders': sales_orders,
                               'window_title':"Sales Order Report"
                               },
                              context_instance=RequestContext(request))


@permission_required('access.view_flavor')
@sales_order_info_wrapper
def sales_order_review(request, sales_order):
    hundredths = Decimal('0.00')
    page_title="Sales Order Review"
    help_link = "/wiki/index.php/Sales_orders"
    icli = IngredientCounterLI(LineItem.objects.filter(salesordernumber=sales_order))
    icli.aggregate_ingredients()
    line_items = []
    sales_orders = SalesOrderNumber.objects.filter(customer=sales_order.customer)
    for li in sales_order.lineitem_set.all():
        li.rmc = 0
        li.profitmargin = 0
        li.unit_price = li.unit_price.quantize(hundredths, rounding=ROUND_HALF_UP)
        try:
            li.rmc = li.flavor.rawmaterialcost * li.quantity
            li.rmc = li.rmc.quantize(hundredths, rounding=ROUND_HALF_UP)
            li.profitmargin = li.unit_price / li.rmc
            li.profitmargin = str(round(li.profitmargin,2))
        except:
            pass
        line_items.append(li)  
    return render_to_response('salesorders/sales_order_review.html',
                              {
                               'window_title': "Sales Order %s" % sales_order.__unicode__(),
                               'sales_orders':sales_orders,
                               'help_link': help_link,
                               'sales_order': sales_order,
                               'line_items': line_items,
                               'page_title': page_title,
                               'ingredients_ordered': icli.ingredients,
                               },
                              context_instance=RequestContext(request))

@permission_required('access.view_flavor')
def sales_order_by_product(request, status_message=None):
    page_title="Sales Orders by Product"
    help_link = "/wiki/index.php/Sales_orders"
    hundredths = Decimal('0.00')
    orders= {}
    for order in LineItem.objects.filter(salesordernumber__open=True):
        try:
            orders[order.flavor] += [order]
        except KeyError:
            orders[order.flavor] = [order]
           # 
    summarized_orders = []
    for flavor, details in orders.items():
        total = Decimal('0')
        for detail in details:
            total += detail.quantity
        try:
            totalcost = flavor.rawmaterialcost * total
            totalcost = totalcost.quantize(hundredths, rounding=ROUND_HALF_UP)
            #flavor.update_cost()
        except:
            totalcost = 0
        summarized_orders.append({'flavor': flavor,
                                  'total': total,
                                  'details':details,
                                  'totalcost':totalcost,
                                  })
    summarized_orders = sorted(summarized_orders, key=itemgetter('total'))
    resultant_orders = summarized_orders

    return render_to_response('salesorders/by_product.html',
                              {
                               'window_title': page_title,
                               'orders':resultant_orders,
                               'help_link': help_link,
                               'status_message': status_message,
                               'page_title':page_title,
                               'get': request.GET,},
                               context_instance=RequestContext(request))

@permission_required('access.view_flavor')
def sales_order_by_lineitem(request):
    queryset = LineItem.objects.all().extra(select={'total_sale_price':"quantity*unit_price"})
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset=queryset,
        extra_context= dict({
            'page_title':"Sales Orders",
            'month_list':None,
        },),
    )

#@permission_required('access.view_flavor')
#def sales_order_by_lineitem(request, status_message=None):
#    hundredths = Decimal('0.00')
#    page_title="Sales Orders by Line Item"
#    help_link = "/wiki/index.php/Sales_orders"
#    initialcolor = request.session.get('color', False)
#    lineitems = LineItem.objects.filter(salesordernumber__open=True)
#    for li in lineitems:
#
#        try:
#            li.profitmargin = li.unit_price / li.flavor.rawmaterialcost
#            li.profitmargin = li.profitmargin.quantize(hundredths, rounding=ROUND_HALF_UP)
#        except:
#            li.profitmargin = 0
#        try:
#            li.rmc = li.flavor.rawmaterialcost * li.quantity
#            li.rmc = li.rmc.quantize(hundredths, rounding=ROUND_HALF_UP)
#        except:
#            li.rmc = 0
#    
#    coloractivationform = ColorActivationForm(
#                            initial= {'color': False})
#
#    return render_to_response('salesorders/by_lineitem.html',
#                              {
#                               'coloractivationform': coloractivationform,
#                               'help_link': help_link,
#                               'lineitems': lineitems,
#                               'status_message': status_message,
#                               'page_title':page_title,
#                               'window_title':page_title,
#                               'get': request.GET,},
#                               context_instance=RequestContext(request))

@permission_required('access.view_flavor')
def sales_order_search(request, status_message=None):
    page_title = "Sales Orders By Number"
    help_link = "/wiki/index.php/Sales_orders"

    resultant_sales_orders = SalesOrderNumber.objects.all()
    return render_to_response('salesorders/sales_order_search.html', 
                              {
                               'orders': resultant_sales_orders,
                               'help_link': help_link,
                               'status_message':status_message,
                               'page_title': page_title,
                               'window_title':page_title,
                               'get': request.GET,},
                               context_instance=RequestContext(request))
    
def flavors_ordered(request, status_message=None):
    page_title = "Flavors Required to Fulfill Orders"
    help_link = "/wiki/index.php/Sales_orders"
    gc = GazintaCounterLI(LineItem.objects.filter(salesordernumber__open=True))
    gc.aggregate_gazintas()
    return render_to_response('salesorders/flavors_ordered.html',
                              {
                               'status_message':status_message,
                               'help_link': help_link,
                               'page_title': page_title,
                               'window_title':page_title,
                               'flavors_ordered': gc.gazintas,
                               },
                               context_instance=RequestContext(request))
    
def ingredients_required(request, status_message=None):
    page_title = "Ingredients Required to Fulfill Orders"
    help_link = "/wiki/index.php/Sales_orders"
    icli = IngredientCounterLI(LineItem.objects.filter(salesordernumber__open=True))
    icli.aggregate_ingredients()
    total_cost = 0
    for ingredient, flavor_order in icli.ingredients.items():
        total_cost += flavor_order.total_cost()
    return render_to_response('salesorders/ingredients_required.html',
                              {
                               'status_message':status_message,
                               'help_link': help_link,
                               'page_title': page_title,
                               'window_title': page_title,
                               'ingredients_required': icli.ingredients,
                               'total_cost': total_cost,
                               },
                               context_instance=RequestContext(request))    
    

def coloractivation(request):
    response_dict = {}
    color = request.GET.get('color')
    request.session['color'] = color
    response_dict['color'] = request.session.get(color)
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')
