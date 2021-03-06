import json

from decimal import Decimal, ROUND_HALF_UP
from operator import itemgetter

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.functional import wraps
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from django.views.generic.list import ListView


import reversion

from access.views import SubListView
from access.models import Flavor, Customer, FlavorSpecification
from access.forms import make_flavorspec_form, make_customerspec_form

from salesorders.controller import create_new_spec, update_spec, delete_specification
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
        return HttpResponseRedirect('/salesorders/')
    else:
        form = SalesOrderReportFileForm()
    return render(
        request,
        'salesorders/upload_report.html',
        {'form':form},
    )


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
        
    return render(
        request,
        'salesorders/sales_order_report.html',
        {
            'page_title':"Sales Orders",
            'sales_orders': sales_orders,
            'window_title':"Sales Order Report"
        },
    )

@permission_required('access.view_flavor')
def customer_report(request, customer_pk):
    customer = get_object_or_404(Customer, pk=customer_pk)
    sales_orders = SalesOrderNumber.objects.filter(customer=customer)
    
    ordered_flavors = []
    for so in sales_orders:
        for soli in so.lineitem_set.all():
            if soli.flavor not in ordered_flavors:
                ordered_flavors.append(soli.flavor)
    
    return render(
        request,
        'salesorders/customer_report.html',
        {
            'page_title':customer,
            'customer':customer,
            'sales_orders': sales_orders,
            'ordered_flavors':ordered_flavors,
            'window_title':"Sales Order Report"
        },
    )


def customer_spec_sheet(request, flavor_number, customer_pk):
    
    flavor = Flavor.objects.get(number=flavor_number)
    customer = Customer.objects.get(pk=customer_pk)

    #want customer specs and general specs that have not been replaced
    
    exclude_spec_ids = []
    customer_spec_list = []


    #add all customer specs
    for spec in FlavorSpecification.objects.filter(flavor = flavor).filter(customer = customer):
        if spec.replaces != None:
            exclude_spec_ids.append(spec.replaces.id)
            
        customer_spec_list.append(spec)
            
    #append general specs which have not been replaced
    for spec in FlavorSpecification.objects.filter(flavor = flavor).filter(customer = None).exclude(id__in=[id for id in exclude_spec_ids]):
        customer_spec_list.append(spec)
        
    #separate the specs into micro and non-micro
    micro_specs = []
    other_specs = []
    
    for spec in customer_spec_list:
        if spec.micro:
            micro_specs.append(spec)
        else:
            other_specs.append(spec)
    
    return render(
        request,
        'access/flavor/spec_sheet.html',
        {
            'flavor':flavor,
            'other_specs':other_specs,
            'micro_specs':micro_specs
        }
    )
        

            
    

@permission_required('access.view_flavor')
def customer_spec_list(request, customer_pk, flavor_number):
    page_title = "View Customer Specs"
    
    flavor = Flavor.objects.get(number=flavor_number)
    customer = get_object_or_404(Customer, pk=customer_pk)
    
    #want two lists: first one is general specs/overwritten general specs
    #second one is unique customer specs
    
    #in the general/overwritten spec list, i also want to show what spec a customer spec replaces 

    general_spec_list = []
    customer_spec_list = []

    #we want to show general specs that customer has not overridden 
    replaced_spec_ids = []
    
    for flavorspec in flavor.flavorspecification_set.all():
        if flavorspec.customer == customer:
            
            #obtain any general spec that is replaced
            if flavorspec.replaces != None:
                replaced_spec_ids.append(flavorspec.replaces.id) 
            
            #obtain the list of unique customer specs (do not replace anything, customer field != None)
            if flavorspec.replaces == None and flavorspec.customer != None:
                customer_spec_list.append(flavorspec)
                
    #first list = all specs - general specs that have been replaced - unique customer specs 
    for flavorspec in flavor.flavorspecification_set.exclude(id__in=replaced_spec_ids).exclude(id__in=[fs.id for fs in customer_spec_list]):
        edit_url = reverse('salesorders.views.edit_customer_spec', args=[customer_pk, flavor_number, flavorspec.id])
        delete_url = reverse('salesorders.views.delete_customer_spec', args=[customer_pk, flavor_number, flavorspec.id])
        general_spec_list.append((flavorspec.name, flavorspec.specification, flavorspec.micro, flavorspec.replaces, edit_url, delete_url))
        
    #second list is customer_spec_list, zip the urls to the customer spec list
    customer_spec_urls = []
    delete_urls = []
    for spec in customer_spec_list:
        customer_spec_urls.append(reverse('salesorders.views.edit_customer_spec', args=[customer_pk, flavor_number, spec.id]))
        delete_urls.append(reverse('salesorders.views.delete_customer_spec', args=[customer_pk, flavor_number, spec.id]))
    
        
    customer_spec_list = zip(customer_spec_list, customer_spec_urls, delete_urls)
    
    return render(
        request,
        'salesorders/customer_spec_list.html',
        {
            'page_title':page_title,
            'customer':customer,
            'flavor':flavor,
            'general_spec_list': general_spec_list,
            'customer_spec_list': customer_spec_list,
            'add_url': reverse('salesorders.views.edit_customer_spec', args=[customer_pk, flavor_number])
        },
    )
    
@permission_required('access.view_flavor')
def edit_customer_spec(request, customer_pk, flavor_number, spec_id=0):
    page_title = "Edit Customer Spec"
    
    flavor = Flavor.objects.get(number=flavor_number)
    customer = get_object_or_404(Customer, pk=customer_pk)  
    CustomerSpecificationForm = make_customerspec_form(flavor)
    
    return_url = reverse('salesorders.views.customer_spec_list', args=[customer_pk, flavor_number])
    
    if spec_id == 0:
        spec = None
    else:
        spec = get_object_or_404(FlavorSpecification, id=spec_id)
    
        #this is used if NOT post
        initial_data = {'pk':spec.pk,
                        'name':spec.name, 
                        'specification':spec.specification,
                        'micro':spec.micro,}

    if request.method == 'POST':
        form = CustomerSpecificationForm(request.POST)
        if form.is_valid():
            #if they are adding a new unique customer spec
            if spec_id == 0:
                    name = form.cleaned_data['name']
                    specification = form.cleaned_data['specification']
                    micro = form.cleaned_data['micro']
                    
                    create_new_spec(flavor, name, specification, micro, customer)
            
            #if they are overwriting a general spec for the first time, create a new spec
            elif spec.replaces == None and spec.customer == None: 
                #only create the customer spec if it differs from the general spec
                 if form.cleaned_data['name'] != spec.name or form.cleaned_data['specification'] != spec.specification:


                    name = form.cleaned_data['name']
                    specification = form.cleaned_data['specification']
                    micro = form.cleaned_data['micro']
                    
                    create_new_spec(flavor, name, specification, micro, customer, spec)
            #otherwise, just change the existing customer spec
            else: 
                name = form.cleaned_data['name']
                specification = form.cleaned_data['specification']
                micro = form.cleaned_data['micro']
                
                update_spec(spec, name, specification, micro)
            
            return HttpResponseRedirect(return_url)
        

    #the replace variable will tell us when to display the general spec which a customer spec replaces
    #the delete variable will tell us when to display the delete button 
        #if they are editing a general spec for the first time or adding a new customer spec do not display the delete button
        
    
    if spec_id == 0:
        replace = None
        delete = False
        initial_data = {}
    else:
        if spec.replaces == None and spec.customer != None: #unique
            replace = None 
            delete = True
        else:
            if spec.replaces == None: #general spec
                replace = spec
                initial_data = {}
                delete = False
            else: #override spec
                replace = spec.replaces
                delete = True
                
    if request.method != 'POST':
        form = CustomerSpecificationForm(initial=initial_data)
        
    
    
    delete_url = reverse('salesorders.views.delete_customer_spec', args=[customer_pk, flavor_number, spec_id])
        
    return render(
        request,
        'salesorders/edit_customer_spec.html',
        {
            'flavor': flavor,
            'customer': customer,
            'spec': spec,
            'replace': replace,
            'window_title': page_title,
            'page_title': page_title,
            'form': form,
            'delete': delete,
            'delete_url': delete_url,
            'return_url': reverse('salesorders.views.customer_spec_list', args=[customer_pk, flavor_number])
        },
    )
        
        
@permission_required('access.view_flavor')
def delete_customer_spec(request, customer_pk, flavor_number, spec_id):
    spec = get_object_or_404(FlavorSpecification, id=spec_id)
          
    delete_specification(spec)
        
    return HttpResponseRedirect(reverse('salesorders.views.customer_spec_list', args=[customer_pk, flavor_number]))
                 
            


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
    return render(
        request,
        'salesorders/sales_order_review.html',
        {
            'window_title': "Sales Order %s" % sales_order.__unicode__(),
            'sales_orders':sales_orders,
            'help_link': help_link,
            'sales_order': sales_order,
            'line_items': line_items,
            'page_title': page_title,
            'ingredients_ordered': icli.ingredients,
        },
     )

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

    return render(
        request,
        'salesorders/by_product.html',
        {
            'window_title': page_title,
            'orders':resultant_orders,
            'help_link': help_link,
            'status_message': status_message,
            'page_title':page_title,
            'get': request.GET,
        },
    )

@permission_required('access.view_flavor')
def sales_order_by_lineitem(request):
    queryset = LineItem.objects.all().extra(select={'total_sale_price':"quantity*unit_price"})
    callable_view = SubListView.as_view(
        queryset=queryset,
        paginate_by=100,
        extra_context= dict({
            'page_title':"Sales Orders",
            'month_list':None,
        }),
    )
    
    return callable_view(request)

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
#                               context=RequestContext(request))

@permission_required('access.view_flavor')
def sales_order_search(request, status_message=None):
    page_title = "Sales Orders By Number"
    help_link = "/wiki/index.php/Sales_orders"

    resultant_sales_orders = SalesOrderNumber.objects.all()
    return render(
        request,
        'salesorders/sales_order_search.html',
        {
            'orders': resultant_sales_orders,
            'help_link': help_link,
            'status_message':status_message,
            'page_title': page_title,
            'window_title':page_title,
            'get': request.GET,
        },
    )
    
def flavors_ordered(request, status_message=None):
    page_title = "Flavors Required to Fulfill Orders"
    help_link = "/wiki/index.php/Sales_orders"
    gc = GazintaCounterLI(LineItem.objects.filter(salesordernumber__open=True))
    gc.aggregate_gazintas()
    return render(
        request,
        'salesorders/flavors_ordered.html',
        {
            'status_message':status_message,
            'help_link': help_link,
            'page_title': page_title,
            'window_title':page_title,
            'flavors_ordered': gc.gazintas,
        },
    )
    
def ingredients_required(request, status_message=None):
    page_title = "Ingredients Required to Fulfill Orders"
    help_link = "/wiki/index.php/Sales_orders"
    icli = IngredientCounterLI(LineItem.objects.filter(salesordernumber__open=True))
    icli.aggregate_ingredients()
    total_cost = 0
    for ingredient, flavor_order in icli.ingredients.items():
        total_cost += flavor_order.total_cost()
    return render(
        request,
        'salesorders/ingredients_required.html',
        {
            'status_message':status_message,
            'help_link': help_link,
            'page_title': page_title,
            'window_title': page_title,
            'ingredients_required': icli.ingredients,
            'total_cost': total_cost,
        },
    )
    

def coloractivation(request):
    response_dict = {}
    color = request.GET.get('color')
    request.session['color'] = color
    response_dict['color'] = request.session.get(color)
    return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')
