from django.core.paginator import Paginator, InvalidPage, EmptyPage

from mysearch.forms import MainSearch

from access.models import Flavor, Ingredient, ExperimentalLog, PurchaseOrder, FEMAIngredient
from access.forms import FlavorFilterSelectForm, IngredientFilterSelectForm, ExperimentalFilterSelectForm, PurchaseOrderFilterSelectForm
from newqc.models import ProductInfo
from salesorders.models import SalesOrderNumber
from salesorders.forms import SalesOrderFilterSelectForm
from salesorders.views import *

search_spaces = {
    'flavor':(Flavor, FlavorFilterSelectForm),
    'ingredient':(Ingredient, IngredientFilterSelectForm),
    'experimental':(ExperimentalLog, ExperimentalFilterSelectForm),
    'sales_order':(SalesOrderNumber, SalesOrderFilterSelectForm),
    'fema':(FEMAIngredient, IngredientFilterSelectForm),
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
    
def process_session_order_by(request):
    # returns the order of results and saves session state about it
    # don't think I need to save session state here, but don't want to change
    # it until test coverage of search features is better
    last_search_space = request.session.get('last_space', None)
    last_order_by = request.session.get('last_order_by', None)
    if last_search_space != search_space:
        request.session.flush()
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
    return my_order_by
    
def search_guts(request, search_space, search_string):
    search_string = ms.cleaned_data['search_string']
    search_space = ms.cleaned_data['search_space']
    
    MyModel, MyFilterSelectForm = search_spaces[search_space]
        
    url = MyModel.get_absolute_url_from_softkey(search_string)
    if url:
        return HttpResponseRedirect(url)
        
    process_session_order_by
    
    filters = MyModel.build_kwargs(filterselect.data, {}, get_filter_kwargs)
    headers = MyModel.headers
    


    resultant_objects = MyModel.text_search(search_string)
    
    if filters:
        resultant_objects = resultant_objects.filter(**filters).distinct()
    
    if my_order_by:
        resultant_objects = resultant_objects.order_by(my_order_by)
    
    rows = [] 
    for obj in resultant_objects[:100]:
        inner_row = []
        for attr_name, header_name, html_attrs in headers:
            inner_row.append(obj.__getattribute__(attr_name))
        rows.append((obj, inner_row))
            
    if resultant_objects.count() > 100:
        rows.append(("%s more results." % (resultant_objects.count() - 100)))
        
    return rows
    
    
def process_into_table_rows(resultant_objects, headers):
    pass

def print_search(request):
    ms = MainSearch(request.GET)
    if ms.is_valid():
        search_string = ms.cleaned_data['search_string']
        search_space = ms.cleaned_data['search_space']
    else:
        return HttpResponseRedirect('/')
    
    process_request(search_space, search_string)
        
    page_title = "Search"
    return render_to_response('mysearch/print_search_results.html',
                              {
                               'ms':ms,
                               'filterselect': filterselect,
                               'headers': headers,
                               'rows': rows,
                               'resultant_objs': resultant_objects,
                               'page_title': page_title,
                               'window_title': page_title,
                               'get': request.GET,
                               },
                                context_instance=RequestContext(request))

def search(request):
    ms = MainSearch(request.GET)
    if ms.is_valid():
        search_string = ms.cleaned_data['search_string']
        search_space = ms.cleaned_data['search_space']
    else:
        return HttpResponseRedirect('/')
    
    
    
    rows = [] 
    for obj in resultant_objects[:100]:
        inner_row = []
        for attr_name, header_name, html_attrs in headers:
            inner_row.append(obj.__getattribute__(attr_name))
        rows.append((obj, inner_row))

    paginator = Paginator(resultant_objects, 40)
    page = int(request.GET.get('page', '1'))
    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)
    
    page_title = "Search"
    try:
        profile = request.user.get_profile()
    except:
        profile = None 
    return render_to_response('mysearch/search_results.html',
                          {
                           'profile': profile,
                           'print_link': 'javascript:search_results_popup()',
                           'ms':ms,
                           'filterselect': filterselect,
                           'headers': headers,
                           'rows': rows,
                           'list_items': objects,
                           'resultant_objs': resultant_objects,
                           'page_title': page_title,
                           'window_title': page_title,
                           'get': request.GET,
                           },
                            context_instance=RequestContext(request))
    
def alternate_rm(request):
    pass