from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from mysearch.forms import MainSearch

from access.models import Flavor, Ingredient, ExperimentalLog, PurchaseOrder, FEMAIngredient, TSR
from access.forms import FlavorFilterSelectForm, IngredientFilterSelectForm, ExperimentalFilterSelectForm, PurchaseOrderFilterSelectForm, TSRFilterSelectForm
from newqc.models import Lot
from newqc.forms import LotFilterSelectForm
from salesorders.models import SalesOrderNumber
from salesorders.forms import SalesOrderFilterSelectForm
from salesorders.views import *
from unified_adapter.models import ProductInfo
from unified_adapter.forms import ProductInfoFilterSelectForm

search_spaces = {
    'flavor':(Flavor, FlavorFilterSelectForm),
    'ingredient':(Ingredient, IngredientFilterSelectForm),
    'experimental':(ExperimentalLog, ExperimentalFilterSelectForm),
    'sales_order':(SalesOrderNumber, SalesOrderFilterSelectForm),
    'fema':(FEMAIngredient, IngredientFilterSelectForm),
    'purchase_order':(PurchaseOrder, PurchaseOrderFilterSelectForm),
    'unified':(ProductInfo, ProductInfoFilterSelectForm),
    'lot':(Lot, LotFilterSelectForm),
    'tsr':(TSR, TSRFilterSelectForm),
}

def get_filter_kwargs(qdict):
    filter_kwargs = []
    for key in qdict.keys():
        if key == 'page':
            pass
        elif key == 'search_string':
            pass
        elif key == 'search_space':
            pass
        elif key == 'order_by':
            pass
        else:
            filter_kwargs.append(key)
    return filter_kwargs

def toggle_order(order):
    if order[0] == '-':
        return order[1:]
    else:
        return "-%s" % order

def sanity_check(resultant_objects):
    if resultant_objects.count() == 1:
        return ('redirect', resultant_objects[0])
        #HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    else:
        return None

def search_guts(request, context_dict, paginate_by=None):
    """attempts to return search results while doing the least amount of work
    """    
    # reads data from the search string to get the target model and filters
    search_string = context_dict['ms'].cleaned_data['search_string']
    search_space = context_dict['ms'].cleaned_data['search_space']
    MyModel, MyFilterSelectForm = search_spaces[search_space]
    
    context_dict['search_string'] = search_string
    request.session['search_request_GET'] = request.GET.copy()
    
    # checks if the search string points directly to a primary key
    obj = MyModel.get_object_from_softkey(search_string)
    
    if obj is not None:
        return ('redirect', obj)
    # get the raw list, and do a first check on the count
    resultant_objects = MyModel.text_search(search_string).distinct()
    sc = sanity_check(resultant_objects)
    if sc: return sc
    
    # filter the data
    filterselect = MyFilterSelectForm(request.GET.copy())  
    filters = MyModel.build_kwargs(filterselect.data, {}, get_filter_kwargs)

    if filters:
        resultant_objects = resultant_objects.filter(**filters).distinct()
    sc = sanity_check(resultant_objects)
    if sc: return sc
    
    
    # so now there are actual search results, some session stuff
    # happens including ordering the data
    last_search_space = request.session.get('last_space', None)
    my_order_by = None
    if last_search_space != search_space:
        request.session['last_order_by'] = None
        request.session['search_request_GET'] = None
        request.session['last_space'] = search_space
        my_order_by = None
    else:
        my_order_by = request.GET.get('order_by', None)
        # the current order_by is defined iff the user clicks on a header
        # if the current and last orders match, then toggle the orders
        if my_order_by:
            if my_order_by[0] == '-':
                my_order_by = "-%s" % MyModel.fix_header(my_order_by[1:])
            else:
                my_order_by = MyModel.fix_header(my_order_by)
            request.session['last_order_by'] = my_order_by   
   
    if my_order_by is not None:
        resultant_objects = resultant_objects.order_by(my_order_by)
 
    if paginate_by is not None:
        paginator = Paginator(resultant_objects, paginate_by)
        page = int(request.GET.get('page', '1'))
        try:
            list_items = paginator.page(page)
        except (EmptyPage, InvalidPage):
            list_items = paginator.page(paginator.num_pages)
 
    headers = MyModel.headers   
    rows = process_rows(list_items.object_list, headers)
    context_dict.update({
        'filterselect':filterselect,
        'resultant_objs':resultant_objects,
        'MyModel':MyModel,
        'headers':headers,
        'rows':rows,
        'list_items':list_items,
    })
    
    return ('results', context_dict)

def process_rows(object_list, headers):
    for obj in object_list:
        inner_row = []
        for attr_name, header_name, html_attrs in headers:
            inner_row.append(obj.__getattribute__(attr_name))
        yield (obj, inner_row)

def search(request):
    context_dict = {}
    context_dict['ms'] = MainSearch(request.GET)
    if not context_dict['ms'].is_valid():
        return HttpResponseRedirect('/django/')
    # this is stupid. if i have a redirect type, i redirect
    # if i dont, then i reset results to the results[1] because
    # i know longer care about rediret type that was in results[0]
    # this function mutates context_dict!
    results = search_guts(request, context_dict, paginate_by=40)
    if results[0] != 'results':
        return HttpResponseRedirect(results[1].get_absolute_url())
        #return ('redirect', HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    
    context_dict['page_title'] = "Search -- %s" % context_dict['search_string']
    context_dict['window_title'] = context_dict['page_title']
    try:
        context_dict['profile'] = request.user.get_profile()
    except:
        context_dict['profile'] = None 
    context_dict['print_link'] = 'javascript:search_results_popup()'
    context_dict['get'] = request.GET

    return render_to_response(
        'mysearch/search_results.html',
        context_dict,
        context_instance=RequestContext(request)
    )

def print_search(request):
    context_dict = {}
    context_dict['ms'] = MainSearch(request.GET)
    if not context_dict['ms'].is_valid():
        return HttpResponseRedirect('/django/')
    
    # this is stupid. if i have a redirect type, i redirect
    # if i dont, then i reset results to the results[1] because
    # i know longer care about rediret type that was in results[0]
    results = search_guts(request, context_dict, paginate_by=100)
    if results[0] != 'results':
        return HttpResponseRedirect(results[1].get_absolute_url())
        #return ('redirect', HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
      
    context_dict['page_title'] = "Search Results -- %s" % context_dict['search_string']
    context_dict['window_title'] = context_dict['page_title']
    try:
        context_dict['profile'] = request.user.get_profile()
    except:
        context_dict['profile'] = None
    return render_to_response(
        'mysearch/print_search_results.html',
        context_dict,
        context_instance=RequestContext(request)
    )

def alternate_rm(request):
    context_dict = {}
    context_dict['ms'] = MainSearch(request.GET)
    if not context_dict['ms'].is_valid():
        context_dict['filterselect'] = IngredientFilterSelectForm()
        return render_to_response(
            'mysearch/alternate_rm_search_results.html',
            context_dict,
            context_instance=RequestContext(request)
        )
    
    # this is stupid. if i have a redirect type, i redirect
    # if i dont, then i reset results to the results[1] because
    # i know longer care about rediret type that was in results[0]
    # this function mutates context_dict!
    results = search_guts(request, context_dict, paginate_by=40)
    if results[0] != 'results':
        return redirect('/django/access/new_rm/rm/%s/' % results[1].rawmaterialcode)
        #return ('redirect', HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    
    context_dict['page_title'] = "Alternate Supplier For Raw Material Search -- %s" % context_dict['search_string']
    context_dict['window_title'] = context_dict['page_title']
    try:
        context_dict['profile'] = request.user.get_profile()
    except:
        context_dict['profile'] = None
    context_dict['get'] = request.GET
    return render_to_response(
        'mysearch/alternate_rm_search_results.html',
        context_dict,
        context_instance=RequestContext(request)
    )
    
def new_pin_flavor(request):
    context_dict = {}
    context_dict['ms'] = MainSearch(request.GET)
    if not context_dict['ms'].is_valid():
        context_dict['filterselect'] = FlavorFilterSelectForm()
        return render_to_response(
            'mysearch/new_pin_flavor.html',
            context_dict,
            context_instance=RequestContext(request)
        )
    
    # this is stupid. if i have a redirect type, i redirect
    # if i dont, then i reset results to the results[1] because
    # i know longer care about rediret type that was in results[0]
    # this function mutates context_dict!
    results = search_guts(request, context_dict, paginate_by=40)
    if results[0] != 'results':
        flavor = results[1]
        if flavor.gazinta.count() != 0:
            return redirect('/django/access/ingredient/pin_review/%s/' % flavor.gazinta.all()[0].id)
        return redirect('/django/access/new_rm/flavor/%s/' % results[1].number)
        #return ('redirect', HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    
    context_dict['page_title'] = "Register RM PIN for Flavor -- %s" % context_dict['search_string']
    context_dict['window_title'] = context_dict['page_title']
    try:
        context_dict['profile'] = request.user.get_profile()
    except:
        context_dict['profile'] = None
    context_dict['get'] = request.GET
    return render_to_response(
        'mysearch/new_pin_flavor.html',
        context_dict,
        context_instance=RequestContext(request)
    )
    
#last_space
#search_request_GET
#last_order_by