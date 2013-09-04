from decimal import Decimal, ROUND_HALF_UP
from datetime import date
import re
import copy
import operator

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.generic import list_detail
from django.http import HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.functional import wraps
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.views.generic.create_update import create_object

from reversion import revision

from unified_adapter.models import ProductInfo

from access.barcode import barcodeImg, codeBCFromString
from access.models import *
from access.my_profile import profile
from access.templatetags.review_table import review_table as legacy_explosion
from access.templatetags.ft_review_table import consolidated, explosion, production_lots, retains, raw_material_pin, gzl_ajax
from access import forms
from access.scratch import build_tree, build_leaf_weights, synchronize_price, recalculate_guts
from access.tasks import ingredient_replacer_guts
from access.forms import IngredientFilterSelectForm, FormulaEntryFilterSelectForm
from access.formula_filters import ArtNatiFilter, Prop65Filter

from solutionfixer.models import Solution, SolutionStatus

ones = Decimal('1')
tenths = Decimal('0.0')
hundredths = Decimal('0.00')
thousandths = Decimal('0.000')
ONE_THOUSAND = Decimal('1000')
ONE_HUNDRED = Decimal('100')
TEN = Decimal('10')
price_attention_threshold = Decimal('0.04')

class BatchSheetException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

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

# decorator
def flavor_info_wrapper(view):
    @wraps(view)
    def inner(request, flavor_number, *args, **kwargs):
        flavor = get_object_or_404(Flavor, number=flavor_number)
        return view(request, flavor, *args, **kwargs)
    return inner

# decorator
def po_info_wrapper(view):
    @wraps(view)
    def inner(request, po_number, *args, **kwargs):
        po = get_object_or_404(PurchaseOrder, number=po_number)
        return view(request, po, *args, **kwargs)
    return inner


# decorator
def ingredient_by_rmc_info_wrapper(view):
    @wraps(view)
    def inner(request, ingredient_rmc, *args, **kwargs):
        ingredient = get_object_or_404(Ingredient, rawmaterialcode=ingredient_rmc)
        return view(request, ingredient, *args, **kwargs)
    return inner  


# decorator
def ingredients_by_pin_info_wrapper(view):
    @wraps(view)
    def inner(request, ingredient_id, *args, **kwargs):
        ingredients = Ingredient.objects.filter(id=ingredient_id)
        return view(request, ingredients, *args, **kwargs)
    return inner      

# decorator
def experimental_wrapper(view):
    @wraps(view)
    def inner(request, experimentalnum, *args, **kwargs):
        experimental = get_object_or_404(ExperimentalLog, experimentalnum=experimentalnum)
        return view(request, experimental, *args, **kwargs)
    return inner     

@experimental_wrapper
@login_required
def experimental_edit(request, experimental):
    if request.method == 'POST':
        form = forms.ExperimentalForm(request.POST, instance=experimental)
        if form.is_valid():
            form.save()
            return redirect('/django/access/experimental/%s/' % experimental.experimentalnum)
    page_title = "Experimental Edit"
    form = forms.ExperimentalForm(instance=experimental)
    if request.user.get_profile().initials == experimental.initials or request.user.is_superuser:
        pass
    else:
        return render_to_response('access/experimental/experimental_edit_permission.html',context_instance=RequestContext(request))
    context_dict = {
                    'experimental': experimental,
                    'page_title': page_title,
                    'experimentalform':form,
                    }
    return render_to_response('access/experimental/experimental_edit.html',
                              context_dict,
                              context_instance=RequestContext(request))

@experimental_wrapper
@permission_required('access.add_flavor')
def approve_experimental(request,experimental):
    if request.method == 'POST':
        form = forms.ApproveForm(request.POST, instance=experimental.flavor)
        if form.is_valid():
            form.save()
            for gazinta in form.instance.gazintas():
                if gazinta.prefix == "EX":
                    gazinta.prefix = "GZ"
                    gazinta.approved = True
                    gazinta.save()
            experimental.product_number = form.instance.number
            experimental.save()
            return redirect(experimental.flavor.get_absolute_url())
        else:
            return render_to_response('access/experimental/approve.html',
                              {'form':form,
                               'experimental':experimental,},
                              context_instance=RequestContext(request))
    experimental.flavor.prefix = ""
    experimental.flavor.number = ""
    f = forms.ApproveForm(instance=experimental.flavor)
    return render_to_response('access/experimental/approve.html',
                              {'form':f,
                               'experimental':experimental,},
                              context_instance=RequestContext(request))

@experimental_wrapper
def experimental_add_formula(request, experimental):
    f = Flavor(number=Flavor.get_next_tempex_number(),
               name=experimental.product_name,
               prefix='EX',
               natart=experimental.natart[:3],
               experimental=experimental.experimentalnum)
    f.save()
    experimental.flavor = f
    experimental.save()
    return HttpResponseRedirect('/django/access/experimental/%s/' % experimental.experimentalnum)

@experimental_wrapper
def experimental_review(request, experimental):
    status_message = request.GET.get('status_message', "")
    page_title = "Experimental Review"
    field_details = []
    for field in experimental._meta.fields:
        field_details.append((field.verbose_name,
                              field.value_from_object(experimental)))
        
    digitized_table = []
    digitized_test_re = re.compile('\w')
    for digitizedformula in experimental.digitizedformula_set.all().order_by('pk'):
        contains_values = digitized_test_re.search(digitizedformula.raw_row)
        if contains_values:
            digitized_table.append(digitizedformula.raw_row.split("|||"))
            
    green_book_link = Flavor.get_absolute_url_from_softkey(experimental.product_number)
    
    
    context_dict = {
                        'status_message':status_message,
                        'digitized_table':digitized_table,
                        'window_title': experimental.__unicode__(),
                        'experimental': experimental,
                        'field_details': field_details,
                        'page_title': page_title,
                        'print_link':'javascript:print_experimental_review(%s)' % experimental.experimentalnum,
                        'green_book_link':green_book_link,
                        }
    if experimental.flavor is None:
        return render_to_response('access/experimental/old_experimental_review.html',
                                  context_dict,
                                  context_instance=RequestContext(request))
    else:
        dci = experimental.flavor.discontinued_ingredients
        if len(dci) != 0:
            dci_status = "Formula contains discontinued ingredients: %s" % ", ".join(dci)
            status_message = ", ".join((status_message, dci_status))
           
        context_dict['approve_link'] = experimental.get_approve_link()
        context_dict['status_message'] = status_message
        context_dict['recalculate_link'] = '/django/access/experimental/%s/recalculate/' % experimental.experimentalnum
        return render_to_response('access/experimental/experimental_review.html',
                                  context_dict,
                                  context_instance=RequestContext(request))

@experimental_wrapper    
def digitized_review(request, experimental):
    page_title = "Digitized Review"
    digitized_table = []
    digitized_test_re = re.compile('\w')
    for digitizedformula in experimental.digitizedformula_set.all():
        contains_values = digitized_test_re.search(digitizedformula.raw_row)
        if contains_values:
            digitized_table.append(digitizedformula.raw_row.split("|||"))
            
    green_book_link = Flavor.get_absolute_url_from_softkey(experimental.product_number)

    context_dict = {
                    'digitized_table':digitized_table,
                    'window_title': experimental.__unicode__(),
                    'experimental': experimental,
                    'page_title': page_title,
                    'green_book_link':green_book_link,
                    }
    return render_to_response('access/digitized/digitized_review.html',
                              context_dict,
                              context_instance=RequestContext(request))

@flavor_info_wrapper
def flavor_review(request, flavor):
    #flavor.update_cost()
    try:
        weight_factor = Decimal(str(request.GET.get('wf', 1000)))
    except:
        weight_factor = Decimal('1000')
    formula_weight = str(weight_factor)
    weight_factor = weight_factor / Decimal('1000')
    page_title = "Flavor Review"
    help_link = "/wiki/index.php/Flavor_Review"

    context_dict = {
                    'window_title': flavor.__unicode__(),
                   'flavor': flavor,
                   'help_link': help_link,
                   'page_title': page_title,
                   'weight_factor': weight_factor,
                   'formula_weight': formula_weight,
                   }   
    return render_to_response('access/flavor/flavor_review.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
@login_required
@po_info_wrapper
def po_review(request, po):
    page_title = "Purchase Order Review"
    help_link = "/wiki/index.php/Purchase_Order_Review"
    context_dict = {
                    'window_title': po.__unicode__(),
                   'po': po,
                   'help_link': help_link,
                   'page_title': page_title,
                   'print_link':'/django/access/purchase/%s/print/' % po.number,
                   }   
    return render_to_response('access/purchase/po_review.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
@login_required
@po_info_wrapper
def po_review_print(request, po):
    polis = []
    for poli in po.purchaseorderlineitem_set.all():
        poli.total = poli.quantity*poli.package_size
        polis.append(poli)
    context_dict = {
                    'x':po,
                   'po': po,
                   'polis':polis,
                   }   
    return render_to_response('access/purchase/po_review_print.html',
                              context_dict,
                              context_instance=RequestContext(request))

def location_entry(request):
    
    return render_to_response('access/location_entry.html',
                              context_instance=RequestContext(request))
#    page_title = "Location Code Entry"
#    status_message = ""
#    if request.method == 'POST':
#        LocationCodeFormSet = formset_factory(forms.LocationEntryForm)
#        formset = LocationCodeFormSet(request.POST)
#        if formset.is_valid():
#            flavor_list = {}
#            for form in formset.forms:
#                # working on form validation. validate that duplicates are not enetered?
#                try:
#                    flavor = Flavor.objects.get(form.cleaned_data['flavor_number'])
#                except:
#                    continue
#                try:
#                    ingredient_list[ingredient] = ingredient_list[ingredient] + form.cleaned_data['amount']
#                except KeyError:
#                    ingredient_list[ingredient] = form.cleaned_data['amount']
#            previous_formula_text_summary = []
#            for old_formula_row in flavor.formula_set.all():
#                previous_formula_text_summary.append("%s: %s" % (old_formula_row.ingredient, old_formula_row.amount))
#            revision.comment = "Old formula: %s" % ", ".join(previous_formula_text_summary)
#            flavor.ingredients.clear()
#            
#            for ing, amount in ingredient_list.iteritems():
#                formula_row = Formula(flavor=flavor,
#                                    ingredient=ing,
#                                    amount=amount,
#                                    acc_flavor=flavor.number,
#                                    acc_ingredient=ing.id,)
#                formula_row.save()
#                
#            flavor.save()
#            redirect_path = "/django/access/%s/recalculate/" % (flavor.number)
#            return HttpResponseRedirect(redirect_path)
#    # else:
#    initial_data, label_rows = forms.build_LocationEntryForm_formset_initial_data(flavor)
#    if len(label_rows) == 0:
#        LocationCodeFormSet = formset_factory(forms.LocationEntryForm, extra=1)
#        label_rows.append({'cost': '', 'name': ''})
#    else:
#        LocationCodeFormSet = formset_factory(forms.LocationEntryForm, extra=0)
#    formset = LocationCodeFormSet(initial=initial_data)
#    formula_rows = zip(formset.forms,
#                       label_rows)
#    
#    return render_to_response('access/flavor/formula_entry.html', 
#                                  {'flavor': flavor,
#                                   'status_message': status_message,
#                                   'window_title': page_title,
#                                   'page_title': page_title,
#                                   'formula_rows': formula_rows,
#                                   'management_form': formset.management_form,
#                                   },
#                                   context_instance=RequestContext(request))

    
def ingredient_replacer_preview(request, old_ingredient_id, new_ingredient_id):
    old_ingredient = Ingredient.get_object_from_softkey(old_ingredient_id)
    old_ingredient_gzl = LeafWeight.objects.filter(ingredient=old_ingredient).order_by('-weight')
    new_ingredient = Ingredient.get_object_from_softkey(new_ingredient_id)
    if request.method == 'POST':
        x = ingredient_replacer_guts.delay(old_ingredient, new_ingredient)
        return render_to_response('access/ingredient_replacer_preview.html',
                              {
                               'page_title': "Replacement in process",
                               'old_ingredient':old_ingredient,
                               'new_ingredient':new_ingredient,
                               'old_ingredient_gzl':old_ingredient_gzl,},
                              context_instance=RequestContext(request))
    
    return render_to_response('access/ingredient_replacer_preview.html',
                              {
                               'page_title': "Replacement preview",
                               'old_ingredient':old_ingredient,
                               'new_ingredient':new_ingredient,
                               'old_ingredient_gzl':old_ingredient_gzl,},
                              context_instance=RequestContext(request))

@login_required
def ingredient_replacer(request):
    if request.user.is_superuser:
        if request.method=='POST':
            form = forms.IngredientReplacerForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect('/django/access/ingredient_replacer_preview/%s/%s/' 
                                        % (form.cleaned_data['original_ingredient'],
                                           form.cleaned_data['new_ingredient']))
        else:
            form = forms.IngredientReplacerForm()
        return render_to_response('access/ingredient_replacer.html',
                                  {'form':form,},
                                  context_instance=RequestContext(request))
    else:
        return HttpResponseRedirect('/django/')

@flavor_info_wrapper
def ft_review(request, flavor):
    #flavor.update_cost()
    try:
        weight_factor = Decimal(str(request.GET.get('wf', 1000)))
    except:
        weight_factor = Decimal('1000')
    formula_weight = str(weight_factor)
    weight_factor = weight_factor / Decimal('1000')
    page_title = "FT Review"
    
    status_message = request.GET.get('status_message', None)
    dci = flavor.discontinued_ingredients
    if len(dci) != 0:
        status_message = "Formula contains discontinued ingredients: %s" % ", ".join(dci)
    
    context_dict = {
                    'status_message':status_message,
                    'window_title': flavor.__unicode__(),
                   'flavor': flavor,
                   'page_title': page_title,
                   'weight_factor': weight_factor,
                   'formula_weight': formula_weight,
                   'print_link':'javascript:print_review(%s)' % flavor.number,
                   'recalculate_link':'/django/access/%s/recalculate/' % flavor.number,
                   }
    if flavor.prefix == "EX":
        experimentals = flavor.experimental_log.order_by('-experimentalnum')
        if experimentals.count() > 0:
            context_dict['approve_link'] = experimentals[0].get_approve_link()
             
    return render_to_response('access/flavor/ft_review.html',
                              context_dict,
                              context_instance=RequestContext(request))


@flavor_info_wrapper
@login_required
@transaction.commit_on_success
def recalculate_flavor(request,flavor):
    old_new_attrs, flavor = recalculate_guts(flavor)
    context_dict = {
                   'window_title': flavor.__unicode__(),
                   'page_title': "Recalculate Flavor Properties",
                   'flavor': flavor,
                   'weight_factor':1000,
                   'old_new_attrs':old_new_attrs,
                   }   
    return render_to_response('access/flavor/recalculate.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
    
    
    
@experimental_wrapper
@login_required
@transaction.commit_on_success
def recalculate_experimental(request,experimental):
    flavor=experimental.flavor
    old_flavor_dict = copy.copy(flavor.__dict__)
    
    FormulaTree.objects.filter(root_flavor=flavor).delete()
    LeafWeight.objects.filter(root_flavor=flavor).delete()
    
    my_valid = True
    my_amount = 0
    for fr in flavor.formula_set.all():
        my_amount += fr.amount
        gazinta = fr.ingredient.gazinta()
        if gazinta is None:
            continue
        if gazinta.valid == False:
            my_valid = False
            break
    if my_amount != Decimal(1000):
        my_valid=False
    flavor.valid = my_valid
    
    build_tree(flavor)
    build_leaf_weights(flavor)
    my_leaf_weights = LeafWeight.objects.filter(root_flavor=flavor).select_related()
    
    sulfites = Decimal('0')
    allergens = {}
    my_prop_65 = False
    my_diacetyl = False
    my_pg = False
    my_solvents = {}
    sorted_solvent_string_list = []
    
    for lw in my_leaf_weights:
        
        sulfites += lw.ingredient.sulfites_ppm * lw.weight / ONE_THOUSAND
        
        for allergen in Ingredient.aller_attrs:
            if getattr(flavor, allergen):
                allergens[allergen]=1
                
        if lw.ingredient.prop65 == True:
            my_prop_65 = True
        if lw.ingredient.pk in DIACETYL_PKS:
            my_diacetyl = True
        if lw.ingredient.pk in PG_PKS:
            my_pg = True
            
        if lw.ingredient.id in SOLVENT_NAMES:
            my_solvents[lw.ingredient.id] = lw.weight
        
    flavor.sulfites_ppm = sulfites.quantize(tenths)
    if sulfites > 10:
        flavor.sulfites = True
        flavor.sulfites_usage_threshold = ONE_HUNDRED / (sulfites / TEN)    
    else:
        flavor.sulfites = False
        flavor.sulfites_usage_threshold = 0
        
    allergens = allergens.keys()
    if len(allergens) > 0:
        flavor.allergen = "Yes: %s" % ','.join(allergens)
        flavor.ccp2 = True
        flavor.ccp4 = True
    else:
        flavor.allergen = "None"

    flavor.prop_65 = my_prop_65
    flavor.prop65 = my_prop_65
    flavor.diacetyl = not my_diacetyl
    flavor.no_pg = not my_pg

    solvents_by_weight = sorted(my_solvents.iteritems(), key=operator.itemgetter(1))
    solvents_by_weight.reverse()
    for solvent_number, solvent_amount in solvents_by_weight:
        if solvent_amount > 0:
            relative_solvent_amount = (solvent_amount / 10).quantize(ones)
            sorted_solvent_string_list.append("%s %s%%" % (SOLVENT_NAMES[solvent_number], relative_solvent_amount))
    solvent_string = "; ".join(sorted_solvent_string_list)
    flavor.solvent = solvent_string[:50]
        
    synchronize_price(flavor)
    flavor.rawmaterialcost = flavor.rawmaterialcost.quantize(thousandths)
    flavor.save()    
    
    old_new_attrs = [
            ('Raw Material Cost',old_flavor_dict['rawmaterialcost'],flavor.rawmaterialcost),
            ('Sulfites PPM',old_flavor_dict['sulfites_ppm'],flavor.sulfites_ppm),
            ('Allergen',old_flavor_dict['allergen'],flavor.allergen),
            ('Solvent',old_flavor_dict['solvent'],flavor.solvent),    
            ('Prop 65',old_flavor_dict['prop_65'],flavor.prop65),
            ('NO Diacetyl',old_flavor_dict['diacetyl'],flavor.diacetyl),
            ('NO PG',old_flavor_dict['no_pg'],flavor.no_pg),   
            ('Valid',old_flavor_dict['valid'],flavor.valid),           
        ]
        
    
    
    context_dict = {
                    'experimental':experimental,
                   'window_title': flavor.__unicode__(),
                   'page_title': "Recalculate Flavor Properties",
                   'flavor': flavor,
                   'weight_factor':1000,
                   'old_new_attrs':old_new_attrs,
                   }   
    return render_to_response('access/experimental/recalculate.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
@flavor_info_wrapper
def print_review(request,flavor):
    info_form = forms.FlavorReviewForm(instance=flavor)
    context_dict = {
                   'window_title': flavor.__unicode__(),
                   'info_form':info_form,
                   'flavor': flavor,
                   }   
    return render_to_response('access/flavor/print_review.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
@experimental_wrapper
def experimental_print_review(request,experimental):
    try:
        info_form = forms.FlavorReviewForm(instance=experimental.flavor)
    except:
        info_form = None
    digitized_table = []
    digitized_test_re = re.compile('\w')
    for digitizedformula in experimental.digitizedformula_set.all().order_by('pk'):
        contains_values = digitized_test_re.search(digitizedformula.raw_row)
        if contains_values:
            digitized_table.append(digitizedformula.raw_row.split("|||"))
            
    context_dict = {
                    'info_form':info_form,
                    'flavor':experimental.flavor,
                   'window_title': experimental.__unicode__(),
                   'experimental': experimental,
                   'digitized_table':digitized_table,
                   }   
    return render_to_response('access/experimental/print_review.html',
                              context_dict,
                              context_instance=RequestContext(request))

@flavor_info_wrapper
def gzl(request, flavor):
    page_title = "Product Gazinta List (GZL)"       
    context_dict = {
                   'window_title': flavor.__unicode__(),
                   'product': flavor,
                   'page_title': page_title,
                   }   
    return render_to_response('access/gzl.html',
                              context_dict,
                              context_instance=RequestContext(request))


@ingredient_by_rmc_info_wrapper
def ingredient_gzl(request, ingredient):
    page_title = "Ingredient Gazitna List (GZL)"
    context_dict = {
                   'window_title': ingredient.__unicode__(),
                   'product': ingredient,
                   'page_title': page_title,
                   }   
    return render_to_response('access/gzl.html',
                              context_dict,
                              context_instance=RequestContext(request))


@ingredients_by_pin_info_wrapper
def ingredient_pin_review(request, ingredients):
    page_title = "Ingredient Review"
    updated_flavors_threshold = {}
    table_headers = (
                     "RM Code",
                     "Nat-Art",
                     "Name",
                     "Description",
                     "Supplier",
                     "Price",
                     "Last Update",
                     "Kosher",
    )
    highlighted_ingredient = ingredients[0]
    for ing in ingredients:
        if ing.discontinued == False:
            highlighted_ingredient = ing
            break
        
    if request.method == 'POST':
        icu = forms.IngredientCostUpdate(request.POST)
        if icu.is_valid():
            x =  icu.cleaned_data['new_cost']
            updated_flavors = highlighted_ingredient.update_price(icu.cleaned_data['new_cost'])
        
        if updated_flavors != True:
            for f, prices in updated_flavors.iteritems():
                try:
                    delta = prices[1] - prices[0]
                    if delta > price_attention_threshold:
                        new_profit_ratio = (f.unitprice / prices[1]).quantize(Decimal('0.000'), rounding=ROUND_HALF_UP)
                        prices.extend((delta, new_profit_ratio))
                        updated_flavors_threshold[f]=prices
                except:
                    pass
            
        
    else:
        icu = forms.IngredientCostUpdate()
        updated_flavors = {}

    context_dict = {
                    'window_title': highlighted_ingredient.__unicode__(),
                    'highlighted_ingredient': highlighted_ingredient,
                    'ingredients': ingredients,
                    'page_title': page_title,
                    'table_headers': table_headers,
                    'icu': icu,
                    'updated_flavors': updated_flavors_threshold,                   
    }
    return render_to_response('access/ingredient/ingredient_pin_review.html',
                              context_dict,
                              context_instance=RequestContext(request))


@ingredient_by_rmc_info_wrapper
def ingredient_review(request, ingredient):
    page_title = "Ingredient Review"
    field_details = []
    for field in ingredient._meta.fields:
        field_details.append((field.verbose_name,
                              field.value_from_object(ingredient)))

    context_dict = {
                    'window_title': ingredient.__unicode__(),
                   'ingredient': ingredient,
                   'field_details': field_details,
                   'page_title': page_title,
    }   
    return render_to_response('access/ingredient/ingredient_review.html',
                              context_dict,
                              context_instance=RequestContext(request))
    
    
@flavor_info_wrapper
def batch_sheet(request, flavor):
    #flavor.update_cost()
    try:
        weight_factor = Decimal(str(request.GET.get('wf', 1000)))
    except:
        weight_factor = Decimal('1000')
    weight_factor = weight_factor / Decimal('1000')
    page_title = "Batch Sheet"
    
    ingredients = flavor.formula_set.all()
    todays_date = date.today()
    # get grams equivalent
    for ingredient in ingredients:
        #ingredient.amount = ingredient.amount.quantize(hundredths, rounding=ROUND_HALF_UP)
        ingredient.grams_equivalent = Decimal(ingredient.amount * Decimal('453.59237')).quantize(hundredths, rounding=ROUND_HALF_UP)

    context_dict = {
                   'flavor': flavor,
                   'page_title': page_title,
                   'ingredients': ingredients,
                   'todays_date': todays_date,
                   }   
    return render_to_response('access/flavor/batch_sheet.html',
                              context_dict,
                              context_instance=RequestContext(request))


def flavor_search(request, status_message=None):
    page_title = "Flavor Search"
    search_string = request.GET.get('search_string', '') 
    
    try:
        resultant_flavors = Flavor.objects.filter(number__exact=int(search_string))
    except ValueError:
        resultant_flavors = Flavor.objects.filter(name__icontains=search_string)

    paginator = Paginator(resultant_flavors, 40)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    try:
        flavors = paginator.page(page)
    except (EmptyPage, InvalidPage):
        flavors = paginator.page(paginator.num_pages)
            
    return render_to_response('access/flavor/index.html', 
                              {
                               'window_title': page_title,
                               'list_items': flavors,
                               'resultant_objs': resultant_flavors,
                               'status_message': status_message,
                               'search': forms.FlavorSearch({'search_string': search_string}, label_suffix=''),
                               'page_title': page_title,
                               'get': request.GET,
                               },
                              context_instance=RequestContext(request))

def ingredient_autocomplete(request):
    """
    This returns a JSON object that is an array of objects that have 
    the following properties: id, label, value. Labels are shown to
    the user in the form of a floating dialog. 
    """
    # this is provided by the jQuery UI widget
    term = request.GET['term']
        
    # todo:
    #
    # refactor the delegated functions so that only the ingredient
    # search is actually autocompleted...not the weight.
    # also refactor the 
    #
    # the search term has to be parsed, and scanned for a number.
    # if it has a number:
    #     and if it has an f: 
    #         search for flavor numbers.
    #     else:
    #         search for product numbers
    # else:
    #     search for product names
    match = re.search(r'[0-9]+', term)
    ret_array = []
    if match:
        if len(term) == 1:
            ingredients = Ingredient.objects.filter(id=int(term))
        else:
            ingredients = Ingredient.objects.filter(id__contains=match.group())
    else:
        ingredients = Ingredient.objects.filter(product_name__icontains=term)
    for ingredient in ingredients:
        ingredient_json = {}
        ingredient_json["id"] = ingredient.id
        ingredient_json["label"] = ingredient.__unicode__()
        ingredient_json["value"] = ingredient_json["id"]
        ret_array.append(ingredient_json)
    return HttpResponse(simplejson.dumps(ret_array), content_type='application/json; charset=utf-8')


    

def process_filter_update(request):
    
    return_messages = {}
    
    for FilterClass in (ArtNatiFilter, Prop65Filter):
        checked_boxes = request.GET.getlist(FilterClass.key_string)
        if checked_boxes != []: #only execute a filter query for the current filter category if there are checked boxes
            my_query = FilterClass.get_q_list(checked_boxes)
            filtered_ingredients = Ingredient.objects.filter(my_query)
            
            filtered_pks = filtered_ingredients.values_list('pk', flat=True)
            
            for pk in map(int, request.GET.getlist('pks[]')):
                if pk not in filtered_pks: #the ingredient does not match the filter requirements 
                    if pk in return_messages: #check if there is already an message for this ingredient
                        return_messages[pk].append(FilterClass.label) #if there is, add the current category to the message list
                    else:
                        return_messages[pk] = [FilterClass.label] #if there isn't, create a message list
    

    
    return HttpResponse(simplejson.dumps(return_messages), content_type='application/json; charset=utf-8')

def process_cell_update(request):
    number = request.GET['number']
    amount = request.GET['amount']
    response_dict = {}
    try:
        ingredient = Ingredient.get_formula_ingredient(number)
        response_dict['name'] = "%s %s %s" % (
                                   ingredient.art_nati,
                                   ingredient.prefix,
                                   ingredient.product_name)
        response_dict["pk"] = ingredient.pk
        try:
            try:
                response_dict['cost'] = str(
                    Decimal(ingredient.rawmaterialcost * Decimal(amount) / 1000).quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
                
            except:
                response_dict['cost'] = str(Decimal(ingredient.unitprice * Decimal(amount) / 1000).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        except:
            response_dict['cost'] = ''
    except:
        if number == '':
            response_dict['name'] = ''
        else:
            response_dict['name'] = "Invalid Number"
        response_dict['cost'] = ''
    
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

def sanity_check(resultant_objects):
    if resultant_objects.count() == 1:
        return ('redirect', resultant_objects[0])
        #HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    else:
        return None

@login_required
@permission_required('access.change_formula')
@flavor_info_wrapper
@revision.create_on_success
@transaction.commit_on_success
def formula_entry(request, flavor, status_message=None):
    page_title = "Formula Entry"
    if request.method == 'POST':
        FormulaFormSet = formset_factory(forms.FormulaRow)
        formset = FormulaFormSet(request.POST)
        if formset.is_valid():
            ingredient_list = {}
            for form in formset.forms:
                try:
                    ingredient = Ingredient.get_formula_ingredient(form.cleaned_data['ingredient_number'])
                except KeyError:
                    continue
                try:
                    ingredient_list[ingredient] = ingredient_list[ingredient] + form.cleaned_data['amount']
                except KeyError:
                    ingredient_list[ingredient] = form.cleaned_data['amount']
            previous_formula_text_summary = []
            for old_formula_row in flavor.formula_set.all():
                previous_formula_text_summary.append("%s: %s" % (old_formula_row.ingredient, old_formula_row.amount))
            revision.comment = "Old formula: %s" % ", ".join(previous_formula_text_summary)
            flavor.ingredients.clear()
            
            for ing, amount in ingredient_list.iteritems():
                formula_row = Formula(flavor=flavor,
                                    ingredient=ing,
                                    amount=amount,
                                    acc_flavor=flavor.number,
                                    acc_ingredient=ing.id,)
                formula_row.save()
                
            flavor.save()
            redirect_path = "/django/access/%s/recalculate/" % (flavor.number)
            return HttpResponseRedirect(redirect_path)
    # else:
    initial_data, label_rows = forms.build_formularow_formset_initial_data(flavor)
    if len(label_rows) == 0:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=1)
        label_rows.append({'cost': '', 'name': ''})
    else:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=0)
        
    filterselect = FormulaEntryFilterSelectForm(request.GET.copy())
    filters = Ingredient.build_kwargs(filterselect.data, {}, get_filter_kwargs)
    resultant_objects = Ingredient.objects.all()
    if filters:
        resultant_objects = resultant_objects.filter(**filters).distinct()
    sc = sanity_check(resultant_objects)
    if sc: return sc
    
    formset = FormulaFormSet(initial=initial_data)
    formula_rows = zip(formset.forms,
                       label_rows )
  
    
    return render_to_response('access/flavor/formula_entry.html', 
                                  {'flavor': flavor,
                                   'filterselect': filterselect,
                                   'resultant_objects': resultant_objects,
                                   'status_message': status_message,
                                   'window_title': page_title,
                                   'page_title': page_title,
                                   'formula_rows': formula_rows,
                                   'management_form': formset.management_form,
                                   },
                                   context_instance=RequestContext(request))
    
@login_required
@experimental_wrapper
@revision.create_on_success
@transaction.commit_on_success
def experimental_formula_entry(request, experimental, status_message=None):
    page_title = "Experimental Formula Entry"
    status_message = ""
    if request.user.get_profile().initials == experimental.initials or request.user.is_superuser:
        pass
    else:
        return render_to_response('access/experimental/experimental_edit_permission.html',context_instance=RequestContext(request))
    flavor = experimental.flavor
    if request.method == 'POST':
        FormulaFormSet = formset_factory(forms.FormulaRow)
        formset = FormulaFormSet(request.POST)
        if formset.is_valid():
            ingredient_list = {}
            for form in formset.forms:
                try:
                    ingredient = Ingredient.get_formula_ingredient(form.cleaned_data['ingredient_number'])
                except KeyError:
                    continue
                try:
                    ingredient_list[ingredient] = ingredient_list[ingredient] + form.cleaned_data['amount']
                except KeyError:
                    ingredient_list[ingredient] = form.cleaned_data['amount']
            previous_formula_text_summary = []
            for old_formula_row in flavor.formula_set.all():
                previous_formula_text_summary.append("%s: %s" % (old_formula_row.ingredient, old_formula_row.amount))
            revision.comment = "Old formula: %s" % ", ".join(previous_formula_text_summary)
            flavor.ingredients.clear()
            rawmaterialcost = 0
            
            for ing, amount in ingredient_list.iteritems():
                rawmaterialcost = rawmaterialcost + amount * ing.unitprice
                formula_row = Formula(flavor=flavor,
                                    ingredient=ing,
                                    amount=amount,
                                    acc_flavor=flavor.number,
                                    acc_ingredient=ing.id,)
                formula_row.save()
                
            
            
            flavor.rawmaterialcost = Decimal(rawmaterialcost / 1000)
            
            flavor.save()
            redirect_path = "/django/access/experimental/%s/recalculate/" % (experimental.experimentalnum)
            return HttpResponseRedirect(redirect_path)
    # else:
    initial_data, label_rows = forms.build_formularow_formset_initial_data(flavor)
    if len(label_rows) == 0:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=1)
        label_rows.append({'cost': '', 'name': ''})
    else:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=0)
    formset = FormulaFormSet(initial=initial_data)
    formula_rows = zip(formset.forms,
                       label_rows)
    digitized_table = []
    digitized_test_re = re.compile('\w')
    for digitizedformula in experimental.digitizedformula_set.all().order_by('pk'):
        contains_values = digitized_test_re.search(digitizedformula.raw_row)
        if contains_values:
            digitized_table.append(digitizedformula.raw_row.split("|||"))
            
    return render_to_response('access/experimental/formula_entry.html', 
                                  {'experimental': experimental,
                                   'status_message': status_message,
                                   'window_title': page_title,
                                   'page_title': page_title,
                                   'formula_rows': formula_rows,
                                   'management_form': formset.management_form,
                                   'digitized_table':digitized_table,
                                   },
                                   context_instance=RequestContext(request))
    
    
    
    
    
    
    
    

@login_required
@po_info_wrapper
#@revision.create_on_success
#@transaction.commit_on_success
def po_entry(request, po):
    page_title = "Purchase Order Entry"
    status_message = ""
    POLIFormSet = inlineformset_factory(PurchaseOrder, PurchaseOrderLineItem, extra=1, form=forms.POLIForm, can_delete=True)
    if request.method == 'POST':
        formset = POLIFormSet(request.POST, instance=po)
        if formset.is_valid():
            formset.save()
            for poli in po.purchaseorderlineitem_set.all():
                poli.raw_material.date_ordered = po.date_ordered
                poli.raw_material.save()
                poli.save()
            return HttpResponseRedirect("/django/access/purchase/%s/po_entry/" % po.number)
        else:
            return render_to_response('access/purchase/poli_entry.html', 
                                  {'po': po,
                                   'status_message': status_message,
                                   'window_title': page_title,
                                   'page_title': page_title,
                                   'poli_rows': zip(formset.forms,),
                                   'management_form': formset.management_form,
                                   },
                                   context_instance=RequestContext(request))
    formset = POLIFormSet(instance=po)
#    initial_data, label_rows = forms.build_poli_formset_initial_data(po)
#    if len(label_rows) == 0:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=1)
#        label_rows.append({'cost':'', 'name':''})
#    else:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=0)
#    formset = POLIFormSet(initial=initial_data)
    poli_rows = zip(formset.forms,
                   #    label_rows)
                   )
    return render_to_response('access/purchase/poli_entry.html', 
                                  {'po': po,
                                   'status_message': status_message,
                                   'window_title': page_title,
                                   'page_title': page_title,
                                   'poli_rows': poli_rows,
                                   'management_form': formset.management_form,
                                   'extra':poli_rows[-1],
                                   },
                                   context_instance=RequestContext(request))

ajax_function = {
    'consolidated': (consolidated, 'access/flavor/consolidated.html'),
    'explosion': (explosion, 'access/flavor/explosion.html'),
    'legacy_explosion': (legacy_explosion, 'access/flavor/legacy_explosion.html'),
    'production_lots': (production_lots, 'access/flavor/production_lots.html'),
    'retains': (retains, 'access/flavor/retains.html'),    
    'raw_material_pin': (raw_material_pin, 'access/ingredient/raw_material_pin.html'),
    'gzl_ajax': (gzl_ajax, 'access/gzl_ajax.html'),
}

#def ajax_dispatch(request, template_name, flavor_number):
def ajax_dispatch(request):
    ajax_func, ajax_template = ajax_function[request.GET['tn']]
    
    return render_to_response(ajax_template,
                       ajax_func( Flavor.objects.get(pk=request.GET['pk']) ))
        #eturn HttpResponse(simplejson.dumps({'a':1}), content_type='application/json; charset=utf-8')
    
#    ingredient_json = {}
#        ingredient_json["id"] = ingredient.id
#        ingredient_json["label"] = ingredient.__unicode__()
#        ingredient_json["value"] = ingredient_json["id"]
#        ret_array.append(ingredient_json)
#    return HttpResponse(simplejson.dumps(ret_array), content_type='application/json; charset=utf-8')
    
 
def table_to_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % request.POST['flavor_number']
    response.write(request.POST['exportdata'])
    return response


def get_ingredient_option_list(request):
    option_list = []
    for ing in Ingredient.objects.all():
        option_list.append({ing.rawmaterialcode: ing.__unicode__()})
    return HttpResponse(simplejson.dumps(option_list), content_type='application/json; charset=utf-8')


def get_barcode(request, flavor_number):
    f = get_object_or_404(Flavor, number=flavor_number)
    barcode = barcodeImg(codeBCFromString(str(f.number)))
    response = HttpResponse(mimetype="image/png")
    barcode.save(response, "PNG")
    return response


# TODO : fix these; just placeholder
@login_required
@revision.create_on_success
def db_ops(request):
    return render_to_response('access/flavor/db_ops.html', {})


def process_digitized_paste(request):
    response_dict = {}
    response_dict['test'] = request.GET.get('text')
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')


@login_required
@revision.create_on_success
def digitized_entry(request):
    form = forms.DigitizedFormulaPasteForm()
    return render_to_response('access/flavor/digitized_entry.html', {'form': form})

@login_required
@revision.create_on_success
def new_po(request):
    return create_object(request, 
                         form_class=forms.PurchaseOrderForm, 
                         template_name="access/purchase/new.html",
                         post_save_redirect="/django/access/purchase/%(number)s/po_entry/",)


def jil_object_list(request):
    queryset = JIList.objects.all()
    return list_detail.object_list(
            request,
            paginate_by=100,
            queryset=queryset,
            extra_context= {
                    'page_title': "Similar Flavrors",
                },
        )

@login_required
def new_rm_wizard(request):
    return forms.NewRMWizard([forms.NewRMForm1, forms.NewRMForm11, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5])(request)

@login_required
@flavor_info_wrapper
def new_rm_wizard_flavor(request, flavor):
    ingredients = Ingredient.objects.filter(sub_flavor=flavor)
#    print ingredients
    if ingredients.count()!=0:
        return redirect(ingredients[0].get_absolute_url())
    if flavor.prop65 == True:
        my_prop_65 = 1
    else:
        my_prop_65 = 0
    if flavor.microtest == "Yes":
        my_microsensitive = 1
    else:
        my_microsensitive = 0
    
    allers = []
    for aller in Ingredient.aller_attrs:
        if getattr(flavor, aller) == True:
            allers.append(aller)
    if len(allers) == 0:
        allers = ["None"]
    
    initial = {
        0:{
           'art_nati':flavor.natart,
           'prefix':"%s-%s" % (flavor.prefix, flavor.number),
           'product_name':"%s %s" % (flavor.name, flavor.label_type),
           },
        1:{
           'unitprice':flavor.rawmaterialcost,
           'purchase_price_update':flavor.lastspdate,
           'suppliercode':"FDI",
           'package_size':0,
           'minimum_quantity':0,
           'fob_point':"FDI",
           'lead_time':0,
           },
        2:{
           'kosher':flavor.kosher,
           'kosher_code':flavor.kosher_id,
           },
        3:{
           'hazardous':0,
           'microsensitive':my_microsensitive,
           'prop65':my_prop_65,
           'nutri':0,
           },
        4:{
           'sulfites_ppm':flavor.sulfites_ppm,
           'allergens':allers,
           
           },
        'extra_flavor':{
            'sub_flavor_id':flavor.id,
            'flavornum':flavor.number,
            'solubility_memo':flavor.solvent,
            },
    }
    request.session['new_solution_wizard_initial'] = initial
    return forms.NewRMWizard([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial=initial)(request)


SOLVENT_NAMES = {
    1983:'Neobee',
    829:'Triacetin',
    86:'Benzyl Alcohol',
    703:'PG',
    321:'ETOH',
    100:'Water',
    473:'Lactic Acid',
    25:'Iso Amyl Alcohol',
    758:'Soybean Oil',
}

@login_required
def new_solution_wizard(request):
    if request.method == "POST":
        return forms.NewRMWizard([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial=request.session['new_solution_wizard_initial'])(request)
    form = forms.NewSolutionForm(request.GET)
    if form.is_valid():
        base_ingredient = Ingredient.get_obj_from_softkey(form.cleaned_data['PIN'])
        solvent = Ingredient.get_obj_from_softkey(form.cleaned_data['solvent'])
        concentration = form.cleaned_data['concentration'][:-1]
        try:
            solutions = Solution.objects.filter(my_base=base_ingredient).filter(my_solvent=solvent).filter(percentage=concentration)
            if solutions.count() != 0:
                return redirect('/django/access/ingredient/pin_review/%s/' % solutions[0].ingredient.id)
        except:
            pass
        new_name = "%s(%s) %s%% in %s" % (base_ingredient.product_name, base_ingredient.id, concentration, SOLVENT_NAMES[solvent.id])
        concentration_decimal = Decimal(concentration)/100
        allers = []
        for aller in Ingredient.aller_attrs:
            if getattr(base_ingredient, aller) == True:
                allers.append(aller)
        if len(allers) == 0:
            allers = ["None"]
        component_price = base_ingredient.unitprice * concentration_decimal
        solvent_price = solvent.unitprice * (1-concentration_decimal)
        unit_price = (component_price + solvent_price).quantize(thousandths)
        if base_ingredient.prop65:
            prop65 = 1
        else:
            prop65 = 0
        if base_ingredient.microsensitive:
            microsensitive = 1
        else:
            microsensitive = 0
        #print component_price+solvent_price
        initial = {
            0:{
               'art_nati':base_ingredient.art_nati,
               'prefix':base_ingredient.prefix,
               'product_name':new_name,
               },
            1:{
               'unitprice':unit_price,
               'purchase_price_update':base_ingredient.purchase_price_update,
               'suppliercode':"FDI",
               'package_size':0,
               'minimum_quantity':0,
               'fob_point':"FDI",
               'lead_time':0,
               },
            2:{
               'kosher':base_ingredient.kosher,
               'kosher_code':base_ingredient.kosher_code,
               'lastlkoshdt':base_ingredient.lastkoshdt,
               },
            3:{
               'hazardous':0,
               'cas':base_ingredient.cas,
               'fema':base_ingredient.fema,
               'natural_document_on_file':base_ingredient.natural_document_on_file,
               'microsensitive':microsensitive,
               'prop65':prop65,
               'nutri':0,
               },
            4:{
               'allergens':allers,
               'sulfites_ppm':(base_ingredient.sulfites_ppm * concentration_decimal).quantize(tenths)
               },
            'extra_solution':{
                'solution':concentration,
                'solvent':solvent.product_name[:10],
                'my_base_pk':base_ingredient.pk,
                'my_solvent_pk':solvent.pk,
                },
        }
        request.session['new_solution_wizard_initial'] = initial
        return forms.NewRMWizard([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial=initial)(request)
    f = forms.NewSolutionForm()
    return render_to_response('access/new_solution.html',
                              {'form':f})

#            new_ingredient = Ingredient(art_nati=base_ingredient.art_nati,
#                                        prefix=base_ingredient.prefix,
#                                        product_name=new_name,
#                                        unitprice=component_price+solvent_price,
#                                        suppliercode="FDI",
#                                        kosher=base_ingredient.kosher,
#                                        solution=concentration,
#                                        solvent=solvent.product_name[:10],
#                                        gmo=base_ingredient.gmo,
#                                        cas=base_ingredient.cas,
#                                        fema=base_ingredient.fema,
#                                        allergen=base_ingredient.allergen,
#                                        prop65=base_ingredient.prop65,
#                                        sulfites=base_ingredient.sulfites,
#                                        sulfites_ppm=base_ingredient.sulfites_ppm * concentration_decimal,
#                                        eggs=base_ingredient.eggs,
#                                        fish=base_ingredient.fish,
#                                        milk=base_ingredient.milk,
#                                        peanuts=base_ingredient.peanuts,
#                                        soybeans=base_ingredient.soybeans,
#                                        treenuts=base_ingredient.treenuts,
#                                        wheat=base_ingredient.wheat,
#                                        sunflower=base_ingredient.sunflower,
#                                        sesame=base_ingredient.sesame,
#                                        mollusks=base_ingredient.mollusks,
#                                        mustard=base_ingredient.mustard,
#                                        celery=base_ingredient.celery,
#                                        lupines=base_ingredient.lupines,
#                                        yellow_5=base_ingredient.yellow_5,
#                                        crustacean=base_ingredient.crustacean,
#                                        )
#            new_ingredient.save()
#            s = Solution(ingredient=new_ingredient,
#                         my_base=base_ingredient,
#                         my_solvent=solvent,
#                         percentage=concentration,
#                         status=SolutionStatus.objects.get(status_name__iexact="verified"))
#            s.save()
#            return redirect('/django/access/ingredient/pin_review/%s/' % new_ingredient.id)


def allergen_list(request):
    
    return render_to_response('access/allergen_list.html',
                              {'flavors':Flavor.objects.exclude(allergen__iexact="None")}
                              )
    
def rm_allergen_list(request):
    
    return render_to_response('access/rm_allergen_list.html',
                              {'rms':Ingredient.objects.exclude(allergen__iexact="None")}
                              )

@login_required
def new_rm_wizard_launcher(request):
    return render_to_response('access/new_rm_wizard_launcher.html')


@login_required
@permission_required('access.add_experimentallog')
def new_ex_wizard(request):
    return forms.NewExFormWizard([forms.NewExForm1,forms.NewExForm2,forms.NewExForm3])(request)

@login_required
def new_rm_wizard_rm(request, ingredient_pk):
    i = Ingredient.objects.get(pk=ingredient_pk)
    allers = []
    for aller in Ingredient.aller_attrs:
        if getattr(i, aller) == True:
            allers.append(aller)
    if len(allers) == 0:
        allers = ["None"]
        
    initial = {
        0:{
           'art_nati':i.art_nati,
           'prefix':i.prefix,
           'product_name':i.product_name,
           'part_name2':i.part_name2,
           'description':i.description,
           },
        1:{
           'comments':i.comments,
           'solubility':i.solubility,
           'solubility_memo':i.solubility_memo,
           },
        3:{
           'cas':i.cas,
           'fema':i.fema,
           'hazardous':1 if i.hazardous else 0,
           'microsensitive':1 if i.microsensitive else 0,
           'prop65':1 if i.prop65 else 0,
           'nutri':1 if i.nutri else 0,
           },
        4:{
           'sulfites_ppm':i.sulfites_ppm,
           'allergens':allers,
           },
        'extra_rm':{
                'id':i.id,
                },
    }
    return forms.NewRMWizard([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial=initial)(request)