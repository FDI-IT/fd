from decimal import Decimal, ROUND_HALF_UP
from operator import itemgetter

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.utils.functional import wraps
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.forms.formsets import formset_factory
from django.core.urlresolvers import reverse

from django.views.generic import list_detail


from reversion import revision


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
    
    ordered_flavors = []
    for so in sales_orders:
        for soli in so.lineitem_set.all():
            if soli.flavor not in ordered_flavors:
                ordered_flavors.append(soli.flavor)
    
    return render_to_response('salesorders/customer_report.html',
                              {
                               'page_title':customer,
                               'customer':customer,
                               'sales_orders': sales_orders,
                               'ordered_flavors':ordered_flavors,
                               'window_title':"Sales Order Report"
                               },
                              context_instance=RequestContext(request))


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
    
    return render_to_response('access/flavor/spec_sheet.html',
                          {'flavor':flavor,
                           'other_specs':other_specs,
                           'micro_specs':micro_specs})  
        

            
    

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
    
    return render_to_response('salesorders/customer_spec_list.html',
                              {
                               'page_title':page_title,
                               'customer':customer,
                               'flavor':flavor,
                               'general_spec_list': general_spec_list,
                               'customer_spec_list': customer_spec_list,
                               'add_url': reverse('salesorders.views.edit_customer_spec', args=[customer_pk, flavor_number])
                               },
                              context_instance=RequestContext(request))    
    
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
        
    return render_to_response('salesorders/edit_customer_spec.html', 
                                  {'flavor': flavor,
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
                                   context_instance=RequestContext(request))           
        
        
@permission_required('access.view_flavor')
def delete_customer_spec(request, customer_pk, flavor_number, spec_id):
    spec = get_object_or_404(FlavorSpecification, id=spec_id)
          
    delete_specification(spec)
        
    return HttpResponseRedirect(reverse('salesorders.views.customer_spec_list', args=[customer_pk, flavor_number]))
                 
            
# edit_customer_specs view no longer used
# separated the actions of overwriting general specs and adding unique customer specs
# @permission_required('access.view_flavor')
# def edit_customer_specs(request, customer_pk, flavor_number):
#     page_title = "Edit Customer Specs"
#     
#     flavor = Flavor.objects.get(number=flavor_number)
#     customer = get_object_or_404(Customer, pk=customer_pk)
#     
#     
#     SpecFormSet = formset_factory(FlavorSpecificationForm, extra=1, can_delete=True)
#     
#     if request.method == 'POST':
#         formset = SpecFormSet(request.POST)
#         if formset.is_valid():
#             
#             for form in formset.forms:
# #                 try: #need this try/except in case they click 'delete' on an empty row and save
#                     if 'DELETE' in form.cleaned_data:
#                         if form.cleaned_data[u'DELETE']==True:
#                             #if they clicked to delete a row, only delete it if it is a customer spec
#                             # otherwise, do nothing
#                             try: 
#                                 spec = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
#                                 if spec.customer != None:
#                                     spec.delete()
#                             except:
#                                 return "DELETE ERROR"
#                         else: #probably can fix this, it seems fugly
#                             if (form.cleaned_data['customer_id'] == 0 and form.cleaned_data['replaces_id'] == 0):
#                                 #if they edited a 'general' spec, make a new spec and change the 'customer' and 'replaces' field
#                                 if FlavorSpecification.objects.filter(pk=form.cleaned_data['pk']).exists():
#                                     flavorspec = FlavorSpecification()
#                                     cust = customer
#                                     replaces = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
#                                 #if they created a new customer spec, make a new spec with replaces = None
#                                 else:
#                                     flavorspec = FlavorSpecification()
#                                     cust = customer
#                                     replaces = None
#                                     
#                             
#                             #if they edited a spec that replaced a 'general' spec, do NOT make a new spec, just edit the existing spec
#                             if (form.cleaned_data['customer_id'] != 0 and form.cleaned_data['replaces_id'] != 0):
#                                 flavorspec = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
#                                 cust = customer
#                                 replaces = flavorspec.replaces
#                                 
#                             #if they edited an existing customer spec, just edit that (dont make a new spec)
#                             if(form.cleaned_data['customer_id'] != 0 and form.cleaned_data['replaces_id'] == 0):
#                                 flavorspec = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
#                                 
#                                 cust = customer
#                                 replaces = None
#                             
#                             #make sure they changed something
#                             if not FlavorSpecification.objects.filter(flavor=flavor).filter(name=form.cleaned_data['name']).filter(specification=form.cleaned_data['specification']).exists():
#                                 flavorspec.flavor = flavor
#                                 flavorspec.name = form.cleaned_data['name']
#                                 flavorspec.specification = form.cleaned_data['specification']
#                                 flavorspec.micro = form.cleaned_data['micro']
#                                 flavorspec.customer = cust
#                                 flavorspec.replaces = replaces
#                                 
#                                 flavorspec.save()                            
#                             
#                 
# #                 except:
# #                     return HttpResponseRedirect("/salesorder/customer/{{ customer.id }}/customer_specs/{{ flavor.number }}/FOOBARERROR")
# 
#             
#             redirect_url="/salesorders/customer/%s/customer_specs/%s" % (customer.id, flavor.number)
#             return HttpResponseRedirect(redirect_url)
#         
#         #if formset is not valid
#         else:
#             return render_to_response('salesorders/customer_specs.html', 
#                                   {'flavor': flavor,
#                                    'customer': customer,
#                                    'window_title': page_title,
#                                    'page_title': page_title,
#                                    'spec_rows': zip(formset.forms,),
#                                    'flavor_edit_link': '#',
#                                    'management_form': formset.management_form,
#                                    },
#                                    context_instance=RequestContext(request))
#         
#     initial_data = []       
#     
# 
#     for flavorspec in flavor.flavorspecification_set.all().order_by('replaces', 'customer'):
#         if flavorspec.customer is not None:
#             customer_id = flavorspec.customer.id
#         else:
#             customer_id = 0
#         
#         if flavorspec.replaces is not None:
#             replaces_id = flavorspec.replaces.id
#         else:
#             replaces_id = 0
#             
#     #we want to show general specs that customer has not overridden, and all customer specs 
#     exclude_spec_ids = []
#     
#     for flavorspec in flavor.flavorspecification_set.all():
#         if flavorspec.customer == customer:
#             if flavorspec.replaces != None:
#                 exclude_spec_ids.append(flavorspec.replaces.id)
#     
#     
#     #couldn't figure out how to combine the two querysets(customer = customer OR customer = None)
#     #so split it into two
#     
#     #unedited general specs
#     for flavorspec in flavor.flavorspecification_set.filter(customer=None).filter(replaces=None).exclude(id__in=exclude_spec_ids):
#         
#         initial_data.append({'pk':flavorspec.pk, 
#                              'customer_id':0, 
#                              'replaces_id':0, 
#                              'name':flavorspec.name, 
#                              'specification':flavorspec.specification, 
#                              'micro':flavorspec.micro})
#     
#     #customer specs
#     for flavorspec in flavor.flavorspecification_set.filter(customer=customer).order_by('replaces'):
#         
#         if flavorspec.replaces is not None:
#             replaces_id = flavorspec.replaces.id
#         else:
#             replaces_id = 0
#                      
#         initial_data.append({'pk':flavorspec.pk, 
#                              'customer_id':customer.id, 
#                              'replaces_id':replaces_id, 
#                              'name':flavorspec.name, 
#                              'specification':flavorspec.specification, 
#                              'micro':flavorspec.micro}) 
#         
#           
#     formset = SpecFormSet(initial=initial_data)
#              
#     spec_rows = zip(formset.forms)
#     return render_to_response('salesorders/customer_specs.html', 
#                                   {'flavor': flavor,
#                                    'customer': customer,
#                                    'window_title': page_title,
#                                    'page_title': page_title,
#                                    'spec_rows': spec_rows,
#                                    'flavor_edit_link': '#',
#                                    'management_form': formset.management_form,
#                                    'extra':spec_rows[-1],
#                                    },
#                                    context_instance=RequestContext(request))       
     
      


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
