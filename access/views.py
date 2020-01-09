# -*- coding: utf-8 -*-

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import re
import copy
import operator
import json
import logging
import ast
import os
import sys

from decimal import ROUND_HALF_UP

from django import template
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.list import ListView
from django.views.generic.dates import ArchiveIndexView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core import serializers
from django.utils.functional import wraps
from django.template import RequestContext
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Sum, Avg
from django.urls import reverse
from django.core.files.uploadedfile import UploadedFile
from django.core.files import File
from django import forms

import reversion

from access.training_questions_revised import *
from access.controller import reconcile_flavor, reconcile_update, discontinue_ingredient, activate_ingredient
#from access.formatter import formulatree_to_jsinfovis
from access.barcode import barcodeImg, codeBCFromString
from access.models import *
from access.my_profile import profile
from access.templatetags.review_table import review_table as legacy_explosion
from access.templatetags.ft_review_table import documentation, similar_flavors, consolidated, consolidated_indivisible, explosion, spec_sheet, customer_info, production_lots, retains, raw_material_pin, gzl_ajax, revision_history
from access import forms
from access.scratch import build_tree, build_leaf_weights, synchronize_price, recalculate_flavor, recalculate_guts
from access.tasks import ingredient_replacer_guts
from access.forms import FormulaEntryFilterSelectForm, FormulaEntryExcludeSelectForm, make_flavorspec_form, make_tsr_form, GHSReportForm, CasFemaSpreadsheetsFileForm, searchForm, flavorNumberForm, nutriForm, nutriFormTemp,spec_sheet_form, coa_form
from access.formula_filters import ArtNatiFilter, MiscFilter, AllergenExcludeFilter

# Billy's code
from access.ghs_analysis import get_ghs_only_ingredients, get_fdi_only_ingredients, write_ghs_report, write_fdi_report
from access.fema_cas import initialFormData, initialFormData_errors, initialFormData_changes, makeSelectedChanges, find_pending_changes_from_cas_fema_files

from solutionfixer.models import Solution
from one_off.mtf import *
from salesorders.controller import delete_specification, create_new_spec, update_spec
from pluggable.csv_unicode_wrappers import UnicodeWriter

from hazards.models import IngredientCategoryInfo, HazardClass, HazardCategory, GHSIngredient
from hazards.views import get_sds_info, hazard_calculator

from newqc.models import RMRetain, ReceivingLog, Lot, Retain
from newqc.forms import ReceivingLogStaticForm, ReceivingLogDynamicForm, RMInventoryForm

from salesorders.models import SalesOrderNumber, LineItem
from rest_framework import viewsets
from access.serializers import *


ones = Decimal('1')
tenths = Decimal('0.0')
hundredths = Decimal('0.00')
thousandths = Decimal('0.000')
ONE_THOUSAND = Decimal('1000')
ONE_HUNDRED = Decimal('100')

TEN = Decimal('10')
price_attention_threshold = Decimal('0.04')

#list_detail is now depracated, use this subclass of ListView instead
class SubListView(ListView):
    extra_context = {}
    def get_context_data(self, **kwargs):
        context = super(SubListView, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

class BatchSheetException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def get_filter_kwargs(qdict):
    filter_kwargs = []
    for key in list(qdict.keys()):
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
def experimental_edit(request, experimental):
    if request.method == 'POST':
        form = forms.ExperimentalForm(request.POST, instance=experimental)
        if form.is_valid():
            form.save()
            experimental.process_changes_to_flavor()
            return redirect('/access/experimental/%s/' % experimental.experimentalnum)
    else:
        form = forms.ExperimentalForm(instance=experimental)
    page_title = "Experimental Edit"

#     if request.user.userprofile.initials == experimental.initials or request.user.is_superuser:
#         pass
#     else:
#         return render(request, 'access/experimental/experimental_edit_permission.html', )

    foobar = form.iter_fieldsets()
    # foobar1 = form.as_fieldset_p()

    context_dict = {
                    'experimental': experimental,
                    'page_title': page_title,
                    'experimentalform':form,
                    }

    return render(request, 'access/experimental/experimental_edit.html', context_dict)

@reversion.create_revision()
@transaction.atomic
@experimental_wrapper
@permission_required('access.add_flavor')
def approve_experimental(request,experimental):
    if request.method == 'POST':
        form = forms.ApproveForm(request.POST, instance=experimental.flavor)
        if form.is_valid():
            old_ex_number = experimental.product_number
            experimental_approve_from_form(form, experimental)
            reversion.set_comment("Approved. Old ex number: %s." % old_ex_number)
            return redirect(experimental.flavor.get_absolute_url())
        else:
            return render(request, 'access/experimental/approve.html', {'form':form, 'experimental':experimental,})
    experimental.flavor.prefix = ""
    experimental.flavor.number = ""
    attr_list = (
            'mixing_instructions',
            'color',
            'organoleptics',
            'natart',
            'organic_compliant_required',
            'organic_certified_required',
            'liquid',
            'dry',
            'spraydried',
            'natural_type',
            'wonf',
            'flavorcoat',
            'concentrate',
            'oilsoluble',
            'label_type',
        )
    for attr in attr_list:
        setattr(experimental.flavor, attr, getattr(experimental,attr))
    # this doesn't fit in the above loop because names of attrs differ
    experimental.flavor.productmemo = experimental.memo
    f = forms.ApproveForm(instance=experimental.flavor)
    return render(request, 'access/experimental/approve.html', {'form':f,
                               'experimental':experimental,})

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
    return HttpResponseRedirect('/access/experimental/%s/' % experimental.experimentalnum)

@experimental_wrapper
def experimental_review(request, experimental):
    # labuser = False
    # if request.user.groups.filter(name='Lab').exists() or request.user.is_superuser:
    #     labuser = True

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
                        'window_title': experimental.__str__(),
                        'experimental': experimental,
                        # 'labuser':labuser,
                        'field_details': field_details,
                        'page_title': page_title,
                        'print_link':'javascript:print_experimental_review(%s)' % experimental.experimentalnum,
                        'green_book_link':green_book_link,
                        }
    if experimental.flavor is None:
        return render(request, 'access/experimental/old_experimental_review.html', context_dict)
    else:
        dci = experimental.flavor.discontinued_ingredients
        if len(dci) != 0:
            dci_status = "Formula contains discontinued ingredients: %s" % ", ".join(dci)
            status_message = ", ".join((status_message, dci_status))

        context_dict['approve_link'] = experimental.get_approve_link()
        context_dict['status_message'] = status_message
        context_dict['recalculate_link'] = '/access/experimental/%s/recalculate/' % experimental.experimentalnum
        context_dict['experimental_edit_link'] = '#'
        return render(request, 'access/experimental/experimental_review.html', context_dict)
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
                    'window_title': experimental.__str__(),
                    'experimental': experimental,
                    'page_title': page_title,
                    'green_book_link':green_book_link,
                    }
    return render(request, 'access/digitized/digitized_review.html', context_dict)

@flavor_info_wrapper
def flavor_review(request, flavor):
    #flavor.update_cost()
    # labuser = False
    # if(request.user.groups.get(name="Lab")):
    #     labuser = True

    try:
        weight_factor = Decimal(str(request.GET.get('wf', 1000)))
    except:
        weight_factor = Decimal('1000')
    formula_weight = str(weight_factor)
    weight_factor = weight_factor / Decimal('1000')
    page_title = "Flavor Review"
    help_link = "/wiki/index.php/Flavor_Review"

    context_dict = {
                    # 'labuser':labuser,
                    'window_title': flavor.__str__(),
                    'flavor': flavor,
                    'help_link': help_link,
                    'page_title': page_title,
                    'weight_factor': weight_factor,
                    'formula_weight': formula_weight,
                   }
    return render(request, 'access/flavor/flavor_review.html', context_dict)

@login_required
def tsr_review(request, tsr_number):
    tsr = TSR.objects.get(number=tsr_number)
    page_title = "TSR Review"
    help_link = "/wiki/index.php/Purchase_Order_Review"
    context_dict = {
                    'window_title': tsr.__str__(),
                   'tsr': tsr,
                   'help_link': help_link,
                   'page_title': page_title,
                   'print_link':'/access/purchase/%s/print/' % tsr.number,
                   }
    return render(request, 'access/tsr/tsr_review.html', context_dict)

@login_required
@po_info_wrapper
def po_review(request, po):
    page_title = "Purchase Order Review"
    help_link = "/wiki/index.php/Purchase_Order_Review"
    context_dict = {
                    'window_title': po.__str__(),
                   'po': po,
                   'help_link': help_link,
                   'page_title': page_title,
                   'print_link':'/access/purchase/%s/print/' % po.number,
                   }
    return render(request, 'access/purchase/po_review.html', context_dict)

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
    return render(request, 'access/purchase/po_review_print.html', context_dict)

def location_entry(request):

    return render(request, 'access/location_entry.html', )
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
#            reversion.revision.comment = "Old formula: %s" % ", ".join(previous_formula_text_summary)
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
#            redirect_path = "/access/%s/recalculate/" % (flavor.number)
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
#                                   context=RequestContext(request))


def ingredient_replacer_preview(request, old_ingredient_id, new_ingredient_id):
    old_ingredient = Ingredient.get_object_from_softkey(old_ingredient_id)
    old_ingredient_gzl = LeafWeight.objects.filter(ingredient=old_ingredient).order_by('-weight')
    new_ingredient = Ingredient.get_object_from_softkey(new_ingredient_id)
    if request.method == 'POST':
        x = ingredient_replacer_guts.delay(old_ingredient, new_ingredient)
        return render(
            request,
            'access/ingredient_replacer_preview.html',
            {
                'page_title': "Replacement in process",
                'old_ingredient':old_ingredient,
                'new_ingredient':new_ingredient,
                'old_ingredient_gzl':old_ingredient_gzl,
            },
        )

    return render(
        request,
        'access/ingredient_replacer_preview.html',
        {
            'page_title': "Replacement preview",
            'old_ingredient':old_ingredient,
            'new_ingredient':new_ingredient,
            'old_ingredient_gzl':old_ingredient_gzl,
        },
    )

@login_required
def ingredient_replacer(request):
    if request.user.is_superuser:
        if request.method=='POST':
            form = forms.IngredientReplacerForm(request.POST)
            if form.is_valid():
                return HttpResponseRedirect('/access/ingredient_replacer_preview/%s/%s/'
                                        % (form.cleaned_data['original_ingredient'],
                                           form.cleaned_data['new_ingredient']))
        else:
            form = forms.IngredientReplacerForm()
        return render(request, 'access/ingredient_replacer.html', {'form':form,})
    else:
        return HttpResponseRedirect('/')

@flavor_info_wrapper
def ft_review(request, flavor):
    # register = template.Library()
    #
    # @register.filter(name='has_group')
    # def has_group(user, group_name):
    #     group = Group.objects.get(name=group_name)
    #     return True if group in user.groups.all() else False
    #flavor.update_cost()
    # labuser = False
    # if request.user.groups.filter(name='Lab').exists() or request.user.is_superuser:
    #     labuser = True

    try:
        weight_factor = Decimal(str(request.GET.get('wf', 1000)))
    except:
        weight_factor = Decimal('1000')
    formula_weight = str(weight_factor)
    weight_factor = weight_factor / Decimal('1000')
    page_title = "FT Review"

#     status_message = request.GET.get('status_message', None)

    status_message = flavor.status

    #ingredient statement
    if IngredientStatement.objects.filter(flavor=flavor).exists():
        ingredient_statement = IngredientStatement.objects.get(flavor=flavor)
    else:
        ingredient_statement = None

    context_dict = {
                    # 'labuser':labuser,
                    'status_message':status_message,
                    'window_title': flavor.__str__(),
                    'flavor': flavor,
                    'page_title': page_title,
                    'weight_factor': weight_factor,
                    'formula_weight': formula_weight,
                    'print_link':'FLAVOR_REVIEW_PRINT_MENU',
                    'recalculate_link':'/access/%s/recalculate/' % flavor.number,
                    'ingredient_statement': ingredient_statement
                   }
    return render(request, 'access/flavor/ft_review.html', context_dict)


@flavor_info_wrapper
@login_required
@transaction.atomic
def recalculate_flavor_view(request,flavor):
    results = recalculate_flavor(flavor)
    context_dict = {
                   'window_title': flavor.__str__(),
                   'page_title': "Recalculate Flavor Properties",
                   'flavor': flavor,
                   'weight_factor':1000,
                   'results':results,
                   }
    return render(request, 'access/flavor/recalculate.html', context_dict)




@experimental_wrapper
@login_required
@transaction.atomic
def recalculate_experimental(request,experimental):
    flavor=experimental.flavor
    results = recalculate_flavor(flavor)
    context_dict = {
                    'experimental':experimental,
                   'window_title': flavor.__str__(),
                   'page_title': "Recalculate Flavor Properties",
                   'flavor': flavor,
                   'weight_factor':1000,
                   'results':results
                   }
    return render(request, 'access/experimental/recalculate.html', context_dict)

@flavor_info_wrapper
def print_review(request,flavor):
    info_form = forms.FlavorReviewForm(instance=flavor)

    if IngredientStatement.objects.filter(flavor=flavor).exists():
        ingredient_statement = IngredientStatement.objects.get(flavor=flavor)
    else:
        ingredient_statement = None

    context_dict = {
                   'window_title': flavor.__str__(),
                   'info_form':info_form,
                   'flavor': flavor,
                   'ingredient_statement': ingredient_statement,
                   }
    return render(request, 'access/flavor/print_review.html', context_dict)

@experimental_wrapper
@login_required
def experimental_name_edit(request, experimental):
    """
    This view uses a lot of logic in javascript.
    """
    if request.method == 'POST':
        form = forms.ExperimentalNameForm(request.POST)
        PRODUCT_CATEGORY_CHOICES = []
        for pc in ProductCategory.objects.all():
            PRODUCT_CATEGORY_CHOICES.append((pc.id,pc.name))
        form.fields['product_category'].choices = PRODUCT_CATEGORY_CHOICES

        if form.is_valid():
            form.process_data(experimental)
            experimental.save()
            experimental.process_changes_to_flavor()
            return redirect('/access/experimental/%s/' % experimental.experimentalnum)
    else:
        form = forms.ExperimentalNameForm(initial=experimental.__dict__)
        PRODUCT_CATEGORY_CHOICES = []
        for pc in ProductCategory.objects.all():
            PRODUCT_CATEGORY_CHOICES.append((pc.id,pc.name))
        form.fields['product_category'].choices = PRODUCT_CATEGORY_CHOICES
    page_title = "Experimental Name Edit"
    if request.user.userprofile.initials == experimental.initials or request.user.is_superuser:
    # if request.user.groups.filter(name='Lab').exists() or request.user.is_superuser:
        pass
    else:
        return render(request, 'access/experimental/experimental_edit_permission.html', )
    context_dict = {
                    'experimental': experimental,
                    'page_title': page_title,
                    'experimental_name_form':form,
                    }
    return render(request, 'access/experimental/experimental_name_edit.html', context_dict)


@experimental_wrapper
def experimental_print_review(request, experimental):
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
                   'window_title': experimental.__str__(),
                   'experimental': experimental,
                   'digitized_table':digitized_table,
                   }
    return render(request, 'access/experimental/print_review.html', context_dict)

@flavor_info_wrapper
def gzl(request, flavor):
    page_title = "Product Gazinta List (GZL)"
    context_dict = {
                   'window_title': flavor.__str__(),
                   'product': flavor,
                   'page_title': page_title,
                   }
    return render(request, 'access/gzl.html', context_dict)


@ingredients_by_pin_info_wrapper
def ingredient_gzl_review(request, ingredients):
    page_title = "Ingredient Gazinta List (GZL)"
    ingredient = Ingredient.get_obj_from_softkey(ingredients[0].id)
    if ingredient.sub_flavor == None:
        context_dict = {
                       'window_title': ingredient.__str__(),
                       'product': ingredient,
                       'leafweights': LeafWeight.objects.filter(ingredient__in=ingredients).order_by('-weight'),
                       'page_title': page_title,
                       }
    else:
        context_dict = {
                       'window_title': ingredient.__str__(),
                       'product': ingredient,
                       'leafweights': FormulaTree.objects.filter(node_ingredient__in=ingredients).order_by('-weight'),
                       'page_title': page_title,
                       }
    return render(request, 'access/ingredient/gzl.html', context_dict)

@ingredients_by_pin_info_wrapper
def ingredient_documentation(request, ingredients):
    page_title = "Ingredient Documentation"
    ingredient = Ingredient.get_obj_from_softkey(ingredients[0].id)

    documentation_path = '/var/www/static_root/Documentation/%s/' % ingredient.id
    static_path = '/static/Documentation/%s/' % ingredient.id
    documentation_list = []


    for root, dirnames, filenames in os.walk(documentation_path):
        for filename in filenames:
            url = root + '/' + filename
            date_modified = datetime.fromtimestamp(os.path.getmtime(url)).strftime('%x')
            documentation_list.append([filename, url.replace('/var/www/static_root/','/static/'), date_modified])
        break #break because we only want the files in the top level folder, not the ones in subdirectories

    #The code below is used to get all files in documentation_path, even the ones in subfolders
    # for root, dirnames, filenames in os.walk(documentation_path):
    #     for filename in filenames:
    #         if root.endswith('/'):
    #             url = root + filename
    #         else:
    #             url = root + '/' + filename
    #         date_modified = datetime.fromtimestamp(os.path.getmtime(url)).strftime('%x')
    #         documentation_list.append([filename, url.replace('/var/www/static_root','static'), date_modified])

    context_dict = {
                    'ingredient': ingredient,
                    'documentation_list': documentation_list,
                    }

    return render(request, 'access/ingredient/documentation.html', context_dict)

@login_required
@reversion.create_revision()
@transaction.atomic
def ingredient_activate(request, raw_material_code=False, ingredient_id=False):

    reversion_comment = None

    #if no raw material code provided, discontinue all was selected; discontinue any activated ingredients having the ingredient_id in url
    if raw_material_code == False:

        for ingredient in Ingredient.objects.filter(id=ingredient_id):
            if ingredient.discontinued == False:
                old_active_ingredient = ingredient
                break

        discontinue_ingredient(old_active_ingredient)

        reversion.set_comment("Old Active Ingredient %s, now discontinued." % old_active_ingredient)

        #redirect_path = "/access/%s/recalculate/" % (flavor.number)
        redirect_path = "/access/ingredient/pin_review/%s" % ingredient_id
        return HttpResponseRedirect(redirect_path)

    else: #otherwise, activate the ingredient with the raw material code specified in the url

        page_title = "Raw Material Update Information"
        table_headers = (
                "Flavor Number",
                "Raw Material Weight",
                "Old Price",
                "New Price",
                "Price Difference"
        )

        new_active_ingredient = Ingredient.objects.get(rawmaterialcode=raw_material_code)

        #find the old active ingredient (id is the same), if there is one
        all_discontinued = True

        for ingredient in Ingredient.objects.filter(id=new_active_ingredient.id):
            if ingredient.discontinued == False:
                all_discontinued = False
                old_active_ingredient = ingredient
                break

        if all_discontinued == False: #if there was an ingredient already active, discontinue it, activate the new one, and calculate price differences

            #create list of tuples with flavornumber, rawmaterial weight, oldprice, newprice
            updated_flavors = []
            if old_active_ingredient == new_active_ingredient: #if they refresh the page (ingredient is already active)
                for lw in LeafWeight.objects.filter(ingredient=old_active_ingredient):
                    root_flavor = lw.root_flavor
                    price = root_flavor.rawmaterialcost
                    price_change = 0
                    updated_flavors.append((lw.root_flavor, lw.weight, price, price, price_change))

            else:
                discontinue_ingredient(old_active_ingredient)
                activate_ingredient(new_active_ingredient)

                #replace all foreignkeys to the old ingredient with the new active ingredient
                replace_ingredient_foreignkeys(new_active_ingredient)

                updated_flavors = update_prices_and_get_updated_flavors(old_active_ingredient, new_active_ingredient)

                reversion_comment = "Old Active Ingredient: %s, New Active Ingredient: %s" % (old_active_ingredient.name, new_active_ingredient.name)


        else: #if all ingredients were previously discontinued, activate the single ingredient
            new_active_ingredient.discontinued = False
            new_active_ingredient.save()

            replace_ingredient_foreignkeys(new_active_ingredient)

            updated_flavors = []
            for lw in LeafWeight.objects.filter(ingredient=new_active_ingredient):
                lw.root_flavor.save()
                updated_flavors.append((lw.root_flavor, lw.weight, "Discontinued", lw.root_flavor.rawmaterialcost, "-"))

            reversion_comment = "Old Active Ingredient: None (ALL DISCONTINUED), New Active Ingredient: %s" % new_active_ingredient.name

        if reversion_comment:
            reversion.set_comment(reversion_comment)

        context_dict = {
                        'activated_ingredient': new_active_ingredient,
                        'updated_flavors': updated_flavors,
                        'page_title': page_title,
                        'table_headers': table_headers,
        }
        return render(request, 'access/ingredient/activate_raw_materials.html', context_dict)


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
                     "Activate",
    )
    highlighted_ingredient = ingredients[0]

    all_discontinued = True

    for ing in ingredients:
        if ing.discontinued == False:
            highlighted_ingredient = ing
            all_discontinued = False
            break

    discontinued_flavors = []
    if all_discontinued == True:
        for lw in LeafWeight.objects.filter(ingredient__id = highlighted_ingredient.id):
            discontinued_flavors.append((lw.root_flavor, lw.weight))

    if request.method == 'POST':
        icu = forms.IngredientCostUpdate(request.POST)
        if icu.is_valid():
            x =  icu.cleaned_data['new_cost']
            updated_flavors = highlighted_ingredient.update_price(icu.cleaned_data['new_cost'])

        if updated_flavors != True:
            for f, prices in updated_flavors.items():
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
                    'window_title': highlighted_ingredient.__str__(),
                    'highlighted_ingredient': highlighted_ingredient,
                    'ingredients': ingredients,
                    'page_title': page_title,
                    'table_headers': table_headers,
                    'icu': icu,
                    'updated_flavors': updated_flavors_threshold,
                    'all_discontinued': all_discontinued,
                    'discontinued_flavors': discontinued_flavors
    }
    return render(request, 'access/ingredient/ingredient_pin_review.html', context_dict)


@ingredient_by_rmc_info_wrapper
def ingredient_review(request, ingredient):
    page_title = "Ingredient Review"
    field_details = []
    for field in ingredient._meta.fields:
        field_details.append((field.verbose_name,
                              field.value_from_object(ingredient)))

    context_dict = {
                    'window_title': ingredient.__str__(),
                   'ingredient': ingredient,
                   'field_details': field_details,
                   'page_title': page_title,
    }
    return render(request, 'access/ingredient/ingredient_review.html', context_dict)


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
    return render(request, 'access/flavor/batch_sheet.html', context_dict)


def flavor_search(request, status_message=None):
    page_title = "Flavor Search"
    search_string = request.GET.get('search_string', '')

    # labuser = False
    # admin = Group(name="Admin")
    # lab = Group(name="Lab")
    # cs = Group(name="Customer Service")
    # if request.user in lab:
    #     labuser = True
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

    return render(
        request,
        'access/flavor/index.html',
        {
            # 'labuser':labuser,
            'window_title': page_title,
            'list_items': flavors,
            'resultant_objs': resultant_flavors,
            'status_message': status_message,
            'search': forms.FlavorSearch({'search_string': search_string}, label_suffix=''),
            'page_title': page_title,
            'get': request.GET,
        },
    )

def sort_ingredient_search(ingredient_list):
    #take the ingredient list from the ingredient_autocomplete function
    #sort it - 1. discontinued 2. non-solutions 3. pin #
    pass
    #find the fastest way to determine whether an ingredient is a solution


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
    if match: #this returns true if the search term is an integer
        if len(term) == 1:
            #if the term is a single digit, find any ingredient with that id
            ingredients = Ingredient.objects.filter(id=int(term))
        else:
            #if the term is multiple digits, find any ingredients whose id contains those digits
            ingredients = Ingredient.objects.filter(id__contains=match.group())
    else: #if the search term contains characters
        #find any ingredients whose product_naem contains the term
        ingredients = Ingredient.objects.filter(product_name__icontains=term)
    for ingredient in ingredients.order_by('discontinued','-ing_obj'):
        ingredient_json = {}
        ingredient_json["id"] = ingredient.id
        ingredient_json["label"] = ingredient.__str__()
        ingredient_json["value"] = ingredient_json["id"]
        ret_array.append(ingredient_json)
    return HttpResponse(json.dumps(ret_array), content_type='application/json; charset=utf-8')

def process_filter_update(request):

    return_messages = {}
    # pks = map(int, request.GET.getlist('pks[]'))
    pks = request.GET.getlist('pks[]')
    # removed Prop65Filter for now, AllergenExcludeFilter
    for FilterClass in (ArtNatiFilter, MiscFilter, AllergenExcludeFilter):
        fc = FilterClass(request.GET)
        if fc.apply_filter:
            for pk in pks:
                return_message = fc.check_pk(pk)
                if return_message is not None:
                    if pk not in return_messages:
                        return_messages[pk] = [return_message,]
                    else:
                        return_messages[pk].append(return_message)

    return HttpResponse(json.dumps(return_messages), content_type='application/json; charset=utf-8')

def process_tsrli_update(request):
    try:
        type = request.GET['type']
    except:
        type = None #user has not selected a product type (for the new row)

    number = request.GET['number']
    response_dict = {}

    if type == 'flavor':
        try:
            flavor = Flavor.objects.get(number=number)
            response_dict['name'] = flavor.long_name
        except:
            if number == '':
                response_dict['name'] = 'Please enter a flavor number.'
            else:
                response_dict['name'] = "Invalid Flavor Number"

    if type == 'ex_log':
        try:
            ex_log = ExperimentalLog.objects.get(experimentalnum = number)
            response_dict['name'] = ex_log.__str__()
        except:
            if number == '':
                response_dict['name'] = 'Please enter an experimental number.'
            else:
                response_dict['name'] = "Invalid Experimental Log Number"

    if type == None:
        response_dict['name'] = "Please select a product type."

    return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')

def process_cell_update(request):
    number = request.GET.get('number')
    amount = request.GET.get('amount')
    response_dict = {}
    try:
        ingredient = Ingredient.get_formula_ingredient(number)
    except:
        ingredient = None
    if ingredient is not None:
        response_dict['name'] = ingredient.long_name
        response_dict["pk"] = ingredient.pk
        try:
            try:
                response_dict['cost'] = str(
                    Decimal(ingredient.rawmaterialcost * Decimal(amount) / 1000).quantize(Decimal('.001'), rounding=ROUND_HALF_UP))

            except:
                response_dict['cost'] = str(Decimal(ingredient.unitprice * Decimal(amount) / 1000).quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        except:
            response_dict['cost'] = ''
    else:
        if number == '':
            response_dict['name'] = ''
        else:
            response_dict['name'] = "Invalid Ingredient Number"
        response_dict['cost'] = ''

    return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')

def sanity_check(resultant_objects):
    if resultant_objects.count() == 1:
        return ('redirect', resultant_objects[0])
        #HttpResponseRedirect(resultant_objects[0].get_absolute_url()))
    else:
        return None

@permission_required('access.change_formula')
@flavor_info_wrapper
@reversion.create_revision()
@transaction.atomic
def formula_entry(request, flavor, status_message=None):
    # labuser = False
    # if request.user.groups.filter(name='Lab').exists() or request.user.is_superuser:
    #     labuser = True
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
            reversion.set_comment("Old formula: %s" % ", ".join(previous_formula_text_summary))
            flavor.ingredients.clear()

            for ing, amount in ingredient_list.items():
                formula_row = Formula(flavor=flavor,
                                    ingredient=ing,
                                    amount=amount,
                                    acc_flavor=flavor.number,
                                    acc_ingredient=ing.id,)
                formula_row.save()

            flavor.save()
            redirect_path = "/access/%s/recalculate/" % (flavor.number)
            return HttpResponseRedirect(redirect_path)

        else:
            filterselect = FormulaEntryFilterSelectForm(request.GET.copy())
            filterexclude = FormulaEntryExcludeSelectForm(request.GET.copy())
            label_rows = forms.build_formularow_formset_label_rows(formset)
            formula_rows = list(zip(formset.forms,
                       label_rows ))
            return render(
                request,
                'access/flavor/formula_entry.html',
                {
                    # 'labuser':labuser,
                    'flavor': flavor,
                    'request':formset.errors,
                    'filterselect': filterselect,
                    'filterexclude': filterexclude,
                    'status_message': status_message,
                    'window_title': page_title,
                    'page_title': page_title,
                    'formula_rows': formula_rows,
                    'management_form': formset.management_form,
                },
            )

    # else:
    initial_data, label_rows = forms.build_formularow_formset_initial_data(flavor)
    if len(label_rows) == 0:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=1)
        label_rows.append({'cost': '', 'name': ''})
    else:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=0)

    filterselect = FormulaEntryFilterSelectForm(request.GET.copy())

    formset = FormulaFormSet(initial=initial_data)
    formula_rows = list(zip(formset.forms,
                       label_rows ))


    return render(
        request,
        'access/flavor/formula_entry.html',
        {
            'flavor': flavor,
            'filterselect': filterselect,
            'status_message': status_message,
            'window_title': page_title,
            'page_title': page_title,
            'formula_rows': formula_rows,
            'management_form': formset.management_form,
        },
    )

@experimental_wrapper
@reversion.create_revision()
@transaction.atomic
def experimental_formula_entry(request, experimental, status_message=None):
    page_title = "Experimental Formula Entry"
    status_message = ""
    try:
        if request.user.userprofile.initials == experimental.initials or request.user.is_superuser:
        # if request.user.groups.filter(name='Lab').exists() or request.user.is_superuser:
            pass
        else:
            return render(request, 'access/experimental/experimental_edit_permission.html', )
    except:
        return render(request, 'access/experimental/experimental_edit_permission.html', )
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
            reversion.set_comment("Old formula: %s" % ", ".join(previous_formula_text_summary))
            flavor.ingredients.clear()
            rawmaterialcost = 0

            for ing, amount in ingredient_list.items():
                rawmaterialcost = rawmaterialcost + amount * ing.unitprice
                formula_row = Formula(flavor=flavor,
                                    ingredient=ing,
                                    amount=amount,
                                    acc_flavor=flavor.number,
                                    acc_ingredient=ing.id,)
                formula_row.save()



            flavor.rawmaterialcost = Decimal(rawmaterialcost / 1000)

            flavor.save()
            redirect_path = "/access/experimental/%s/recalculate/" % (experimental.experimentalnum)
            return HttpResponseRedirect(redirect_path)
        else:
            label_rows = forms.build_formularow_formset_label_rows(formset)
            formula_rows = list(zip(formset.forms,
                       label_rows ))
            digitized_table = []
            digitized_test_re = re.compile('\w')
            for digitizedformula in experimental.digitizedformula_set.all().order_by('pk'):
                contains_values = digitized_test_re.search(digitizedformula.raw_row)
                if contains_values:
                    digitized_table.append(digitizedformula.raw_row.split("|||"))

            return render(
                request,
                'access/experimental/formula_entry.html',
                {
                    'experimental': experimental,
                    'status_message': status_message,
                    'window_title': page_title,
                    'page_title': page_title,
                    'formula_rows': formula_rows,
                    'management_form': formset.management_form,
                    'digitized_table':digitized_table,
                },
            )
    # else:
    initial_data, label_rows = forms.build_formularow_formset_initial_data(flavor)
    if len(label_rows) == 0:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=1)
        label_rows.append({'cost': '', 'name': ''})
    else:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=0)
    formset = FormulaFormSet(initial=initial_data)
    formula_rows = list(zip(formset.forms,
                       label_rows))
    digitized_table = []
    digitized_test_re = re.compile('\w')
    for digitizedformula in experimental.digitizedformula_set.all().order_by('pk'):
        contains_values = digitized_test_re.search(digitizedformula.raw_row)
        if contains_values:
            digitized_table.append(digitizedformula.raw_row.split("|||"))

    return render(
        request,
        'access/experimental/formula_entry.html',
        {
            'experimental': experimental,
            'status_message': status_message,
            'window_title': page_title,
            'page_title': page_title,
            'formula_rows': formula_rows,
            'management_form': formset.management_form,
            'digitized_table':digitized_table,
        },
    )




@login_required
#@reversion.create_revision()
#@transaction.atomic
def tsr_entry(request, tsr_number):
    tsr = get_object_or_404(TSR, number=tsr_number)
    page_title = "TSR Product Entry"
    status_message = ""
    TSRLIFormSet = inlineformset_factory(TSR, TSRLineItem, extra=1, form=forms.TSRLIForm, can_delete=True)
    if request.method == 'POST':
        formset = TSRLIFormSet(request.POST, instance=tsr)
        if formset.is_valid():
            formset.save()

            for id, tsrli in enumerate(tsr.tsrlineitem_set.all()):
                type = formset.cleaned_data[id]['content_type_select']

                number = formset.cleaned_data[id]['code']
                if type == 'flavor':
                    line_product = Flavor.objects.get(number = number)
                if type == 'ex_log':
                    line_product = ExperimentalLog.objects.get(experimentalnum = number)
                #line_product = Flavor.objects.get(number = 8851)
                tsrli.product = line_product
                tsrli.save()

            #foo = formset.cleaned_data
            #print foo


            return HttpResponseRedirect("/access/tsr/%s/tsr_entry/" % tsr.number)
        else:
            return render(
                request,
                'access/tsr/tsr_entry.html',
                {
                    'tsr': tsr,
                    'status_message': status_message,
                    'window_title': page_title,
                    'page_title': page_title,
                    'tsr_rows': list(zip(formset.forms,)),
                    'management_form': formset.management_form,
                },
            )
    formset = TSRLIFormSet(instance=tsr)
#    initial_data, label_rows = forms.build_poli_formset_initial_data(po)
#    if len(label_rows) == 0:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=1)
#        label_rows.append({'cost':'', 'name':''})
#    else:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=0)
#    formset = POLIFormSet(initial=initial_data)
    tsrli_rows = list(zip(formset.forms,
                   #    label_rows)
                   ))
    return render(
        request,
        'access/tsr/tsr_entry.html',
        {
            'tsr': tsr,
            'status_message': status_message,
            'window_title': page_title,
            'page_title': page_title,
            'tsr_rows': tsrli_rows,
            'management_form': formset.management_form,
            'extra':tsrli_rows[-1],
        },
    )




@login_required
@po_info_wrapper
#@reversion.create_revision()
#@transaction.atomic
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
            return HttpResponseRedirect("/access/purchase/%s/po_entry/" % po.number)
        else:
            return render(
                request,
                'access/purchase/poli_entry.html',
                {
                    'po': po,
                    'status_message': status_message,
                    'window_title': page_title,
                    'page_title': page_title,
                    'poli_rows': formset.forms,
                    'management_form': formset.management_form,
                },
             )
    formset = POLIFormSet(instance=po)
#    initial_data, label_rows = forms.build_poli_formset_initial_data(po)
#    if len(label_rows) == 0:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=1)
#        label_rows.append({'cost':'', 'name':''})
#    else:
#        POLIFormSet = formset_factory(forms.POLIForm, extra=0)
#    formset = POLIFormSet(initial=initial_data)
    poli_rows = formset.forms
    return render(
        request,
        'access/purchase/poli_entry.html',
        {
            'po': po,
            'status_message': status_message,
            'window_title': page_title,
            'page_title': page_title,
            'poli_rows': poli_rows,
            'management_form': formset.management_form,
            'extra':poli_rows[-1],
        },
    )

ajax_function = {
    'consolidated': (consolidated, 'access/flavor/consolidated.html'),
    'consolidated_indivisible': (consolidated_indivisible, 'access/flavor/consolidated_indivisible.html'),
    'explosion': (explosion, 'access/flavor/explosion.html'),
    'legacy_explosion': (legacy_explosion, 'access/flavor/legacy_explosion.html'),
    'production_lots': (production_lots, 'access/flavor/production_lots.html'),
    'retains': (retains, 'access/flavor/retains.html'),
    'raw_material_pin': (raw_material_pin, 'access/ingredient/raw_material_pin.html'),
    'gzl_ajax': (gzl_ajax, 'access/gzl_ajax.html'),
    'revision_history': (revision_history, 'history_audit/revision_history.html'),
    'spec_sheet': (spec_sheet, 'access/flavor/review_specsheet.html'),
    'customer_info': (customer_info, 'access/flavor/customer_info.html'),
    'similar_flavors': (similar_flavors, 'access/flavor/similar_flavors.html'),
    'documentation': (documentation, 'access/flavor/documentation.html'),
}

#def ajax_dispatch(request, template_name, flavor_number):
def ajax_dispatch(request):
    ajax_func, ajax_template = ajax_function[request.GET['tn']]

    return render(request, ajax_template, ajax_func( Flavor.objects.get(pk=request.GET['pk']) ))
        #eturn HttpResponse(json.dumps({'a':1}), content_type='application/json; charset=utf-8')

#    ingredient_json = {}
#        ingredient_json["id"] = ingredient.id
#        ingredient_json["label"] = ingredient.__str__()
#        ingredient_json["value"] = ingredient_json["id"]
#        ret_array.append(ingredient_json)
#    return HttpResponse(json.dumps(ret_array), content_type='application/json; charset=utf-8')


def table_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % request.POST['flavor_number']
    response.write(request.POST['exportdata'])
    return response


def get_ingredient_option_list(request):
    option_list = []
    for ing in Ingredient.objects.all():
        option_list.append({ing.rawmaterialcode: ing.__str__()})
    return HttpResponse(json.dumps(option_list), content_type='application/json; charset=utf-8')


def get_barcode(request, flavor_number):
    f = get_object_or_404(Flavor, number=flavor_number)
    barcode = barcodeImg(codeBCFromString(str(f.number)))
    response = HttpResponse(content_type="image/png")
    barcode.save(response, "PNG")
    return response


# TODO : fix these; just placeholder
@login_required
@reversion.create_revision()
@transaction.atomic
def db_ops(request):
    return render(request, 'access/flavor/db_ops.html', {})


def process_digitized_paste(request):
    response_dict = {}
    response_dict['test'] = request.GET.get('text')
    return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')


@login_required
@reversion.create_revision()
@transaction.atomic
def digitized_entry(request):
    form = forms.DigitizedFormulaPasteForm()
    return render(request, 'access/flavor/digitized_entry.html', {'form': form})

@login_required
@reversion.create_revision()
@transaction.atomic
def new_tsr(request):

    TSRForm = make_tsr_form(request)

    if request.method == 'POST':
        form = TSRForm(request.POST)
        if form.is_valid():
            form.save()
            number = form.cleaned_data['number']
            return HttpResponseRedirect('/access/tsr/%s/tsr_entry' % number)

    else:
        form = TSRForm()

    return render(request, 'access/tsr/new.html', {'form': form})



#     class TSRCreateView(CreateView):
#          form_class = TSRForm,
#          template_name="access/tsr/new.html",
#          post_save_redirect="/access/tsr/%(number)s/tsr_entry",

#     callable_view = CreateView.as_view(
#          form_class = TSRForm,
#          template_name="access/tsr/new.html",
#          post_save_redirect="/access/tsr/%(number)s/tsr_entry",
#     )
#
#     return callable_view(request)

#     return create_object(request,
#                          form_class = TSRForm,
#                          template_name="access/tsr/new.html",
#                          post_save_redirect="/access/tsr/%(number)s/tsr_entry",)

@login_required
@reversion.create_revision()
@transaction.atomic
def new_po(request):

    if request.method == 'POST':
        form = forms.PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            number = form.cleaned_data['number']
            return HttpResponseRedirect('/access/purchase/%s/po_entry/' % number)

    else:
        form = forms.PurchaseOrderForm()

    return render(request, 'access/purchase/new.html', {'form': form})

#     return create_object(request,
#                          form_class=forms.PurchaseOrderForm,
#                          template_name="access/purchase/new.html",
#                          post_save_redirect="/access/purchase/%(number)s/po_entry/",)


def jil_object_list(request):
    queryset = JIList.objects.all()
    callable_view = SubListView.as_view(
            paginate_by=100,
            queryset=queryset,
            extra_context= {
                    'page_title': "Similar Flavrors",
                },
        )

    return callable_view(request)

@login_required
def new_rm_wizard(request): #TODO, where is the template for this?

    NewRMFormWizard = forms.make_new_rm_form_wizard(request)
    return NewRMFormWizard.as_view([forms.NewRMForm1, forms.NewRMForm11, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5])(request)


@login_required
@permission_required('access.change_formula')
@flavor_info_wrapper
def formula_info_merge(request, flavor):
    return render(request, 'access/flavor/formula_info_merge.html', {'flavor':flavor})



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
    for aller in Ingredient.boolean_allergens + Ingredient.text_allergens:
        if getattr(flavor, aller) == True:
            allers.append(aller)
    if len(allers) == 0:
        allers = ["None"]

    #check if flavor has an experimental log, that it is approved, and that its number is in the experimental range
    #if yes, give it an experimental prefix
    #if none of these things are true, give it the normal prefix

    if flavor.experimental_log.count() > 0 and (not flavor.approved) and (50000 < flavor.number < 59999):
        exlog = flavor.experimental_log.all()[0]
        prefix = '%s-%s' % (exlog.experimentalnum, exlog.initials)
    else:
        prefix = '%s-%s' % (flavor.prefix, flavor.number)





    initial = {
        '0':{
           'art_nati':flavor.natart,
           'prefix': prefix,
           'product_name':"%s %s" % (flavor.name, flavor.label_type),
           },
        '1':{
           'unitprice':flavor.rawmaterialcost,
           'purchase_price_update':flavor.lastspdate,
           'suppliercode':"FDI",
           'supplier':2,
           'package_size':0,
           'minimum_quantity':0,
           'fob_point':"FDI",
           'lead_time':0,
           },
        '2':{
           'kosher':flavor.kosher,
           'kosher_code':flavor.kosher_id,
           },
        '3':{
           'hazardous':0,
           'microsensitive':my_microsensitive,
           'prop65':my_prop_65,
           'nutri':0,
           },
        '4':{
           'sulfites_ppm':flavor.sulfites_ppm,
           'allergens':allers,

           },
        'extra_flavor':{
            'sub_flavor_id':flavor.id,
            'flavornum':flavor.number,
            'solubility_memo':flavor.solvent,
            },
    }
#     request.session['new_solution_wizard_initial'] = initial

    NewRMFormWizard = forms.make_new_rm_form_wizard(request)
    return NewRMFormWizard.as_view([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial_dict=initial)(request)


# SOLVENT_NAMES = {
#     1983:'Neobee',
#     829:'Triacetin',
#     86:'Benzyl Alcohol',
#     703:'PG',
#     321:'ETOH',
#     100:'Water',
#     473:'Lactic Acid',
#     25:'Iso Amyl Alcohol',
#     758:'Soybean Oil',
#     6403:'Safflower Oil',
#     1478:'Dextrose',
#     5928:'Radia',
# }

@login_required
def new_solution_wizard(request, PIN, solvent, concentration):
    solution_parameters = {'PIN':PIN, 'solvent':solvent, 'concentration':concentration}

    return forms.start_rm_wizard_for_new_solution(request, solution_parameters)
#     get_dict = request.GET.dict()
#     if not set(['PIN', 'solvent', 'concentration']) <= set(get_dict.keys()):
#         return redirect('/access/new_rm/solution_starter/')
#     else:
#         return forms.start_rm_wizard_for_new_solution(request)


@login_required
def new_solution_starter(request):

    if request.method == 'POST':
        form = forms.NewSolutionForm(request.POST)
        if form.is_valid():

#             return redirect('/access/new_rm/solution_wizard/?PIN=%s&solvent=%s&concentration=%s' %
#                             (form.cleaned_data['PIN'], form.cleaned_data['solvent'].ingredient.pk, form.cleaned_data['concentration'][:-1]))

            return redirect('/access/new_rm/solution_wizard/pin=%s/solv=%s/conc=%s/' %
                            (form.cleaned_data['PIN'], form.cleaned_data['solvent'].ingredient.pk, form.cleaned_data['concentration'][:-1]))


    f = forms.NewSolutionForm()
    return render(request, 'access/new_solution.html', {'form':f})

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
#            return redirect('/access/ingredient/pin_review/%s/' % new_ingredient.id)


def allergen_list(request):

    return render(request, 'access/allergen_list.html', {'flavors':Flavor.objects.exclude(allergen__iexact="None")})

def rm_allergen_list(request):

    return render(request, 'access/rm_allergen_list.html', {'rms':Ingredient.objects.exclude(allergen__iexact="None")})

@login_required
def new_rm_wizard_launcher(request):
    return render(request, 'access/new_rm_wizard_launcher.html')


@login_required
@permission_required('access.add_experimentallog')
def new_ex_wizard(request):

    NewExFormWizard = forms.make_new_ex_form_wizard(request)

    return NewExFormWizard.as_view([forms.NewExForm1,forms.NewExForm2,forms.NewExForm3])(request)

@login_required
def new_rm_wizard_rm(request, ingredient_pk):
    i = Ingredient.objects.get(pk=ingredient_pk)
    allers = []
    for aller in Ingredient.boolean_allergens + Ingredient.text_allergens:
        if getattr(i, aller):
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
    NewRMFormWizard = forms.make_new_rm_form_wizard(request)
    return NewRMFormWizard.as_view([forms.NewRMForm1, forms.NewRMForm2, forms.NewRMForm3, forms.NewRMForm4, forms.NewRMForm5], initial_dict=initial)(request)


@flavor_info_wrapper
def formula_visualization(request, flavor):
    formatted_ft = formulatree_to_jsinfovis(FormulaTree.objects.filter(root_flavor=flavor))

    st_layout_parameters = {}
    if request.method == 'GET' and 'levels_to_show' in request.GET:
        st_layout_form = forms.STLayoutForm(request.GET)
        if st_layout_form.is_valid():
            for k,v in st_layout_form.cleaned_data.items():
                st_layout_parameters[k] = v
    else:
        st_layout_form = forms.STLayoutForm()
        for k,v in st_layout_form.fields.items():
            st_layout_parameters[k] = v.initial

    context_dict = {
         'flavor':flavor,
         'st_layout_form':st_layout_form,
         'st_layout_parameters':  json.dumps(st_layout_parameters),
        }
    context_dict.update(formatted_ft)
    return render(request, 'access/flavor/formula_visualization.html', context_dict)

@flavor_info_wrapper
def spec_sheet(request, flavor):

    general_specs = flavor.flavorspecification_set.filter(replaces=None).filter(customer=None)

    other_specs = general_specs.filter(micro=False)
    micro_specs = general_specs.filter(micro=True)

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
def delete_spec(request, flavor_number, spec_id):
    spec = get_object_or_404(FlavorSpecification, id=spec_id)

    delete_specification(spec)

    return HttpResponseRedirect(reverse('access.views.specification_list', args=[flavor_number]))

@flavor_info_wrapper
def specification_list(request, flavor):
    page_title = "%s - Spec List" % flavor.name

    spec_list = []

    for flavorspec in flavor.flavorspecification_set.filter(customer=None).filter(replaces=None).order_by('name'):
        edit_url = reverse('access.views.edit_spec', args=[flavor.number, flavorspec.id])
        delete_url = reverse('access.views.delete_spec', args=[flavor.number, flavorspec.id])
        spec_list.append((flavorspec.name, flavorspec.specification, flavorspec.micro, edit_url, delete_url))

    return render(
        request,
        'access/flavor/specification_list.html',
        {
            'page_title':page_title,
            'flavor':flavor,
            'spec_list': spec_list,
            'add_url': reverse('access.views.edit_spec', args=[flavor.number])
        },
    )


@permission_required('access.view_flavor')
def edit_spec(request, flavor_number, spec_id=0):
    page_title = "Edit Customer Spec"

    flavor = Flavor.objects.get(number=flavor_number)
    FlavorSpecificationForm = make_flavorspec_form(flavor)

    return_url = reverse('access.views.specification_list', args=[flavor_number])

    if spec_id == 0:
        spec = None
        initial_data = {}
    else:
        spec = get_object_or_404(FlavorSpecification, id=spec_id)

        #this is used if NOT post
        initial_data = {'pk':spec.pk,
                        'name':spec.name,
                        'specification':spec.specification,
                        'micro':spec.micro,}

    if request.method == 'POST':
        form = FlavorSpecificationForm(request.POST)
        if form.is_valid():
            #if they are adding a new spec
            if spec_id == 0:
                    name = form.cleaned_data['name']
                    specification = form.cleaned_data['specification']
                    micro = form.cleaned_data['micro']

                    create_new_spec(flavor, name, specification, micro)

            #editing an existing spec
            else:
                name = form.cleaned_data['name']
                specification = form.cleaned_data['specification']
                micro = form.cleaned_data['micro']

                update_spec(spec, name, specification, micro)

            return HttpResponseRedirect(return_url)

#         else: #for testing purposes
#             raise forms.ValidationError(form.errors)

    if request.method != 'POST':
        form = FlavorSpecificationForm(initial=initial_data)

    return render(
        request,
        'access/flavor/edit_spec.html',
        {
            'flavor': flavor,
            'spec': spec,
            'window_title': page_title,
            'page_title': page_title,
            'form': form,
            'return_url': return_url
        },
    )



@flavor_info_wrapper
def spec_list(request, flavor):
    page_title = "%s - Spec List" % flavor.name

    SpecFormSet = formset_factory(make_flavorspec_form(flavor), extra=1, can_delete=True)

    if request.method == 'POST':
        formset = SpecFormSet(request.POST)
        if formset.is_valid():

            for form in formset.forms:
                try: #need this try/except in case they click 'delete' on an empty row and save
                    if 'DELETE' in form.cleaned_data:
                        if form.cleaned_data['DELETE']==True:
                            try:
                                flavorspec = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
                                flavorspec.delete()
                            except:
                                pass
#                         elif FlavorSpecification.
                        else:
                            try:
                                flavorspec = FlavorSpecification.objects.get(pk=form.cleaned_data['pk'])
                                flavorspec.name = form.cleaned_data['name']
                                flavorspec.specification = form.cleaned_data['specification']
                                flavorspec.micro = form.cleaned_data['micro']
                            except:
                                flavorspec = FlavorSpecification(
                                    flavor = flavor,
                                    name = form.cleaned_data['name'],
                                    specification = form.cleaned_data['specification'],
                                    micro = form.cleaned_data['micro']
                                )
                            flavorspec.save()
                except:
                    #error
                    return HttpResponseRedirect("/access/%s/spec_list/EXCEPT" % flavor.number)


            return HttpResponseRedirect("/access/%s/spec_list/" % flavor.number)
        else:
            return render(
                request,
                'access/flavor/spec_list.html',
                {
                    'flavor': flavor,
                    'window_title': page_title,
                    'page_title': page_title,
                    'spec_rows': list(zip(formset.forms,)),
                    'flavor_edit_link': '#',
                    'management_form': formset.management_form,
                },
            )


    initial_data = []
#     #display all flavorspecs, including customer specs (don't want this for standard flavorspec edit list)
#     for flavorspec in flavor.flavorspecification_set.all():
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
#         initial_data.append({'pk':flavorspec.pk, 'customer_id':customer_id, 'replaces_id':replaces_id, 'name':flavorspec.name, 'specification':flavorspec.specification, 'micro':flavorspec.micro})

    #only display non-customer specs
    #unedited general specs
    for flavorspec in flavor.flavorspecification_set.filter(customer=None).filter(replaces=None):

        initial_data.append({'pk':flavorspec.pk,
                             'customer_id':0,
                             'replaces_id':0,
                             'name':flavorspec.name,
                             'specification':flavorspec.specification,
                             'micro':flavorspec.micro})

    formset = SpecFormSet(initial=initial_data)

    spec_rows = list(zip(formset.forms))
    return render(
        request,
        'access/flavor/spec_list.html',
        {
            'flavor': flavor,
            'window_title': page_title,
            'page_title': page_title,
            'spec_rows': spec_rows,
            'flavor_edit_link': '#',
            'management_form': formset.management_form,
            'extra':spec_rows[-1],
        },
    )


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            # wanted a simple yield str(o) in the next line,
            # but that would mean a yield on the line with super(...),
            # which wouldn't work (see my comment below), so...
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)

@login_required
@flavor_info_wrapper
def reconcile_specs(request, flavor):

    page_title = "%s - Reconcile Specs" % flavor.name

    if request.method == 'POST':
        ReconciledSpecFormSet = formset_factory(forms.ReconciledSpecForm, extra=0)
        formset = ReconciledSpecFormSet(request.POST)

        if formset.is_valid():
            if request.session.get('scraped_data', False):
                json_data = request.session['scraped_data']

                for form in formset.forms:
                    try:
                        flavorspec = FlavorSpecification.objects.get(flavor=flavor, name=form.cleaned_data['name'], customer = None)
                        flavorspec.specification = form.cleaned_data['specification']
                        flavorspec.save()
                    except:
                        create_new_spec(flavor, form.cleaned_data['name'], form.cleaned_data['specification'], False)

                if ReconciledFlavor.objects.filter(flavor = flavor).exists():
                    reconcile_update(flavor, request.user, json_data)
                else:
                    reconcile_flavor(flavor, request.user, json_data)

                redirect_path = reverse('access.views.specification_list', args=[flavor.number])
                return HttpResponseRedirect(redirect_path)
            else:
                print("The user somehow posted to this page without going through the reconcile specs view...")


    #get any flavors with the same formula and scrape from those files as well!
    flavor_pk_list = flavor.loaded_renumber_list
    flavor_list = [Flavor.objects.get(pk = flavor_pk) for flavor_pk in flavor_pk_list]


    mtf_search_list = [('flash', 'Flash Point'), ('specific gravity', 'Specific Gravity')]
    mtf_vals = get_mtf_vals(flavor_list, mtf_search_list)

    db_search_list = [('flashpoint', 'Flash Point'), ('spg', 'Specific Gravity')]
    db_vals = get_db_vals(flavor_list, db_search_list)

    if "no_mtf" in mtf_vals:
        no_mtf = True
        mtf_vals.pop("no_mtf", None)

    else:
        no_mtf = False

    #combine mtf_vals and db_vals to make it easy to display them in the template
    #list of tuples...

    all_vals = []

    for name in mtf_vals:
        if name in db_vals:
            all_vals.append((name, mtf_vals[name], db_vals[name]))
        else:
            all_vals.append((name, mtf_vals[name], None))

    for name in db_vals:
        if name not in mtf_vals:
            all_vals.append((name, None, db_vals[name]))
        else:
            pass #if the name is in both mtf_vals and db_vals, it should already be in all_vals

    #all_vals = [('flash_point', mtf_vals, db_vals), ...]

    #TODO

    scraped_data = all_vals
    request.session['scraped_data'] = scraped_data

    #turn any decimals to strings because json cannot serialize decimals
    for name, mtf, db in scraped_data:
        for key in list(db.keys()):
            if isinstance(db[key], Decimal):
                db[key] = str(db[key])

    scraped_data = json.dumps(scraped_data)
    request.session['scraped_data'] = scraped_data

    grv = guessed_reconciled_vals(mtf_vals, db_vals)

    if request.method != "POST":
        ReconciledSpecFormSet = formset_factory(forms.ReconciledSpecForm, extra=0)
        formset = ReconciledSpecFormSet(initial = grv)

    return render(
        request,
        'access/flavor/reconcile_specs.html',
        {
            'page_title': page_title,
            'flavor': flavor,
            'all_vals': all_vals,
            'mtf_vals': mtf_vals,
            'no_mtf': no_mtf,
            'db_vals': db_vals,
            'reconciled_formset': formset,
            'management_form': formset.management_form,
        },
    )


def get_mtf_vals(flavor_list, spec_search_term_list):


    mtf_list = []

    for flavor in flavor_list:

        path = "/srv/samba/tank/Master Template Files/%s.xls" % flavor.number
#         mtf_list.append((path, fl.number))

        try:
            mtf = open_workbook(path)
            mtf_list.append((mtf, flavor.number))
        except:
            #print "There does not exist a file at path %s" % path
            pass



    #search_results = search_mtfs_for_specs(mtf_list, spec_search_term_list)

    if mtf_list: #if there exist files to be scraped from
        search_results = search_mtfs_for_specs(mtf_list, spec_search_term_list)

    else:
        search_results = {"no_mtf": "No MTF Exists"}



    return search_results

#     #mtf_list = []
#
#     #for flavor_num in flavor_number_list:
#     #    blahblah
#     #    mtf_list.append(mtf)
#
#     #search_results = search_mtfs_for_specs(mtf_list, spec_search_term_list)
#
#     #scraping
#     path = "/home/matta/Master Template Files/%s.xls" % flavor.number
#
#     try:
#         mtf = open_workbook(path)
#     except:
#         print "There does not exist a file at path %s" % path
#
#
#     search_results = search_mtf_for_specs(mtf, spec_search_term_list)
#
#
#     return search_results

def get_db_vals(flavor_list, database_search_list):
    #return a list of dictionaries (no ranges)
    #eg. [{'flash_point': 100}]

    db_values = {}

    for flavor in flavor_list:

        for property, user_friendly_term in database_search_list:


            if not user_friendly_term in db_values:
                db_values[user_friendly_term] = {}


            try:
                db_values[user_friendly_term][flavor.number] = getattr(flavor, property)
            except:
                db_values[user_friendly_term][flavor.number] = None

    return db_values

#     return {'Flash Point': 180}

def guessed_reconciled_vals(mtf_vals, db_vals):
    #return list of dictionaries of initial values for the reconciled specs


    #only using names for now
    spec_names = set()

    for spec_name in mtf_vals:
        spec_names.add(spec_name)

    for spec_name in db_vals:
        spec_names.add(spec_name)

    reconciled_names = []

    for name in spec_names:
        reconciled_names.append({
                                 'name': name,
                                 'spec': ""
                                 })

    return reconciled_names

# def angularjs_test(request):
#     all_flavors = Flavor.objects.all()
#     flavor_list = []
#
#     for fl in all_flavors:
#         flavor_list.append({"number":fl.number, "name":str(fl.name)})
#
#     return render_to_response('access/angularjs_test.html',
#                                 {'flavors': flavor_list,
#                                  'page_title': "Testing AngularJS"})


# TODO this was in the controller, had to move it back because it
# uses a bare call to Ingredient and controller shouldn't import models...
# or should it...
def experimental_approve_from_form(approve_form, experimental):
    approve_form.save()
    new_flavor = approve_form.instance
    experimental.product_number = new_flavor.number
    experimental.save()
    gazintas = Ingredient.objects.filter(sub_flavor=new_flavor)
    if gazintas.count() > 1:
        # hack job. this will raise exception because get() expects 1
        Ingredient.objects.get(sub_flavor=new_flavor)
    if gazintas.count() == 1:
        gazinta = gazintas[0]
        gazinta.prefix = "%s-%s" % (new_flavor.prefix, new_flavor.number)
        gazinta.flavornum = new_flavor.number
        gazinta.save()
    for ft in FormulaTree.objects.filter(root_flavor=new_flavor).exclude(node_flavor=None).exclude(node_flavor=new_flavor).filter(node_flavor__prefix="EX"):
        ft.node_flavor.prefix="GZ"
        ft.node_flavor.save()


def latest_polis_a():
    return_list = []

    for i in Ingredient.objects.annotate(num_polis=Count('purchaseorderlineitem')).exclude(num_polis=0):
        return_list.append(i.purchaseorderlineitem_set.all().latest('po__date_ordered'))

    return return_list

def latest_polis_b():
    return_list = []

    for i in Ingredient.objects.annotate(num_polis=Count('purchaseorderlineitem')).exclude(num_polis__lte=1):
        return_list.append(i.purchaseorderlineitem_set.all().latest('po__date_ordered'))

    for i in Ingredient.objects.annotate(num_polis=Count('purchaseorderlineitem')).filter(num_polis=1):
        return_list.append(i.purchaseorderlineitem_set.all()[0])

    return return_list

def ingredient_hazard_report(request):
    category_objects = IngredientCategoryInfo.objects.all().select_related()
    hazard_classes = HazardClass.objects.filter(
                        id__in=set(category_objects.values_list(
                        'category__hazard_class__id',flat=True)))
    hazardous_ingredients = defaultdict(dict)
    for ingredient_hazard_category in category_objects:
        hazardous_ingredients[
            ingredient_hazard_category.ingredient][
            ingredient_hazard_category.category.hazard_class] = \
                ingredient_hazard_category.category.category
    # the following line is a workaround of known django bug,
    # can't iterate over defaultdicts
    return render(
        request,
        'access/hazard_report.html',
        {
            'hazard_classes':hazard_classes,
            'hazardous_ingredients':hazardous_ingredients,
        },
    )

def flavor_hazard_report(request):

    from time import time
    start = time()

    total_hazardous_flavor_count = FlavorCategoryInfo.objects.all().values_list('flavor__id',flat=True).order_by().distinct().count()
    filter_hazard_ids = [] #default filter
    filter_hazards = None
    filter_statement = None

    if "filter_hazards" in request.GET:
        filter_hazard_ids = ast.literal_eval(request.GET.dict()['filter_hazards'])

    if "filter_statement" in request.GET:
        filter_statement = request.GET.dict()['filter_statement']

    flavors_by_hazard = FlavorCategoryInfo.objects.filter(category__hazard_class__id__in=filter_hazard_ids)
    filter_hazards = [HazardClass.objects.annotate(num_flavors=Count('hazardcategory__flavor')).get(id=hazard_id) for hazard_id in filter_hazard_ids]
#     else:
#         flavors_by_hazard = FlavorCategoryInfo.objects.all()
    flavor_ids_by_hazard = flavors_by_hazard.values_list('flavor__id',flat=True).distinct()
    category_objects = FlavorCategoryInfo.objects.filter(flavor__id__in=flavor_ids_by_hazard).select_related()
    hazard_classes = HazardClass.objects.all().annotate(
                        num_flavors=Count('hazardcategory__flavor')).order_by('-num_flavors')
    hazardous_flavors = defaultdict(dict)
    for flavor_hazard_category in category_objects:
        hazardous_flavors[
            flavor_hazard_category.flavor][
            flavor_hazard_category.category.hazard_class] = \
                flavor_hazard_category.category.category
    # the following line is a workaround of known django bug,
    # can't iterate over defaultdicts
    hazardous_flavors.default_factory = None

    hazardous_flavor_list = list(hazardous_flavors.items())

    #if the user is filtering by statement, recreate the list to only include flavors that have filter_statement in its hcode
    if filter_statement:
        hazardous_flavor_list[:] = [fl for fl in hazardous_flavor_list if fl[0].hazard_statements_contain(filter_statement)]
    filtered_hazardous_flavor_count = len(hazardous_flavor_list)

    time1 = time() - start

    if 'paginate_by' in request.GET:
        pagination_count = request.GET.get('paginate_by')
    else:
        pagination_count = 50

    #this turns the dictionary into a list of tuples and sorts them by number of keys (more hazards will be first)
    sorted_flavors = sorted(hazardous_flavor_list, key=lambda t: len(t[1]), reverse=True)

    paginator = Paginator(sorted_flavors, pagination_count)

    page = request.GET.get('page')

    try:
        flavor_list = paginator.page(page)
    except PageNotAnInteger:
        #if page is not an integer, deliver first page
        flavor_list = paginator.page(1)
    except EmptyPage:
        #if page is out of range, deliver last page of results
        flavor_list = paginator.page(paginator.num_pages)

    time2 = time() - start

    return render(
        request,
        'access/hazard_report.html',
        {
            'page_title': "Hazardous Flavors Report",
            'hazard_classes':hazard_classes,
#             'hazardous_flavors':hazardous_flavors,
#             'filter_hazard_ids': filter_hazard_ids,
            'filter_hazards': filter_hazards,
            'total_hazardous_flavor_count':total_hazardous_flavor_count,
            'filtered_hazardous_flavor_count': filtered_hazardous_flavor_count,
            'flavor_list': flavor_list,
            'pagination_list': [10, 25, 50, 100, 500, 1000],
            'pagination_count': pagination_count,
            'time1': time1,
            'time2': time2,
        },
    )

# def flavor_hazard_report(request):
#     hazardous_flavor_count = FlavorCategoryInfo.objects.all().values_list('flavor__id',flat=True).order_by().distinct().count()
#     if "filter_hazard" in request.GET:
#         flavors_by_hazard = FlavorCategoryInfo.objects.filter(category__hazard_class__id=request.GET["filter_hazard"])
#     else:
#         flavors_by_hazard = FlavorCategoryInfo.objects.all()
#     flavor_ids_by_hazard = flavors_by_hazard.values_list('flavor__id',flat=True)
#     category_objects = FlavorCategoryInfo.objects.filter(flavor__id__in=flavor_ids_by_hazard).select_related()
#     hazard_classes = HazardClass.objects.all().annotate(
#                         num_flavors=Count('hazardcategory__flavor'))
#     hazardous_flavors = defaultdict(dict)
#     for flavor_hazard_category in category_objects:
#         hazardous_flavors[
#             flavor_hazard_category.flavor][
#             flavor_hazard_category.category.hazard_class] = \
#                 flavor_hazard_category.category.category
#     # the following line is a workaround of known django bug,
#     # can't iterate over defaultdicts
#     hazardous_flavors.default_factory = None
#     return render_to_response('access/hazard_report.html',
#         {
#             'hazard_classes':hazard_classes,
#             'hazardous_flavors':hazardous_flavors,
#             'hazardous_flavor_count':hazardous_flavor_count
#         },
#         context=RequestContext(request))

def get_flavors_by_hazmat_label():
    hazard_classes = HazardClass.objects.all().values_list('human_readable_name', 'python_class_name')
    HazardNamedTuple = collections.namedtuple('HazardNamedTuple',
            HazardClass.objects.all().values_list('python_class_name',flat=True)
        )
    flavors_by_hazmat_label = collections.defaultdict(list)
    all_hazard_classes = HazardClass.objects.all().values_list('python_class_name',flat=True)
    for f in Flavor.objects.filter(valid=True).exclude(hazard_set=None):
        my_flavor_hazards_by_class = {}
        for fh in f.hazard_set.all():
            my_flavor_hazards_by_class[fh.hazard_class.python_class_name] = fh.category
        for hazard_class in all_hazard_classes:
            if hazard_class not in my_flavor_hazards_by_class:
                my_flavor_hazards_by_class[hazard_class] = "No"
        my_hazards_named_tuple = HazardNamedTuple(**my_flavor_hazards_by_class)
        flavors_by_hazmat_label[my_hazards_named_tuple].append(f)
    flavors_by_hazmat_label.default_factory = None
    return flavors_by_hazmat_label

def unique_hazard_combinations(request):
    hazard_classes = HazardClass.objects.all().values_list('human_readable_name', 'python_class_name')
    flavors_by_hazmat_label = get_flavors_by_hazmat_label()
    return render(
        request,
        'access/flavor/flavors_by_hazmat_label.html',
        {
            'hazard_classes':hazard_classes,
            'flavors_by_hazmat_label':flavors_by_hazmat_label,
        },
    )


@flavor_info_wrapper
def small_flavor_hazard_label(request, flavor):
    return render(request, 'hazards/label.html',{'flavor':flavor,})

def ingredient_comparison_reports(request):

    if request.method == 'POST':
        form = GHSReportForm(request.POST)

        if form.is_valid():
            report_to_download = form.cleaned_data['report_to_download']

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = "attachment; filename=%s.csv" % report_to_download
            csv_writer = UnicodeWriter(response)

            if report_to_download == 'GHS_Exclusive_Ingredients':

                ghs_only = get_ghs_only_ingredients()
                write_ghs_report(csv_writer, ghs_only)


            elif report_to_download == 'FDI_Exclusive_Ingredients':

                fdi_only = get_fdi_only_ingredients()
                write_fdi_report(csv_writer, fdi_only)

            return response

    else:
        form = GHSReportForm()

    return render(request, 'access/get_ingredient_comparison_reports.html', {'form': form})


def upload_cas_fema(request):
    #CasFemaSpreadSheetFileFormSet = formset_factory(forms.CasFemaSpreadsheetFileForm, extra=2)
    if request.method == 'POST':
        form=CasFemaSpreadsheetsFileForm(request.POST, request.FILES)                               ##ISSUE (C.F.SpredsheetS) form is not valid
        if form.is_valid():
        #formset=CasFemaSpreadSheetFileFormSet(request.POST, request.FILES)
        #print request.FILES['file']
#         uformset = formset_factory(forms.UploadedFile, extra=2)
#         formset = uformset(request.POST, request.FILES)
        #if formset.is_valid():
            pending_changes = find_pending_changes_from_cas_fema_files(request.FILES['file1'], request.FILES['file2'])                    ##ISSUE --> can't .write() FileField (not UploadedFile field)
            #pending_changes = find_pending_changes_from_cas_fema_files(request.FILES['form1'], request.FILES['form2'])
            request.session['pending_changes'] = pending_changes
            ##this is where we'll save the pending changes in the request session
            return HttpResponseRedirect('/access/preview_cas_fema')
    else:
        #formset = CasFemaSpreadSheetFileFormSet()
        form = CasFemaSpreadsheetsFileForm()
        #form2 = CasFemaSpreadsheetFileForm()
    return render(request, 'access/upload_cas_fema.html', {'form': form})

def preview_cas_fema(request):
    pending_changes = request.session['pending_changes']
    max_num = Ingredient.objects.all().count()*3
    CasFemaFormSet_changes = formset_factory(forms.ChangesCasFemaPreviewForm, extra=0, max_num=max_num)
    CasFemaFormSet_errors = formset_factory(forms.ErrorsCasFemaPreviewForm, extra=0, max_num=max_num)
    CasFemaFormSet_noInfo = formset_factory(forms.NoInfoCasFemaPreviewForm, extra=0, max_num=max_num)
    CasFemaFormSet_unknownFema = formset_factory(forms.UnknownFemaCasFemaPreviewForm, extra=0, max_num=max_num)
    #import pdb; pdb.set_trace()
    if request.method == 'POST':
        formset_changes=CasFemaFormSet_changes(request.POST, prefix='changes')
        formset_disagreements = CasFemaFormSet_errors(request.POST, prefix='errors')
        initialData_errors = initialFormData_errors(pending_changes['disagreements'])
        for i in range(len(initialData_errors)):
            form = formset_disagreements.forms[i]
            initialData = initialData_errors[i]
            error_info = form.fields['ingName_errors']
            error_info.choices = initialData['ingName_error_choices']

            form.error_synonyms = initialData['ingName_synonyms']
        formset_noInfo = CasFemaFormSet_noInfo(request.POST, prefix='noInfo')
        formset_unknownFema = CasFemaFormSet_unknownFema(request.POST, prefix='unknownFema')

        if formset_changes.is_valid() and formset_disagreements.is_valid() and formset_noInfo.is_valid() and formset_unknownFema.is_valid():
            listChanges = makeSelectedChanges([formset_changes, formset_disagreements, formset_noInfo, formset_unknownFema])

           # request.session.flush()###flush() is dangerous find another way
            request.session['listChanges'] = listChanges
            return HttpResponseRedirect('/access/success_cas_fema')
    else:
        #(initialFormData_changes, other)=initialFormData_preview_view(pending_changes)
        initialData_changes = initialFormData_changes(pending_changes['changed_ings'])
        formset_changes = CasFemaFormSet_changes(initial=initialData_changes, prefix='changes')
        if initialData_changes == []:
            formset_changes.isEmpty = 'empty'

        initialData_errors = initialFormData_errors(pending_changes['disagreements'])
        formset_disagreements = CasFemaFormSet_errors(initial=initialData_errors, prefix='errors')
        for i in range(len(initialData_errors)):
            form = formset_disagreements.forms[i]
            initialData = initialData_errors[i]
            error_info = form.fields['ingName_errors']
            error_info.choices = initialData['ingName_error_choices']
            ## we want to attach this info to each form, and only apply if the 'Checkbox' field is selected
            form.error_synonyms = initialData['ingName_synonyms']
        if initialData_errors == []:
            formset_disagreements.isEmpty = 'empty'

        initialData_noInfo = initialFormData(pending_changes['no_info'])
        formset_noInfo = CasFemaFormSet_noInfo(initial=initialData_noInfo, prefix='noInfo')
        if initialData_noInfo == []:
            formset_noInfo.isEmpty = 'empty'

        initialData_unknownFema = initialFormData(pending_changes['unknownFema'])
        formset_unknownFema = CasFemaFormSet_unknownFema(initial=initialData_unknownFema, prefix='unknownFema')
        if initialData_unknownFema == []:
            formset_unknownFema.isEmpty = 'empty'
    return render(
        request,
        'access/preview_cas_fema.html',
        {
            'formset_changes': formset_changes,
            'formset_disagreements': formset_disagreements,
            'formset_noInfo':formset_noInfo,
            'formset_unknownFema': formset_unknownFema
         },
    )

def success_cas_fema(request):
    listChanges = request.session['listChanges']
    ###set to none
    return render(request, 'access/success_cas_fema.html', {'listChanges': listChanges})

@flavor_info_wrapper
def flavor_sds(request, flavor):
    flavor.set_hazards()
    flavor.create_label_objects()
    hazard_categories = flavor.hazard_set.all()
    ld50_dict = flavor.get_ld50s()

    sds_info = get_sds_info(hazard_categories, ld50_dict, flavor)

    experimental = None
    if flavor.prefix == 'EX':
        experimental = flavor.experimental_log.all()[0]

    #ingredient statement
    if IngredientStatement.objects.filter(flavor=flavor).exists():
        ingredient_statement = IngredientStatement.objects.get(flavor=flavor).ingredient_statement
    else:
        ingredient_statement = None

    return render(
        request,
        'access/flavor/sds_preview.html',
        {
            'nav_bar': 'safety_data_sheet',
            'flavor': flavor,
            'ingredient_statement': ingredient_statement,
            'ld50_dict': ld50_dict,
            'sds_info': sds_info,
            'experimental': experimental,
        },
     )

@flavor_info_wrapper
def flavor_hazard_details(request, flavor):
    return hazard_calculator(request, sds_object=flavor)


def outdated_raw_material_list(request):

    outdated_raw_material_list = []

    todays_date = date.today()
    one_year_ago = todays_date - relativedelta(years=1)
    two_years_ago = todays_date - relativedelta(years=2)

    #only get ingredients that are in flavors that were sold in the past two years

    for ing in Ingredient.objects.filter(sub_flavor=None,discontinued=False,purchase_price_update__lt=one_year_ago).exclude(suppliercode='FDI').exclude(supplier=None):

        rm_retains = RMRetain.objects.filter(pin=ing.id)
        try:
            most_recent_qc_date = rm_retains[0].date
            outdated_raw_material_list.append((ing, most_recent_qc_date))
        except IndexError:
            last_date = "No Retains"
            outdated_raw_material_list.append((ing, last_date))

#         lots_created_within_two_years = 0
#         for lw in LeafWeight.objects.filter(ingredient__in=[ing]):
#             for lot in lw.root_flavor.lot_set.all():
#                 if lot.date >= two_years_ago:
#                     lots_created_within_two_years += 1
#
#         if lots_created_within_two_years > 0:
#             outdated_raw_material_list.append((ing, lots_created_within_two_years))


    #Use the following to sort by most recent QC date
    #outdated_raw_material_list.sort(key=lambda x: x[1], reverse=True)

    #Use the following to sort by supplier first
    outdated_raw_material_list.sort(key=lambda x: x[0].supplier.suppliercode)


    paginator = Paginator(outdated_raw_material_list, 50)
    page = request.GET.get('page')
    try:
        raw_materials = paginator.page(page)
    except PageNotAnInteger:
        raw_materials = paginator.page(1)
    except EmptyPage:
        raw_materials = paginator.page(paginator.num_pages)

    return render(
        request,
        'access/ingredient/outdated_raw_material_list.html',
        {
            'page_title': 'Outdated Raw Materials',
            'window_title': 'Outdated Raw Materials',
            'outdated_raw_material_list': raw_materials,
        },
    )


def cas_number_discrepancies(request):
    cas_number_discrepancy_list = []

    for ing in Ingredient.objects.filter(sub_flavor=None,discontinued=False).exclude(cas=''):
        if not GHSIngredient.objects.filter(cas=ing.cas).exists():
            related_product_count = LeafWeight.objects.filter(ingredient=ing, root_flavor__sold=True,root_flavor__valid=True,root_flavor__approved=True).count()
            cas_number_discrepancy_list.append((ing, related_product_count))

    cas_number_discrepancy_list.sort(key=lambda x: x[1], reverse=True)

    paginator = Paginator(cas_number_discrepancy_list, 200)
    page = request.GET.get('page')

    try:
        raw_materials = paginator.page(page)
    except PageNotAnInteger:
        raw_materials = paginator.page(1)
    except EmptyPage:
        raw_materials = paginator.page(paginator.num_pages)

    return render(
        request,
        'access/ingredient/cas_number_discrepancies.html',
        {
            'page_title': 'CAS Number Discrepancies',
            'window_title': 'CAS Number Discrepancies',
            'raw_material_list': raw_materials,
        },
     )

def missing_cas_numbers(request):

    no_cas_ingredients = Ingredient.objects.filter(sub_flavor=None,discontinued=False,cas='')
    no_cas_ingredient_list = []

    for ing in no_cas_ingredients:
        #Remove solutions from the list because they can be separated into their two components (solute and substrate)
        #Keep solutions if they are missing solute or substrate ids
        if Solution.objects.filter(ingredient=ing).exists():
            sol = Solution.objects.get(ingredient=ing)
            if sol.my_base_id == None or sol.my_solvent_id == None:
                related_product_count = LeafWeight.objects.filter(ingredient=ing, root_flavor__sold=True,root_flavor__valid=True,root_flavor__approved=True).count()
                no_cas_ingredient_list.append((ing, related_product_count))
        else:
            related_product_count = LeafWeight.objects.filter(ingredient=ing, root_flavor__sold=True,root_flavor__valid=True,root_flavor__approved=True).count()
            no_cas_ingredient_list.append((ing, related_product_count))

    #Sort list by number of products that the ingredient is in
    no_cas_ingredient_list.sort(key=lambda x: x[1], reverse=True)

    paginator = Paginator(no_cas_ingredient_list, 200)
    page = request.GET.get('page')

    try:
        raw_materials = paginator.page(page)
    except PageNotAnInteger:
        raw_materials = paginator.page(1)
    except EmptyPage:
        raw_materials = paginator.page(paginator.num_pages)

    return render(
        request,
        'access/ingredient/missing_cas_raw_materials.html',
        {
            'page_title': 'No CAS Raw Materials',
            'window_title': 'No CAS Raw Materials',
            'raw_material_list': raw_materials,
        },
    )

def ingredient_statement(request):
    #this view will allow a user to enter in a product number to edit/create/verify its ingredient statement
    #it could also display a list of flavors whose ingredient statements need to be verified

    if request.method == 'POST':
        form = forms.ProductNumberForm(request.POST)
        if form.is_valid(): #TODO we can use form validation to make sure the product exists
            product_number = form.cleaned_data['product_number']

            return HttpResponseRedirect("/access/ingredient_statement/%s/" % product_number)

#             #now we check whether or not an IngredientStatement object exists for this product
#             #if it does not exist, go to the create view
#             #if it does exist, go to the verify/edit view
#             if IngredientStatement.objects.filter(flavor__number=product_number).exists():
#                 if IngredientStatement.objects.get(flavor__number=product_number).verified:
#                     redirect_string = "edit"
#                 else:
#                     redirect_string = "verify"
#             else:
#                 redirect_string = "create"
#
#             return HttpResponseRedirect("access/ingredient_statement/%s/%s/" % (product_number, redirect_string))

    else:
        form = forms.ProductNumberForm()

    page_title = "Ingredient Statements"

    return render(request, 'access/flavor/ingredient_statement_home.html', {'product_number_form':form})

@flavor_info_wrapper
def ingredient_statement_review(request, flavor):
    #this is the ingredient statement page for a flavor; it shows the status of the ingredient statement (if there is one)
    if request.method == 'POST':
        if request.POST.get('create'): #if the user clicked create
            return HttpResponseRedirect("/access/ingredient_statement/%s/edit" % flavor.number)

        elif request.POST.get('verify'): #if the user clicked verify
            #that means that an ingredient statement already exists for the product, just verify and save it
            ingredient_statement = IngredientStatement.objects.get(flavor=flavor)
            ingredient_statement.verified = True
            ingredient_statement.save()
            return HttpResponseRedirect("/access/ingredient_statement/%s" % flavor.number)

        elif request.POST.get('edit'): #if the user clicked edit
            #the ingredient statement may or may not be verified, but it will be after editing no matter what
            return HttpResponseRedirect("/access/ingredient_statement/%s/edit" % flavor.number)

    page_title = "Ingredient Statement Review"

    if IngredientStatement.objects.filter(flavor=flavor).exists():
        ingredient_statement = IngredientStatement.objects.get(flavor=flavor)
    else:
        ingredient_statement = None

    return render(
        request,
        'access/flavor/ingredient_statement_review.html',
        {
            'flavor': flavor,
            'ingredient_statement': ingredient_statement
        },
     )

@flavor_info_wrapper
def ingredient_statement_edit(request, flavor):

    #users will edit/create ingredient statements in this view
    if IngredientStatement.objects.filter(flavor=flavor).exists():
        ingredient_statement = IngredientStatement.objects.get(flavor=flavor)
        initial_data = {'ingredient_statement':ingredient_statement.ingredient_statement}
        context = 'Edit' #context will either be 'Edit' or 'Create'
    else:
        ingredient_statement = None
        initial_data = None
        context = 'Create'

    if request.method == 'POST':
        form = forms.IngredientStatementForm(request.POST)
        if form.is_valid():
            statement = form.cleaned_data['ingredient_statement']

            if context == 'Edit': #use context to determine whether to create or edit existing ingredient statement
                ingredient_statement.ingredient_statement = statement
                ingredient_statement.verified = True
                ingredient_statement.edited = True

            elif context == 'Create':
                ingredient_statement = IngredientStatement(flavor = flavor,
                                                           ingredient_statement = statement,
                                                           verified = True,
                                                           extracted_from_spec_sheet = False)

            ingredient_statement.save()

            return HttpResponseRedirect("/access/ingredient_statement/%s/" % flavor.number)

    else:
        form = forms.IngredientStatementForm(initial=initial_data)

    page_title = "%s Ingredient Statement" % context

    return render(
        request,
        'access/flavor/ingredient_statement_edit.html',
        {
            'ingredient_statement_form':form,
            'flavor': flavor,
            'context': context
        },
    )

def active_purchase_orders(request):

    active_purchase_orders = PurchaseOrder.objects.filter(due_date__gte=date.today())#date.today())

    po_rows = []
    for po in active_purchase_orders:
        total_orders = PurchaseOrderLineItem.objects.filter(po=po).count()
        orders_closed = PurchaseOrderLineItem.objects.filter(po=po).filter(closed=True).count()
        #orders_received = PurchaseOrderLineItem.objects.filter(po=po).exclude(date_received=None).count()

        po_rows.append([po, orders_closed, total_orders])

    return render(
        request,
        'access/purchase/purchase_order_list.html',
        {
            'title': 'Active Purchase Orders',
            'po_rows':po_rows
        },
    )

def purchase_orders_within_one_year(request):

    purchase_orders_from_current_year = PurchaseOrder.objects.filter(due_date__gte=date.today()-relativedelta(years=1))

    po_rows = []
    for po in purchase_orders_from_current_year:
        total_orders = PurchaseOrderLineItem.objects.filter(po=po).count()
        orders_closed = PurchaseOrderLineItem.objects.filter(po=po).filter(closed=True).count()
        #orders_received = PurchaseOrderLineItem.objects.filter(po=po).exclude(date_received=None).count()

        po_rows.append([po, orders_closed, total_orders])

    return render(
        request,
        'access/purchase/purchase_order_list.html',
        {
            'title': 'Purchase Orders since %s' % (date.today()-relativedelta(years=1)).strftime('%b %d, %Y'),
            'po_rows':po_rows
        },
    )

def purchase_order_review(request, po_number):

    po = PurchaseOrder.objects.get(number=po_number)
    poli_rows = PurchaseOrderLineItem.objects.filter(po=po)

    return render(
        request,
        'access/purchase/purchase_order_review.html',
        {
            'po':po,
            'poli_rows':poli_rows
        },
    )

@transaction.atomic
def receiving_log_edit(request, po_number, poli_pk):
    po = PurchaseOrder.objects.get(number=po_number)
    poli = PurchaseOrderLineItem.objects.get(pk=poli_pk)
    raw_material = poli.raw_material

    total_amount_requested = poli.quantity * poli.package_size

    '''
    1st Case:
    POLI has NO receivinglog yet.  There is no initial data.
    'How many supplier lots have been received?' -> User inputs amount
    Render formset, use fills out and hits submit

    If the amount received has reached the amount requested:
        'Would you like to close this raw material order or leave it open?' Close / Leave Open
    If the amount received has NOT reached the amount requested:
        'The amount received DOES NOT add up to the amount requested.  What would you like to do?' Close / Leave Open / Add Lot(s)


    2nd Case:
    POLI has been partially completed, but is still open.  User is adding lot(s) to complete the POLI.
        'This order has been partially received but is still open.  Would you like to add more lots or close the order?'
    '''

    #find out if there are any receivinglogs for the poli - if yes, use those as initial data
    if poli.received:
        receiving_log_exists = True
    else:
        receiving_log_exists = False

    ReceivingLogDynamicFormSet = formset_factory(ReceivingLogDynamicForm, extra=0)

    staticform = None
    formset = None

    if request.method == 'POST':

        #Find out whether the user clicked 'close' or 'leave open'
        if 'submit-close' in request.POST:
            closed = True
        else:
            closed = False

        staticform = ReceivingLogStaticForm(request.POST)
        formset = ReceivingLogDynamicFormSet(request.POST)
        if staticform.is_valid() and formset.is_valid():

            trucking_company = staticform.cleaned_data['trucking_company']
            manufacturer = staticform.cleaned_data['manufacturer']
            supplier = staticform.cleaned_data['supplier']


            net_inventory = 0

            for form in formset.forms:
                '''
                Check if the 'already_created' form field is True or False
                If True, find the existing rm_retain and edit that data
                If False, create a new rm_retain
                '''
                already_created = form.cleaned_data['already_created']
                r_number = form.cleaned_data['r_number']
                date_received = form.cleaned_data['date_received']
                amount_received = form.cleaned_data['amount_received']
                supplier_lot = form.cleaned_data['supplier_lot']
                cp3_received = form.cleaned_data['cp3_received']

                update_inventory = False

                if already_created:
                    rm_retain = None
                    receiving_log = None

                    for rl in poli.receivinglog_set.all():
                        if rl.rm_retain.r_number == r_number and rl.rm_retain.date.year == date_received.year:
                            receiving_log = rl
                            rm_retain = rl.rm_retain

                            #If the receiving log had already been previously created, we want to subtract the previously
                            # entered amount_received value before adding the new one
                            net_inventory -= rl.amount_received

                    if rm_retain == None:
                        #This error should never be raised.  Something's wrong with my logic if it is
                        raise ValueError('There is no rm_retain with R# %d and year %d associated with this Purchase Order' % (r_number, date_received.year))

                else: #This is a brand new ReceivingLog; create one using the cleaned data, and create a new RMRetain as well
                    receiving_log = ReceivingLog(poli=poli)
                    rm_retain = RMRetain(r_number=RMRetain.get_next_r_number(), status="Pending")
                    receiving_log.rm_retain = rm_retain
                    update_inventory = True

                #Set the fields taken from the static form
                receiving_log.trucking_company = trucking_company
                receiving_log.supplier = supplier
                receiving_log.manufacturer = manufacturer

                #Set the fields taken from the dynamic formset
                receiving_log.date_received = date_received
                receiving_log.amount_received = amount_received.normalize()
                receiving_log.supplier_lot = supplier_lot
                receiving_log.cp3_received = cp3_received

                #Set the rm_retain fields
                rm_retain.date=receiving_log.date_received
                rm_retain.pin=receiving_log.poli.raw_material.id
                rm_retain.supplier=receiving_log.supplier
                rm_retain.lot=receiving_log.supplier_lot

                rm_retain.save()

                '''
                When the receiving_log is saved, it automatically creates a new inventory log and updates the RMs inventory.
                There's no need to manually update the raw material's inventory.
                '''
                receiving_log.save()
                # receiving_log.poli.raw_material.recalculate_inventory()


                #IF a new receiving log was just created,
                # create an IngredientInventoryLog object that poitns to the newly created receiving log
                # if update_inventory == True:
                #     receiving_log_type = ContentType.objects.get_for_model(receiving_log)
                #     if IngredientInventoryLog.objects.filter(object_id=receiving_log.id, content_type=receiving_log_type).exists():
                #         #this is a redundant check; if it was just created there should not be an inventory log for it yet
                #         #however, if somehow the code messes up and object_id is not saved for mutliple IILs, it might happen
                #         raise ValueError('A new receiving log %s was created but an inventorylog %s already exists for it.'
                #                          % (receiving_log.id,  IngredientInventoryLog.objects.filter(object_id=receiving_log.id, content_type=receiving_log_type)[0].id))
                #     else:
                #         receiving_log.update_rm_inventory()

            # Set the POLI 'closed' field to true or false depending on which submit button they clicked
            poli.closed = closed
            poli.save()

            return HttpResponseRedirect('/access/purchase_orders/%s/' % po.number)

    if staticform == None and formset == None:
        if poli.receivinglog_set.count() > 0:
            static_initial = {
                'trucking_company':poli.receivinglog_set.all()[0].trucking_company,
                'supplier':poli.receivinglog_set.all()[0].supplier,
                'manufacturer':poli.receivinglog_set.all()[0].manufacturer
            }
            dynamic_initial = []
            for receivinglog in poli.receivinglog_set.order_by('rm_retain__r_number'):
                dynamic_initial.append({
                    'r_number':receivinglog.rm_retain.r_number,
                    'date_received':receivinglog.date_received,
                    'amount_received':receivinglog.amount_received,
                    'supplier_lot':receivinglog.supplier_lot,
                    'cp3_received':receivinglog.cp3_received,
                    'already_created': True,
                })
        else:
            static_initial = {'supplier':poli.po.supplier, 'manufacturer':poli.po.supplier,}
            dynamic_initial = [{'already_created': False}]

        staticform = ReceivingLogStaticForm(initial=static_initial)
        formset = ReceivingLogDynamicFormSet(initial=dynamic_initial)

    return render(
        request,
        'access/purchase/receiving_log_edit.html',
        {
            'staticform':staticform,
            'formset':formset,
            'management_form':formset.management_form,
            'po': po,
            'poli': poli,
            'raw_material': raw_material,
            'total_amount_requested': total_amount_requested,
            'receiving_log_exists': receiving_log_exists
        },
    )


def get_ingredient_name(request): #used for a jquery.get() request
    pin = request.GET['pin']
    response_dict = {}
    try:
        ingredient = Ingredient.objects.get(id=pin, discontinued=False)
    except:
        ingredient = None
    if ingredient is not None:
        response_dict['name'] = ingredient.long_name
    else:
        if pin == '':
            response_dict['name'] = ''
        else:
            response_dict['name'] = "Invalid Ingredient Number"

    return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')

def rm_inventory_data_entry(request):
    #this view deals with entering inventory data for raw materials
    #users enter in a pin number, amount and quantity and the amount*quantity for that pin is added to the raw material's inventory field

    formset = None
    RMInventoryFormSet = formset_factory(RMInventoryForm, extra=20)
    if request.method == 'POST':

        formset = RMInventoryFormSet(request.POST)
        if formset.is_valid():

            inventory_dict = {}

            for form in formset:
                try:
                    pin = form.cleaned_data['pin']
                    amount = form.cleaned_data['amount']
                    quantity = form.cleaned_data['quantity']

                    i = Ingredient.objects.get(id=pin, discontinued=False)
                    if i not in inventory_dict:
                        inventory_dict[i] = amount * quantity
                    else:
                        inventory_dict[i] += amount * quantity

                except KeyError:
                    continue

            for i, total in inventory_dict.items():
                #Create an IngredientInventoryLog for each item updated
                inventory_log = IngredientInventoryLog(
                    ingredient = i,
                    delta = total,
                    comment = "Inventory data entered.  Adding %0.4f lbs of PIN#%d to inventory." % (total, i.id),
                )
                inventory_log.save()
                inventory_log.update_ingredient_inventory()

            if inventory_dict:
                #only proceed to the summary page if at least one raw material was entered
                return render(request, 'access/ingredient/inventory_success_form.html', {'inventory_dict':inventory_dict,})

    if formset == None:
        formset = RMInventoryFormSet()

    return render(
        request,
        'access/ingredient/inventory_data_entry.html',
        {
            'formset': formset,
            'management_form': formset.management_form,
        },
    )


def rm_nutri_edit(request):
    major = ["Carbohydrates", "Ash", "Calories", "Protein", "Other Fat", "Water", "Flavor Content", "Alcohol Content"]
    subcategroygrams = ["Saturated Fat", "Monounsaturated Fat", "Polyunsaturated Fat", "Sugars", "Added Sugars", "Dietary Fiber", 'Ethyl Alcohol', 'Fusel Oil', 'Propylene Glycol', 'Triethyl Citrate', 'Glycerin', 'Triacetin']
    hide = ["GmWt 1", "GmWt Desc1", "GmWt 2", "GmWt Desc2", "Refuse Pct", "WaterAmount"]
    subcategroymicrograms = ["Vitamin A", "Vitamin D"]
    if request.method == 'GET':
        form = searchForm(request.GET)
        hyperlinked = request.GET.get('rm')
        if hyperlinked == None or hyperlinked == '':
            if form.is_valid():
                #check if raw material search already exists as a nutriinfo object
                ing = int(form.cleaned_data['rm_search'])
                if not NutriInfo.objects.filter(ingredient__id = int(form.cleaned_data['rm_search']), ingredient__discontinued=False).exists() and Ingredient.objects.filter(id = int(form.cleaned_data['rm_search'])).exists():
                    i = Ingredient.objects.get(id = ing, discontinued=False)
                    newMessage = "No information for this raw material has been entered. Please fill the fields to the best of your knowledge."
                    nutriform = nutriForm(initial={'Shrt_Desc':i.art_nati+i.prefix+" "+i.product_name, 'Trans_Fat':Decimal(0), 'Water':Decimal(0), 'Calories':Decimal(0), 'Protein':Decimal(0), 'TotalFat':Decimal(0), 'Carbohydrt':Decimal(0), 'Fiber_TD':Decimal(0), 'Ash':Decimal(0),
                                                    'Calcium':Decimal(0), 'Phosphorus':Decimal(0), 'Iron':Decimal(0), 'Sodium':Decimal(0), 'Potassium':Decimal(0), 'Magnesium':Decimal(0), 'Zinc':Decimal(0), 'Copper':Decimal(0),
                                                    'Manganese':Decimal(0), 'Selenium':Decimal(0), 'Vit_A':Decimal(0), 'Vit_E':Decimal(0), 'Thiamin':Decimal(0), 'Riboflavin':Decimal(0), 'Niacin':Decimal(0), 'Panto_acid':Decimal(0),
                                                    'Vit_B6':Decimal(0), 'Folate':Decimal(0), 'Vit_B12':Decimal(0), 'Vit_C':Decimal(0), 'FA_Sat':Decimal(0), 'FA_Mono':Decimal(0), 'FA_Poly':Decimal(0), 'Cholestrl':Decimal(0), 'GmWt_1':Decimal(0),
                                                    'GmWt_2':Decimal(0), 'Refuse_Pct':Decimal(0), 'WaterAmount':Decimal(0),
                                                    'AlcoholContent':Decimal(0) ,'ethyl':Decimal(0),'fusel':Decimal(0), 'pg':Decimal(0), 'tri_citrate':Decimal(0), 'glycerin':Decimal(0), 'triacetin':Decimal(0),
                                                    'FlavorContent':Decimal(0), 'Added_Sugars':Decimal(0), 'Sugars':Decimal(0), 'Vit_D':Decimal(0),
                                                    'Sugar_Alcohols':Decimal(0), 'GmWt_Desc1':"N/A", 'GmWt_Desc2':"N/A"
                                                    })
                    form = searchForm()
                    return render(request,
                        'access/ingredient/rm_nutri_edit.html',
                        {
                            'ingredient':i,
                            'hide':hide,
                            'ing':ing,
                            'saved':newMessage,
                            'form':form,
                            'nutriform': nutriform,
                            'major':major,
                            'grams':subcategroygrams,
                            'mcg':subcategroymicrograms,
                        },
                    )
                else:
                    nutri = NutriInfo.objects.get(ingredient__id = int(form.cleaned_data['rm_search']),ingredient__discontinued=False)
                    nutriform = nutriForm(instance = nutri)
                    form = searchForm()
                    return render(
                        request,
                        'access/ingredient/rm_nutri_edit.html',
                        {
                            'ingredient':nutri.ingredient,
                            'hide':hide,
                            'nutri':nutri,
                            'ing':ing,
                            'form':form,
                            'nutriform': nutriform,
                            'major':major,
                            'grams':subcategroygrams,
                            'mcg':subcategroymicrograms,
                        },
                    )
        else:
            ing = int(hyperlinked)
            newMessage = ""
            #k = Ingredient.objects.get(id = ing, discontinued=False)

            #if no nutri currently exists for the hyperlinked ingredient (copied from code above, could use rework)
            if not NutriInfo.objects.filter(ingredient__id=ing, ingredient__discontinued=False).exists() and Ingredient.objects.filter(id=ing).exists():
                i = Ingredient.objects.get(id=ing, discontinued=False)
                newMessage = "No information for this raw material has been entered. Please fill the fields to the best of your knowledge."
                nutriform = nutriForm(
                    initial={'Shrt_Desc': i.art_nati + i.prefix + " " + i.product_name, 'Trans_Fat': Decimal(0),
                             'Water': Decimal(0), 'Calories': Decimal(0), 'Protein': Decimal(0), 'TotalFat': Decimal(0),
                             'Carbohydrt': Decimal(0), 'Fiber_TD': Decimal(0), 'Ash': Decimal(0),
                             'Calcium': Decimal(0), 'Phosphorus': Decimal(0), 'Iron': Decimal(0), 'Sodium': Decimal(0),
                             'Potassium': Decimal(0), 'Magnesium': Decimal(0), 'Zinc': Decimal(0), 'Copper': Decimal(0),
                             'Manganese': Decimal(0), 'Selenium': Decimal(0), 'Vit_A': Decimal(0), 'Vit_E': Decimal(0),
                             'Thiamin': Decimal(0), 'Riboflavin': Decimal(0), 'Niacin': Decimal(0),
                             'Panto_acid': Decimal(0),
                             'Vit_B6': Decimal(0), 'Folate': Decimal(0), 'Vit_B12': Decimal(0), 'Vit_C': Decimal(0),
                             'FA_Sat': Decimal(0), 'FA_Mono': Decimal(0), 'FA_Poly': Decimal(0),
                             'Cholestrl': Decimal(0), 'GmWt_1': Decimal(0),
                             'GmWt_2': Decimal(0), 'Refuse_Pct': Decimal(0), 'WaterAmount': Decimal(0),
                             'AlcoholContent': Decimal(0),
                             'ethyl':Decimal(0), 'fusel':Decimal(0), 'pg':Decimal(0), 'tri_citrate':Decimal(0), 'glycerin':Decimal(0), 'triacetin':Decimal(0),
                             'FlavorContent': Decimal(0), 'Added_Sugars': Decimal(0),
                             'Sugars': Decimal(0), 'Vit_D': Decimal(0),
                             'Sugar_Alcohols': Decimal(0), 'GmWt_Desc1': "N/A", 'GmWt_Desc2': "N/A"
                             })
                form = searchForm()
                return render(request,
                              'access/ingredient/rm_nutri_edit.html',
                              {
                                'ingredient':i,
                                'hide': hide,
                                'ing': ing,
                                'saved': newMessage,
                                'form': form,
                                'nutriform': nutriform,
                                'major': major,
                                'grams': subcategroygrams,
                                'mcg': subcategroymicrograms,
                              },
                              )

            nutri = NutriInfo.objects.get(ingredient__id=ing, ingredient__discontinued=False)
            nutriform = nutriForm(instance = nutri)

            form = searchForm()
            return render(
                request,
                'access/ingredient/rm_nutri_edit.html',
                {
                    'ing':ing,
                    'saved':newMessage,
                    'form':form,
                    'nutriform': nutriform,
                    'major':major,
                    'grams':subcategroygrams,
                    'mcg':subcategroymicrograms,
                },
            )

    if request.method == 'POST':
        search = searchForm()
        saved = "Updates have been saved"

        inputForm = nutriForm(request.POST)
        if inputForm.is_valid():
            ing = request.POST.get("ing", "")
            if not NutriInfo.objects.filter(ingredient__id = int(ing), ingredient__discontinued=False).exists() and Ingredient.objects.filter(id = int(ing)).exists():
                #create new nutriinfo object if it exists in ingredient table
                inputForm = inputForm.save(commit=False)
                inputForm.ingredient = Ingredient.objects.get(id = int(ing), discontinued=False)
                inputForm.save()
                nutriObject = NutriInfo.objects.get(ingredient__id = ing, ingredient__discontinued=False)
                nutriform = nutriForm(instance = nutriObject)
                return render(
                    request,
                    'access/ingredient/rm_nutri_edit.html',
                    {
                        'ing':ing,
                        'form':search,
                        'saved':saved,
                        'nutri':nutriObject,
                        'nutriform':nutriform,
                        'major':major,
                        'grams':subcategroygrams,
                        'mcg':subcategroymicrograms,
                    },
                )


            else:             #update the existing nutriObject
                nutriObject = NutriInfo.objects.get(ingredient__id = ing, ingredient__discontinued=False)
                form = nutriForm(request.POST, instance=nutriObject)
                form.save()
                return render(
                    request,
                    'access/ingredient/rm_nutri_edit.html',
                    {
                        'ing':ing,
                        'form':search,
                        'saved':saved,
                        'nutri':nutriObject,
                        'nutriform':form,
                        'major':major,
                        'grams':subcategroygrams,
                        'mcg':subcategroymicrograms,
                    },
                )
        else:
            saved = "did not save"
            search = searchForm()
            return render(
                request,
                'access/ingredient/rm_nutri_edit.html',
                {
                    'form':search,
                    'saved':saved,
                    'major':major,
                    'grams':subcategroygrams,
                    'mcg':subcategroymicrograms,
                },
            )
    form = searchForm()
    #nutri = NutriInfo.objects.get(ingredient = 5829)
    return render(request, 'access/ingredient/rm_nutri_edit.html', {'form': form})

def myround(x, base):
    if (base * round(float(x)/base)) <= base:
        return 0
    else:
        return (base * round(float(x)/base))

def flavor_nutri_facts(request, flavor_number=None): #nutri labeling tool
    form = searchForm()
    totalFat, satFats, transFats, polyFats, monoFats, water, protein, totalCarbs, sugars, addedSugar, fiber, ash, chemicals, alcohol = Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)
    vitaminA, vitaminB6, vitaminB12, vitaminC, vitaminD, vitaminE, thiamin, ribo, niacin, panto, folate = Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)
    calcium, phosphorus, iron, sodium, potassium, mangnesium, zinc, copper, manganese, selenium = Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)
    calories, cholesterol, otherFats, ethyl ,fusel, pg, tri_ci, glycerin, triacetin = Decimal(0),Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0),Decimal(0), Decimal(0),
    arr = []
    nonExistentNi = []
    ing = 0
    warning = "Following raw materials do not add up to 100: <br><br>"
    errors = False

    message = "The following Ingredients do not have NutriInfo objects. Please enter nutritional information for the following Ingredients and try again."

    major = ["Carbohydrates", "Ash", "Calories", "Protein",   "Water Weight", "Flavor Content", "Alcohol Content", "Total Carbohydrates", 'Total Fat']
    subcategorygrams = ["Saturated Fat", "Monounsaturated Fat", "Polyunsaturated Fat", "Sugars", "Added Sugars", "Dietary Fiber"]
    subcategorymicrograms = ["Vitamin A", "Vitamin D"]

    if flavor_number == None and request.method != "POST":
        return render(
            request,
            'access/flavor/flavor_nutri_facts.html',
            {
                'form': form,
            },
        )

    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            ing = int(form.cleaned_data['rm_search'])
            fl = Flavor.objects.get(number = ing)
    else:
        fl = Flavor.objects.get(number = flavor_number)

    # name = fl
    #if indgredient doesnt have corresponding ni object, make list of them and warn user
    for lw in LeafWeight.objects.filter(root_flavor=fl):

        if not NutriInfo.objects.filter(ingredient=lw.ingredient).exists() and Ingredient.objects.filter(id=lw.ingredient.id).exists():
            nonExistentNi.append(lw.ingredient)



    if len(nonExistentNi) > 0:
        return render(
            request,
            'access/flavor/flavor_nutri_facts.html',
            {
                'message':message,
                'nonExistentNi':nonExistentNi,
                'form': form,
            },
        )
    else:
        for lw in LeafWeight.objects.filter(root_flavor=fl):

            nutriobj = NutriInfo.objects.get(ingredient=lw.ingredient)
            arr.append(nutriobj)
            percent = lw.weight/Decimal(1000.0)

            water       += percent * nutriobj.Water
            protein     += percent * nutriobj.Protein

            totalCarbs  += percent * nutriobj.Carbohydrt
            sugars      += percent * nutriobj.Sugars
            fiber       += percent * nutriobj.Fiber_TD


            addedSugar  += percent * nutriobj.Added_Sugars

            otherFats   += percent * nutriobj.TotalFat
            satFats     += percent * nutriobj.FA_Sat
            transFats   += percent * nutriobj.Trans_Fat #reported not calculated
            polyFats    += percent * nutriobj.FA_Poly
            monoFats    += percent * nutriobj.FA_Mono

            ash         += percent * nutriobj.Ash
            vitaminA    += percent * nutriobj.Vit_A
            vitaminB6   += percent * nutriobj.Vit_B6
            vitaminB12  += percent * nutriobj.Vit_B12
            vitaminC    += percent * nutriobj.Vit_C
            vitaminD    += percent * nutriobj.Vit_D
            vitaminE    += percent * nutriobj.Vit_E
            thiamin     += percent * nutriobj.Thiamin
            ribo        += percent * nutriobj.Riboflavin
            niacin      += percent * nutriobj.Niacin
            panto       += percent * nutriobj.Panto_acid
            folate      += percent * nutriobj.Folate
            calcium     += percent * nutriobj.Calcium
            phosphorus  += percent * nutriobj.Phosphorus
            iron        += percent * nutriobj.Iron
            sodium      += percent * nutriobj.Sodium
            potassium   += percent * nutriobj.Potassium
            mangnesium  += percent * nutriobj.Magnesium
            zinc        += percent * nutriobj.Zinc
            copper      += percent * nutriobj.Copper
            manganese   += percent * nutriobj.Manganese
            selenium    += percent * nutriobj.Selenium
            cholesterol += percent * nutriobj.Cholestrl

            chemicals += percent * nutriobj.FlavorContent
            # alcohol += percent * nutriobj.AlcoholContent
            ethyl += percent * nutriobj.ethyl
            fusel += percent * nutriobj.fusel
            pg += percent * nutriobj.pg
            tri_ci += percent * nutriobj.tri_citrate
            glycerin += percent * nutriobj.glycerin
            triacetin += percent * nutriobj.triacetin

            rmtotal = nutriobj.total

            if rmtotal > 102 or rmtotal < 98:
                errors = True
                warning += "<a href = '../../rm_nutri_edit/?rm=" + str(lw.ingredient.id)+"' target='_blank'>" + str(lw.ingredient.id) + " " + nutriobj.Shrt_Desc + "</a>: " + str(rmtotal) + "<br>"


        totalFat = Decimal(myround(satFats,.5)) + Decimal(myround(polyFats,.5)) + Decimal(myround(monoFats,.5)) + Decimal(myround(otherFats, .5))
        totalC = Decimal(myround(totalCarbs, 1)) + Decimal(myround(sugars,.5)) + Decimal(myround(fiber,1))

        # calories calculated differently depending on alcohol type
        alcohol = fusel + pg + tri_ci + glycerin + triacetin + ethyl
        alcohol_calories = (fusel + ethyl) * 7 + pg * 4 + tri_ci * Decimal(3.7) + glycerin * 4 + triacetin * Decimal(1.7)
        calories = 4 * (protein + totalCarbs + sugars + fiber) + 9 * totalFat + alcohol_calories
        # something wrong with following lines...prolly
        total = water + protein + totalCarbs + ash + chemicals + alcohol + totalFat

        if total > 102 or total < 98:
            warning += "<br> This flavor does not meet satisfactory weight requirements. Please check/edit this flavor's ingredients and try again. " + str(total) + "<br>"

        weights = [
                   ("Calories",myround(calories,5)),
                   ("Water Weight",myround(water, .5)),
                   ("Protein" ,myround(protein,1)),
                   ("Total Carbohydrates" , totalC),
                   ("Other Carbohydrates" , myround(totalCarbs, 1)),
                   ("Sugars" , myround(sugars, .5)),
                   ("Added Sugars" , myround(addedSugar, .5)),
                   ("Fiber" , myround(fiber, 1)),
                   ("Total Fat" , totalFat),
                   ("Other Fat" , myround(otherFats, .5)),
                   ("Saturated Fat" , myround(satFats,.5)),
                   ("Trans Fat" , myround(transFats,.5)),
                   ("Polyunsaturated Fat" , myround(polyFats,.5)),
                   ("Monounsaturated Fats" , myround(monoFats,.5)),
                   ("Cholesterol" , myround(cholesterol, 2)),
                   ("Ash" , myround(ash,.01)),
                   ("Vitamin A" , myround(vitaminA, 20)),
                   ("Vitamin B6" , myround(vitaminB6, .01)),
                   ("Vitamin B12" , myround(vitaminB12,.01)),
                   ("Vitamin C" , myround(vitaminC, .01)),
                   ("Vitamin D" , myround(vitaminD, .01)),
                   ("Vitamin E" , myround(vitaminE, .01)),
                   ("Thiamin" , myround(thiamin, .01)),
                   ("Riboflavin" , myround(ribo, .01)),
                   ("Niacin" , myround(niacin, .01)),
                   ("Pantothenic Acid" , myround(panto, .01)),
                   ("Folate" , myround(folate,.01)),
                   ("Calcium" , myround(calcium, .01)),
                   ("Phosphorus" , myround(phosphorus, .01)),
                   ("Iron" , myround(iron, .01)),
                   ("Sodium" , myround(sodium, 5)),
                   ("Potassium" , myround(potassium, 5)),
                   ("Magnesium" , myround(mangnesium, .01)),
                   ("Zinc" , myround(zinc, .01)),
                   ("Copper" , myround(copper, .01)),
                   ("Manganese" , myround(manganese, .01)),
                   ("Selenium" , myround(selenium, .01)),
                   #round(chemicals, 3), round(alcohol, 3), round(total, 3),
        ]
        weight = collections.OrderedDict(weights)
        return render(
            request,
            'access/flavor/flavor_nutri_facts.html',
            {
                'errors':errors,
                'warning':warning,
                'nutri': arr,
                'form': form,
                'name':fl,
                'zipped':weight,
                'major':major,
                'subcategorygrams':subcategorygrams,
                'subcategorymicrograms':subcategorymicrograms,
            },
        )

    # return render(
    #     request,
    #     'access/flavor/flavor_nutri_facts.html',
    #     {
    #         'form': form,
    #     },
    # )


def allergen_declaration(request, flavor_number):
    # allergens = ['Wheat* (includes Triticum species & Triticale)', 'Eggs and Egg Products', 'Fish', 'Milk and Milk Products', 'Peanut Products (oil, nut, etc)',
    #         'Crustacean Shellfish', 'Soy (flour, oil, proteins, etc)', 'Sulfur Dioxide and Sulfites', 'Tree Nuts', 'Celery (root, stalk, leaves, not seeds)',
    #         'Lupines and Products thereof', 'Mollusks (oysters, clams, etc)','Mustard and Products thereof', 'Sesame and products thereof','Yellow #5'
    #     ]
    # search = searchForm()
    # if request.method == 'GET':
    #     form = searchForm(request.GET)
    #     if form.is_valid():
    #         flavor = Flavor.objects.get(number = form.cleaned_data['rm_search'])
    #         # stuff = [
    #         #             flavor.wheat, flavor.eggs, flavor.fish, flavor.milk, flavor.peanuts, flavor.crustacean, flavor.soybeans, flavor.sulfites,
    #         #             flavor.treenuts, flavor.celery, flavor.lupines, flavor.mollusks, flavor.mustard, flavor.sesame, flavor.yellow_5
    #         #         ]
    #         # zipped = zip(allergens, stuff)
    # else:
    flavor = Flavor.objects.get(number=flavor_number)

    return render(
        request,
        'access/flavor/allergen_declaration.html',
        {
            'name':flavor,
            # 'form':search,
            'flavor':flavor,
        },
    )
    # return render(request, 'access/flavor/allergen_declaration.html', {'form':search})

def gmo_statement(request, flavor_number):
    search = searchForm()
    fl = Flavor.objects.get(number = flavor_number)
    letter_content = ''
    if fl.gmo_print_review == 'Genetically Modified':
        letter_content = "We have determined that there are Genetically Modified substances in the above product(s)."
        return render(
            request,
            'access/flavor/gmo_statement.html',
            {
                'flavor':fl,
                'letter_content':letter_content,
                'form':search,
            },
        )
    elif fl.gmo_print_review == 'GMO Non-Detect':
        letter_content = """Many of our suppliers claim that their processing either significantly reduces or eliminates the presence of genetically modified fragments. Furthermore, our processing is such that we believe no GM fragments are transmitted to the final product.
                            <br><br>
                            Therefore, it is our belief that there is no detectable Genetically Modified material in the above product(s) if assayed by PCR. However, we cannot confirm this without doing a test on every lot."""
        return render(
            request,
            'access/flavor/gmo_statement.html',
            {
                'flavor':fl,
                'letter_content':letter_content,
                'form':search,
            },
        )
    else:
        letter_content = "To the best of our knowledge and belief we have determined, through documentation from our suppliers, that the above named product(s) have been produced without the use of GMO materials."
        return render(
            request,
            'access/flavor/gmo_statement.html',
            {
                'flavor':fl,
                'letter_content':letter_content,
                'form':search,
            },
        )



def product_spec_sheet(request, flavor_number):

    fl = Flavor.objects.get(number = flavor_number)
    hyperlinked = request.GET.get('productSpecSheet', '')
    try:
        ingredient_statement = IngredientStatement.objects.get(flavor = fl).ingredient_statement
    except:
        ingredient_statement = None
    spec = SpecSheetInfo.objects.filter(flavor = fl)
    storage = "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight."
    shelflife = "9 months to 1 year if stored as recommended."
    warning = ""
    multiple = ""
    emptyFields= []
    extrapowdermessage = "The above microbiological guidelines are based on average results for products of this type.  In accordance with our HACCP protocol, products will be micro-tested based on risk analysis."
    # micro still to be determined
    micro = fl.microsensitive
    isPowder = False

    if fl.phase == "Powder":
        isPowder = True
        storage = "Avoid exposure to excesive heat and direct sunlight."


    if hyperlinked != None and hyperlinked != "":
        update = True
        ing = int(hyperlinked)
        sp = SpecSheetInfo.objects.get(id = ing)
        fl = Flavor.objects.get(number = sp.flavor.number)
        warning = ""
        micro = fl.microsensitive
        standard = False
        #check if it's a standard
        if sp.one_off_customer == '' or sp.one_off_customer == None:
            standard = True

        return render(
                    request,
                    'access/flavor/product_spec_sheet.html',
                    {
                        'warning':warning,
                        'flavor':fl,
                        'ing':ing,
                        'ingredient_statement':ingredient_statement,
                        # 'confirmation':sp,
                        # 'flavor':flavor_number,
                        'micro':micro,
                        'linked':update,
                        'spec':sp,
                        'standard':standard,
                    },
            )


    if(len(spec) == 0):#no specs exist
        warning = "There are currently no Spec Sheets for " + str(fl)
        # multiple +='<form action="../../one_off_specs/?ing='+flavor_number+'&newOneOff=Create+New+One+Off"><input type = "hidden" id="ing" name="ing" value="'+flavor_number+'"><input type="submit" id="newOneOff" name="newOneOff" value="New One Off"/><input type="submit" id="newStandard" name="newStandard" value ="Create New Standard"/></form>'
        multiple = " "

        return render(
            request,
            'access/flavor/product_spec_sheet.html',
            {
                'flavor':fl,
                'ing':flavor_number,
                'warning':warning,
                'multiple':multiple,

                # 'form':search,
                # 'initial':initial,
            }
        )

    if(len(spec) >= 1): #return list of multiple spec sheets
        warning = ""
        multiple += "<h1>%s: Spec Sheets </h1>" % spec[0].flavor.__str__()
        standard = False
        multiple += '<table>'
        for i in spec:
            multiple += '<tr>'
            if(i.one_off_customer == None or i.one_off_customer == ""):
                standard = True
                multiple += '<td><a href="../'+flavor_number+'/?productSpecSheet='+str(i.id)+'">'+"Standard Spec Sheet"+'</a></td> <td><a href="../../one_off_specs/'+ flavor_number +'/?specSheet='+str(i.id)+'">Edit Spec Sheet</a></td>'
            else:
                multiple += '<td><a href="../'+flavor_number+'/?productSpecSheet='+str(i.id)+'">'+str(i.one_off_customer)+'</a></td> <td><a href="../../one_off_specs/'+ flavor_number +'/?specSheet='+str(i.id)+'">Edit Spec Sheet</a></td>'
            multiple += '</tr>'

        multiple += '</table>'
        # if standard:
        #     multiple +='<form method ="POST" action="../../one_off_specs/?ing='+flavor_number+'&newOneOff=Create+New+One+Off"><input type = "hidden" id="ing" name="ing" value="'+flavor_number+'"><input type="submit" id="newOneOff" name="newOneOff" value="New One Off"/></form>'
        # else:
        #     multiple +='<form method ="POST" action="../../one_off_specs/?ing='+flavor_number+'&newOneOff=Create+New+One+Off"><input type = "hidden" id="ing" name="ing" value="'+flavor_number+'"><input type="submit" id="newOneOff" name="newOneOff" value="New One Off"/><input type="submit" id="newStandard" name="newStandard" value ="Create New Standard"/></form>'
        # if standard:
        #     multiple +='<input type = "hidden" id="ing" name="ing" value="'+flavor_number+'"><input type="submit" id="newOneOff" name="newOneOff" value="New One Off"/>'
        # else:
        #     multiple +='<input type = "hidden" id="ing" name="ing" value="'+flavor_number+'"><input type="submit" id="newOneOff" name="newOneOff" value="New One Off"/><input type="submit" id="newStandard" name="newStandard" value ="Create New Standard"/>'

        return render(
                    request,
                    'access/flavor/product_spec_sheet.html',
                    {
                        'warning':warning,
                        'standard':standard,
                        'spec':spec,
                        'ing':flavor_number,
                        'multiple':multiple,
                    },
            )

    return render(
        request,
        'access/flavor/product_spec_sheet.html',
        {
            'warning':warning,
            'emptyFields':emptyFields,
            'isPowder':isPowder,
            'micro':micro,
            'storage':storage,
            'spec':spec,
            'ingredient_statement':ingredient_statement,
            'flavor':fl,
            'flavor':flavor_number,
            'ing':flavor__number,
            'extrapowdermessage':extrapowdermessage,
        },
    )

# def update_mirco(flavor, specform):



def define_spec_params(specform, flavor, update):
    ingredient_statement = IngredientStatement.objects.get(flavor = flavor).ingredient_statement
    if update:
        if flavor.phase == "Powder":
            if flavor.product_category == "Flavorcoat":
                specform.instance.product_name = flavor.name
                specform.instance.product_number = flavor.number
                specform.instance.solubility = flavor.solubility
                # if specform.cleaned_data['sieve'] == None or specform.cleaned_data['sieve'] == '':
                #     specform.instance.sieve = ">98% Thru A USS #10 Mesh"
                # if specform.cleaned_data['moisture'] == None or specform.cleaned_data['moisture'] == '':
                #     specform.instance.moisture = "<10% +/- 2%"
                if specform.cleaned_data['escherichia_coli'] == None or specform.cleaned_data['escherichia_coli'] == '':
                    specform.instance.escherichia_coli = "<10/g"
                if specform.cleaned_data['salmonella'] == None or specform.cleaned_data['salmonella'] == '':
                    specform.instance.salmonella = "Negative/375g"
                if specform.cleaned_data['yeast'] == None or specform.cleaned_data['yeast'] == '':
                    specform.instance.yeast = "200/g Maximum"
                if specform.cleaned_data['mold'] == None or specform.cleaned_data['mold'] == '':
                    specform.instance.mold = "200/g Maximum"
                if specform.cleaned_data['shelf_life'] == None or specform.cleaned_data['shelf_life'] == '':
                    specform.instance.shelf_life = "9 months to 1 year if stored as recommended."
                if specform.cleaned_data['storage'] == None or specform.cleaned_data['storage'] == '':
                    specform.instance.storage = "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive head and direct sunlight."
                specform.instance.description = (flavor.color + " with the taste and aroma of " + flavor.organoleptics).capitalize()
                specform.instance.ingredient_statement = ingredient_statement
                return specform
            else:
                specform.instance.product_name = flavor.name
                specform.instance.product_number = flavor.number
                specform.instance.solubility = flavor.solubility
                specform.instance.description = (flavor.color + " with the taste and aroma of " + flavor.organoleptics).capitalize()
                specform.instance.ingredient_statement = ingredient_statement
                # if specform.cleaned_data['sieve'] == None or specform.cleaned_data['sieve'] == '':
                #     specform.instance.sieve = ">98% Thru A USS #80 Mesh"
                # if specform.cleaned_data['moisture'] == None or specform.cleaned_data['moisture'] == '':
                #     specform.instance.moisture = "5% Max"
                if specform.cleaned_data['escherichia_coli'] == None or specform.cleaned_data['escherichia_coli'] == '':
                    specform.instance.escherichia_coli = "<10/g"
                if specform.cleaned_data['salmonella'] == None or specform.cleaned_data['salmonella'] == '':
                    specform.instance.salmonella = "Negative/375g"
                if specform.cleaned_data['yeast'] == None or specform.cleaned_data['yeast'] == '':
                    specform.instance.yeast = "200/g Maximum"
                if specform.cleaned_data['mold'] == None or specform.cleaned_data['mold'] == '':
                    specform.instance.mold = "200/g Maximum"

                if specform.cleaned_data['shelf_life'] == None or specform.cleaned_data['shelf_life'] == '':
                    specform.instance.shelf_life = "9 months to 1 year if stored as recommended."
                if specform.cleaned_data['storage'] == None or specform.cleaned_data['storage'] == '':
                    specform.instance.storage = "Store in full, tightly closed containers at a cool temperature. Avoid exposure ot excessive head and direct sunglight."
                return specform

        elif flavor.phase == "Liquid":
            if flavor.microsensitive:
                if specform.cleaned_data['aerobic_plate_count'] == None or specform.cleaned_data['aerobic_plate_count'] == '':
                    specform.instance.aerobic_plate_count = "<10,000/gm"
                if specform.cleaned_data['escherichia_coli'] == None or specform.cleaned_data['escherichia_coli'] == '':
                    specform.instance.escherichia_coli = "<10/gm"
                if specform.cleaned_data['salmonella'] == None or specform.cleaned_data['salmonella'] == '':
                    specform.instance.salmonella = "Negative/375gm"
                if specform.cleaned_data['yeast'] == None or specform.cleaned_data['yeast'] == '':
                    specform.instance.yeast = "<100/gm"
                if specform.cleaned_data['mold'] == None or specform.cleaned_data['mold'] == '':
                    specform.instance.mold = "<100/gm"
                if specform.cleaned_data['coliforms'] == None or specform.cleaned_data['coliforms'] == '':
                    specform.instance.coliforms = "<100/gm"
                if specform.cleaned_data['listeria'] == None or specform.cleaned_data['listeria'] == '':
                    specform.instance.listeria = "Negative/25g"

            specform.instance.product_name = flavor.name
            specform.instance.product_number = flavor.number
            specform.instance.solubility = flavor.solubility
            specform.instance.specific_gravity = flavor.spg
            specform.instance.flash_point = flavor.flashpoint
            specform.instance.description = (flavor.color + " with the taste and aroma of " + flavor.organoleptics).capitalize()
            specform.instance.ingredient_statement = ingredient_statement
            if specform.cleaned_data['shelf_life'] == None or specform.cleaned_data['shelf_life'] == '':
                specform.instance.shelf_life = "9 months to 1 year if stored as recommended."
            if specform.cleaned_data['storage'] == None or specform.cleaned_data['storage'] == '':
                specform.instance.storage = "Store in full, tightly closed containers at a cool temperature."
            return specform
    #creating new
    else:
        flav_desc = ""
        if not (flavor.color == "" or flavor.organoleptics == "" or flavor.color == None or flavor.organoleptics == None):
                flav_desc = flavor.color + " with the taste and aroma of " + flavor.organoleptics
                flav_desc = flav_desc.capitalize()

        if flavor.phase == "Liquid":
            specform = spec_sheet_form(initial={'flavor':flavor, 'product_name':flavor.name, 'product_number': flavor.number, 'solubility':flavor.solubility,
                                                'specific_gravity':flavor.spg, 'flash_point': flavor.flashpoint, 'description': flav_desc,
                                                'ingredient_statement': ingredient_statement,
                                                'aerobic_plate_count':"<10,000/gm",
                                                'escherichia_coli':'<10/gm',
                                                'salmonella':'Negative/375gm',
                                                'yeast':'<100/gm',
                                                'mold':'<100/gm',
                                                'coliforms':'<100/gm',
                                                'listeria':'Negative/25g',
                                                'shelf_life':"9 months to 1 year if stored as recommended.",
                                                'storage':"Store in full, tightly closed containers at a cool temperature.",
                                                })

            specform.fields['solubility'].required = True
            specform.fields['specific_gravity'].required = True
            specform.fields['flash_point'].required = True
            return specform
        elif flavor.phase == "Powder":
            if flavor.product_category == "Flavorcoat":
                specform = spec_sheet_form(initial={'flavor':flavor, 'product_name':flavor.name, 'product_number': flavor.number, 'solubility':flavor.solubility,
                                                    # 'sieve':">98% thru A USS #10 Mesh", 'moisture':"<10.0% +/- 2%",
                                                    'escherichia_coli': "<10/g", 'salmonella':"Negative/375g",
                                                    'yeast':"200/g Maximum", 'mold':"200/g Maximum",
                                                    'description': flav_desc,
                                                    'ingredient_statement': ingredient_statement,
                                                    'shelf_life':"9 months to 1 year if stored as recommended.",
                                                    'storage':"Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight.",
                                                    })

                return specform
            else:
                specform = spec_sheet_form(initial={'flavor':flavor, 'product_name':flavor.name, 'product_number': flavor.number, 'solubility':flavor.solubility,
                                                    # 'sieve': ">98% thru A USS #80 Mesh", 'moisture':"5% Max",
                                                    'escherichia_coli': "<10/g", 'salmonella':"Negative/375g",
                                                    'yeast':"200/g Maximum", 'mold':"200/g Maximum",
                                                    'description': flav_desc,
                                                    'ingredient_statement': ingredient_statement,
                                                    'shelf_life':"9 months to 1 year if stored as recommended.",
                                                    'storage':"Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight.",
                                                    })

                specform.fields['solubility'].required = True
                # specform.fields['sieve'].required = True
                # specform.fields['moisture'].required = True
                return specform


def define_donttouch_readonly(flavor):
    dontTouchThese = []
    readOnly = []
    if flavor.phase == "Liquid":
        dontTouchThese.extend(('flavor', 'one_off_customer', 'specification_code', 'source_path','date', 'supercedes', 'sieve', 'moisture', 'fat_content', 'salt_content', 'brix', 'bostwick_consistometer',
                                'ph', 'water_activity', 'aerobic_plate_count', 'escherichia_coli', 'salmonella', 'yeast', 'mold', 'listeria','staphylococci','coliforms', 'standard_plate_count',
                                ))
        readOnly.extend(('product_name', 'product_number', 'solubility', 'specific_gravity', 'flash_point', 'description', 'ingredient_statement'))
        return dontTouchThese, readOnly

    elif flavor.phase == "Powder":
        if flavor.product_category == "Flavorcoat":
            dontTouchThese.extend(('flavor', 'one_off_customer', 'specification_code', 'source_path', 'date', 'supercedes', 'specific_gravity', 'flash_point','fat_content', 'salt_content', 'brix', 'bostwick_consistometer',
                                    'ph', 'water_activity', 'aerobic_plate_count', 'standard_plate_count', 'moisture', 'sieve'
                                    ))
            readOnly.extend(('product_name', 'product_number', 'solubility', #'sieve', 'moisture',
                            'specific_gravity', 'flash_point',
                            'escherichia_coli', 'salmonella', 'yeast', 'mold', 'description', 'ingredient_statement'))
            return dontTouchThese, readOnly
        else:
            dontTouchThese.extend(('flavor', 'one_off_customer', 'specification_code', 'source_path', 'date', 'supercedes', 'specific_gravity', 'flash_point','fat_content', 'salt_content', 'brix', 'bostwick_consistometer',
                                    'ph', 'water_activity', 'aerobic_plate_count', 'escherichia_coli', 'salmonella', 'yeast', 'mold','listeria','staphylococci','coliforms', 'standard_plate_count', 'moisture', 'sieve',
                                    ))
            readOnly.extend(('product_name', 'product_number', 'solubility', #'sieve', 'moisture',
                            'specific_gravity', 'flash_point',
                            'description', 'ingredient_statement'))
            return dontTouchThese, readOnly

def one_off_specs(request, flavor_number):
    dontTouchThese = []
    readOnly = []
    multipleOneoffs = ""
    customer = ""
    hyperlinked = request.GET.get('specSheet')
    search = flavorNumberForm()
    isDry = False
    standard = False
    micro = False
    createNew = False
    update = False
    initial = True
    dontTouchThese.extend(("flavor","source_path", "supercedes",'date',"product_name", "product_number", "ingredient_statement",))
    confirmationMessage = ""
    if request.method == 'POST':
        specform = spec_sheet_form(request.POST)
        specform_initial = spec_sheet_form(request.POST)

        if "update" in request.POST:
            ing = request.POST.get("ing", "")
            sp = SpecSheetInfo.objects.get(id=ing)
            # restate spec with an instance so it replaces an existing spec form instead of creating a new one
            specform = spec_sheet_form(request.POST, instance=sp)

            desc = IngredientStatement.objects.get(flavor = sp.flavor)
            special_fields = ['Specific gravitychk', 'Flash pointchk', 'Shelf lifechk', 'Storagechk', 'Solubilitychk', 'Descriptionchk']
            if specform.is_valid():
                # confirmationMessage+="hit first valid"
                update = True

                specform  = define_spec_params(specform, sp.flavor, True)

                #confirmationMessage = ""
                for field in specform:
                    # populate field with flash and spg from flavor
                    if field.name == 'flash_point':
                        setattr(specform.instance, field.name, sp.flavor.flashpoint)
                    if field.name == 'specific_gravity':
                        setattr(specform.instance, field.name, sp.flavor.spg)
                    if field.name == 'solubility':
                        setattr(specform.instance, field.name, sp.flavor.solubility)
                    if field.name == 'description':
                        setattr(specform.instance, field.name, (sp.flavor.color + " with the taste and aroma of " + sp.flavor.organoleptics).capitalize())
                    if field.name == 'shelf_life' and (field.value == "" or field.value == None):
                        setattr(specform.instance, 'shelf_life', "9 months to 1 year if stored as recommended.")
                    if field.name == 'storage' and (field.value == "" or field.value == None):
                        setattr(specform.instance, 'storage', "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight.")



                    label = field.label + "chk"
                    if not label in special_fields and label in request.POST and not getattr(specform.instance, field.name) == None:
                        setattr(specform.instance, field.name, "")
                    elif getattr(specform.instance, field.name) == None:
                        setattr(specform.instance, field.name, getattr(specform_initial.instance, field.name))


                # update the specform with the default values based on the phase as listed above ^
                specform.save()
                # new variable to get the newly saved spec form from the db
                spec = spec_sheet_form(instance=sp)
                if spec.is_valid():
                    spec.save()
                else:
                    confirmationMessage += str(spec.errors)


                # add other cases here
                confirmationMessage += "Updated SpecSheet"

                if sp.one_off_customer == '' or sp.one_off_customer == None:
                    standard = True
                else:
                    customer = sp.one_off_customer.companyname
                if standard:
                    dontTouchThese, readOnly = define_donttouch_readonly(sp.flavor)
                else:
                    # dontTouchThese.extend(('flavor',,'date' ,'supercedes', 'source_path',"product_name", "product_number", "ingredient_statement",))
                    spec.fields['one_off_customer'].required = True

                readOnly.extend(('one_off_customer', 'specific_gravity', 'flash_point', 'description', 'solubility',))

                fl = Flavor.objects.get(number = flavor_number)
                hyperlinked = request.GET.get('productSpecSheet', '')
                try:
                    ingredient_statement = IngredientStatement.objects.get(flavor = fl).ingredient_statement
                except:
                    ingredient_statement = None


                return HttpResponseRedirect('/access/product_spec_sheet/%s' % str(sp.flavor.number))

                #
                # spec = SpecSheetInfo.objects.filter(flavor = fl)
                # storage = "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight."
                # shelflife = "9 months to 1 year if stored as recommended."
                # warning = ""
                # multiple = ""
                # emptyFields= []
                # extrapowdermessage = "The above microbiological guidelines are based on average results for products of this type.  In accordance with our HACCP protocol, products will be micro-tested based on risk analysis."
                # # micro still to be determined
                # micro = fl.microsensitive
                # isPowder = False
                #



                # return render(
                #     request,
                #     'access/flavor/product_spec_sheet.html',
                #     {
                #         'warning':warning,
                #         'emptyFields':emptyFields,
                #         'isPowder':isPowder,
                #         'micro':micro,
                #         'storage':storage,
                #         'spec':spec,
                #         'ingredient_statement':ingredient_statement,
                #         'flavor':fl,
                #         'flavor':flavor_number,
                #         'ing':flavor__number,
                #         'extrapowdermessage':extrapowdermessage,
                #     },
                # )


                # return render(
                #             request,
                #             'access/flavor/one_off_specs.html',
                #             {
                #                 'flavor':sp.flavor,
                #                 'update':update,
                #                 'ing':ing,
                #                 'confirmation':confirmationMessage,
                #                 'dontTouchThese':dontTouchThese,
                #                 'readOnly':readOnly,
                #                 'form':search,
                #                 'specform':spec,
                #                 'customer':customer,
                #             },
                #     )


        elif "createNew" in request.POST and specform.is_valid(): # creating new, check if its a one off/standard
            warning = "reached create new"
            ing = request.POST.get("ing", "")
            fl = Flavor.objects.get(number = int(ing))
            specform = spec_sheet_form(request.POST)

            setattr(specform.instance, 'description', (fl.color + " with the taste and aroma of " + fl.organoleptics).capitalize())
            setattr(specform.instance, 'solubility', fl.solubility)
            setattr(specform.instance, 'flash_point', fl.flashpoint)
            setattr(specform.instance, 'specific_gravity', fl.spg)
            if getattr(specform.instance, 'shelf_life') == "" or getattr(specform.instance, 'shelf_life') == None:
                setattr(specform.instance, 'shelf_life', "9 months to 1 year if stored as recommended.")
            if getattr(specform.instance, 'storage') == "" or getattr(specform.instance, 'storage') == None:
                setattr(specform.instance, 'storage', "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight.")
            createNew = False
            update = True
            # specform = define_spec_params(specform, fl, False)

            ss = specform.save()
            if ss.shelf_life == "" or ss.shelf_life == None:
                ss.shelf_life = "9 months to 1 year if stored as recommended."
            if ss.storage == "" or ss.storage == None:
                ss.storage = "Store in full, tightly closed containers at a cool temperature. Avoid exposure to excessive heat and sunlight."

            ss.flash_point = fl.flashpoint
            ss.specific_gravity = fl.spg
            ss.description = (fl.color + " with the taste and aroma of " + fl.organoleptics).capitalize()
            ss.solubility = fl.solubility
            ss.save()
            specform = spec_sheet_form(instance = ss)
            ing = ss.id
            #ing = specform.id
            confirmationMessage = "Saved New SpecSheet"

            if specform.instance.one_off_customer == '' or specform.instance.one_off_customer == None:
                standard = True
            else:
                customer = specform.instance.one_off_customer.companyname
            if standard:
                dontTouchThese, readOnly = define_donttouch_readonly(fl)
                if fl.phase == "Liquid":
                    specform.fields['solubility'].required = True
                    specform.fields['specific_gravity'].required = True
                    specform.fields['flash_point'].required = True
                elif fl.phase == "Powder":
                    if not fl.product_category == "Flavorcoat":
                        specform.fields['solubility'].required = True
                        specform.fields['sieve'].required = True
                        specform.fields['moisture'].required = True


            readOnly.extend(('one_off_customer', 'specific_gravity', 'flash_point', 'description', 'solubility',))
                # specform.fields['one_off_customer'].required = True

            return HttpResponseRedirect('/access/product_spec_sheet/%s' % str(fl.number))
            # return render(
            #             request,
            #             'access/flavor/one_off_specs.html',
            #             {
            #                 "flavor": fl,
            #                 "update":update,
            #                 'createNew':createNew,
            #                 'warning':warning,
            #                 'ing':ing,
            #                 'confirmation':confirmationMessage,
            #                 'dontTouchThese':dontTouchThese,
            #                 'readOnly':readOnly,
            #                 'form':search,
            #                 'specform':specform,
            #                 'standard':standard,
            #                 'customer':customer,
            #             },
            #     )
        elif "createNew" in request.POST or "update" in request.POST and not specform.is_valid():
            update = True
            createNew = False
            ing = request.POST.get("ing", "")
            confirmation = "not valid" + str(specform.instance.one_off_customer) + " " + str(specform.errors)
            return render(
                        request,
                        'access/flavor/one_off_specs.html',
                        {
                            'createNew':createNew,
                            'ing':ing,
                            'update':update,
                            'confirmation':confirmation,
                            'specform':specform,
                            'form':search,
                        },
                )
    #come here to edit standards and one offs
    #edit dontTouchThese.extend to filterout fields that cant be changed
    if hyperlinked != None and hyperlinked != "":
        update = True
        customer = ""
        ing = int(hyperlinked)
        sp = SpecSheetInfo.objects.get(id = ing)
        specform = spec_sheet_form(instance = sp)
        fl = Flavor.objects.get(number = sp.flavor.number)
        micro = fl.microsensitive
        #check if it's a standard
        if sp.one_off_customer == '' or sp.one_off_customer == None:
            standard = True
        else:
            customer = sp.one_off_customer.companyname

        if standard:
            dontTouchThese, readOnly = define_donttouch_readonly(sp.flavor)

            if fl.phase == "Liquid":
                specform.fields['solubility'].required = True
                specform.fields['specific_gravity'].required = True
                specform.fields['flash_point'].required = True
            elif fl.phase == "Powder":
                if not fl.product_category == "Flavorcoat":
                    specform.fields['solubility'].required = True
                    specform.fields['sieve'].required = True
                    specform.fields['moisture'].required = True

        else:
            specform.fields['one_off_customer'].required = True

        dontTouchThese.extend(("source_path", "supercedes", ))
        readOnly.extend(('one_off_customer', 'specific_gravity', 'flash_point', 'description','solubility',))

        return render(
                    request,
                    'access/flavor/one_off_specs.html',
                    {
                        'flavor':fl,
                        'update':update,
                        'dontTouchThese':dontTouchThese,
                        'readOnly':readOnly,
                        'ing':ing,
                        'form':search,
                        # 'confirmation':sp,
                        'customer':customer,
                        'specform':specform,
                        'spec':sp,
                        'standard':standard,
                    },
            )

#initial get request from search
    if request.method == 'GET':
        ing = flavor_number
        req = []
        fl = Flavor.objects.get(number = int(ing))
        if "newStandard" in request.GET: #new standard
            standard = True
            # fl = Flavor.objects.get(number = int(ing))

            if fl.phase == "" or fl.phase == 'Undetermined' or fl.phase == None:
                confirmationMessage = "Phase for this flavor is still undetermined. Cannot proceed."
                search = flavorNumberForm()
                return render(
                            request,
                            'access/flavor/one_off_specs.html',
                            {
                                'ing':ing,
                                'form':search,
                                'missingFields':confirmationMessage,
                            },
                )
            try:
                ingredient_statement = IngredientStatement.objects.get(flavor = fl).ingredient_statement
            except:
                ingredient_statement = None
            spec = SpecSheetInfo.objects.filter(flavor = fl)
            specform = spec_sheet_form(initial={'flavor':fl})
            createNew = True

            dontTouchThese, readOnly = define_donttouch_readonly(fl)

            specform = define_spec_params(specform, fl, False)
            if fl.phase == "Liquid":
                req.extend(('name', 'number', 'solubility', 'spg', 'flashpoint', 'color', 'organoleptics', #ingredient statement....idk
                            ))

            elif fl.phase == "Powder":
                if fl.product_category == "Flavorcoat":
                    req.extend(('name', 'number', 'solubility', 'solubility', 'color', 'organoleptics', #ingredient statement....idk
                                ))
                else:
                    req.extend(('name', 'number', 'solubility', 'color', 'organoleptics', #ingredient statement....idk
                                ))

            n = ""
            for field in req:
                if getattr(fl, field)== None or getattr(fl, field) == "" or getattr(fl, field) == 0:
                    n += field + "<br> "
                    createNew = False

            if len(n) > 0:
                confirmationMessage = "Please contact ya boy, Matt Araneta, to resolve the following missing fields: <br> " + n

            return render(
                        request,
                        'access/flavor/one_off_specs.html',
                        {
                            'ing':ing,
                            'flavor':fl,
                            'dontTouchThese':dontTouchThese,
                            'readOnly':readOnly,
                            'form':search,
                            'standard':standard,
                            'spec':spec,
                            'specform':specform,
                            'createNew':createNew,
                            'missingFields':confirmationMessage,
                        },
            )
        elif "newOneOff" in request.GET: #new one off
            dontTouchThese.extend(('flavor',))
            # ing = request.GET.get("ing", "")
            # fl = Flavor.objects.get(number = int(ing))
            spec = SpecSheetInfo.objects.filter(flavor = fl)
            specform = spec_sheet_form(initial={'flavor':fl})
            specform.fields['one_off_customer'].required = True
            createNew = True
            return render(
                        request,
                        'access/flavor/one_off_specs.html',
                        {
                            'ing':ing,
                            'flavor':fl,
                            'dontTouchThese':dontTouchThese,
                            'form':search,
                            'spec':spec,
                            'specform':specform,
                            'createNew':createNew,
                        },
            )

    return render(
                request,
                'access/flavor/one_off_specs.html',
                {
                    # 'flavor':fl,
                    # 'update':update,
                    # 'dontTouchThese':dontTouchThese,
                    # 'readOnly':readOnly,
                    # 'ing':ing,
                    # 'form':search,
                    # # 'confirmation':sp,
                    # 'customer':customer,
                    # 'specform':specform,
                    # 'standard':standard,
                },
        )





def coa(request, lot_number):
    multipleLines = ''
    hyperlinked = False
    multiple = False
    micro = False


    # lot doesnt exist
    if not Lot.objects.filter(number = lot_number).exists():
        multipleLines += "Lot " + lot_number + " does not exist"
        multiple = True
        return render(
                    request,
                    'access/flavor/coa.html',
                    {

                        'multiple': multiple,
                        'multipleLines':multipleLines,


                    },
            )
    else:
        lot = Lot.objects.get(number = lot_number)

    line = LineItem.objects.filter(lot = lot)
    flavor = lot.flavor

    if not SpecSheetInfo.objects.filter(flavor = flavor).exists():
        multiple = True
        multipleLines = "No spec sheet exists for this flavor: " + str(flavor.number)
        return render(
                    request,
                    'access/flavor/coa.html',
                    {
                        'multiple':multiple,
                        'multipleOneoffs': multipleLines,
                    },
            )

    else:
        spec = SpecSheetInfo.objects.filter(flavor = flavor)


    if Retain.objects.filter(lot = lot).exists():
        retain = Retain.objects.get(lot = lot)
        if(retain.status != 'Passed' or retain.status != 'PassedLC' or retain == None):
            multiple = True
            multipleLines = "This lot has not passed QC. Unable to print."
            return render(
                        request,
                        'access/flavor/coa.html',
                        {
                            'multiple':multiple,
                            'multipleOneoffs': multipleLines,
                        },
                )

    ingredient_statement = IngredientStatement.objects.get(flavor = flavor).ingredient_statement
    expiration = lot.date + timedelta(days=365)
    coaform = coa_form()


    if flavor.microsensitive == True:
        micro = True


#saving posted data
    if request.method == "POST":
        updated_data = request.POST.copy()
        lot = updated_data.get('lot')
        line = updated_data.get('line')
        sp = updated_data.get('sp')
        lotitem = Lot.objects.get(id = lot)
        spec_line = LineItem.objects.get(id =line)

        if 'origin_lot' in request.POST:
            multipleLines += "origin lot in post <br>"
            origin_lot_entry = request.POST.get('origin_lot')
            if not origin_lot_entry == None and not origin_lot_entry == '' and Lot.objects.filter(number = int(origin_lot_entry)).exists():
                multipleLines += "origin lot not empty and exists <br>" + origin_lot_entry
                origin_lot = Lot.objects.get(number = int(origin_lot_entry))
                # updated_data = request.POST.copy()
                updated_data.update({'origin_lot':origin_lot.id, 'ingredient_statement': ' ', 'description': ' '})

                # coaform = coa_form(data=updated_data)

        if COA.objects.filter(lot=lot, line=line, sp=sp).exists():
            coa = COA.objects.get(lot=lot, line=line, sp=sp)
            coaform = coa_form(data=updated_data, instance=coa)
        else:
            coaform = coa_form(data=updated_data)



        # origin_lot_entry = request.POST.get('origin_lot', '')
        if request.POST.get("save") and coaform.is_valid():
                coaform.save()
                multipleLines += "saved COA "
                multiple = False

        else:
            multipleLines+= "didn't save"
            multiple = True

        # speclist = SpecSheetInfo.objects.filter(id= sp)
        spec = SpecSheetInfo.objects.filter(id = sp)
        # specfields = spec_sheet_form(data=model_to_dict(sp))
        speclist = spec.values_list()
        li = [None,None,None]
        for i in speclist:
            li += i
        updated_data.update({'origin_lot':origin_lot_entry})
        coaform = coa_form(data=updated_data)
        zipped = list(zip(coaform, li))


        return render(
                    request,
                    'access/flavor/coa.html',
                    {
                        'zipped':zipped,
                        'multipleLines':multipleLines,
                        # 'micro':micro,
                        'flavor':flavor,
                        'lot':lotitem,
                        'expiration':expiration,
                        'lineitem':spec_line,
                        # 'ingredient_statement':ingredient_statement,
                        'multiple': multiple,
                        # 'multipleLines':multipleLines,
                        'coaform':coaform,
                        # 'speclist':specfields,
                    },
            )



# returns list of multiple line items for one lot number
    if len(line) > 1 and request.GET.get('line') == None:
        multipleLines = "Multiple line items for dis lot: <br>"
        multiple = True
        for i in line:
            # multipleLines += "<li>"+ str(i) + "</li>"
            multipleLines += '<li><a href="../'+str(lot_number)+'/?line='+str(i.id)+'">'+ str(i) + '</a></li><br>'
        return render(
                    request,
                    'access/flavor/coa.html',
                    {
                        'multiple':multiple,
                        'multipleOneoffs': multipleLines,
                    },
            )

    elif len(line) == 0:
        multipleLines += "No sale order items exist for this lot."
        multiple = True
        return render(
                    request,
                    'access/flavor/coa.html',
                    {

                        'multiple': multiple,
                        'multipleLines':multipleLines,

                    },
            )

    else:
        # if link to specific line was clicked, run this
        if request.GET.get('line') != None:
            spec_line = LineItem.objects.get(id = str(request.GET.get('line')))
        else:
            line = line[0]
            spec_line = line
        multipleLines += str(spec_line.flavor) + ' ' + str(lot.flavor) + '<br>'
        if not spec_line.flavor == lot.flavor:
            multipleLines += 'LINE FLAVOR AND LOT FLAVOR MISMATCH: ' + str(spec_line.flavor) + ' ' + str(lot.flavor)
            return render(
                        request,
                        'access/flavor/coa.html',
                        {

                            'multiple': multiple,
                            'multipleLines':multipleLines,

                        },
                )

        customer = spec_line.salesordernumber.customer
        multiple = False
        sp = SpecSheetInfo.objects.filter(one_off_customer = customer, flavor = spec_line.flavor)



        multipleLines += 'specific line item <br>' + str(request.GET.get('line')) +" " + str(len(sp))

        #assume 1 oneoff for 1 flavor for 1 customer
        if len(sp) == 1:
            speclist = sp.values_list()
            sp = sp[0]

            multipleLines += '<li><a href="../../one_off_specs/?specSheet='+str(sp.id)+'">'+"One Off"+'</a></li>'
        else:
            sp = SpecSheetInfo.objects.filter(flavor = spec_line.flavor, one_off_customer= None)
            speclist = sp.values_list()

            sp = SpecSheetInfo.objects.get(flavor = spec_line.flavor, one_off_customer= None)

        li = [None,None,None]
        for i in speclist:
            li += i

        # check if COA exists for this flavor and line
        ol_number = ''
        if COA.objects.filter(sp = sp, line = spec_line, lot=lot).exists():
            multipleLines+= "COA exists for this lot and line item"
            coa = COA.objects.get(sp = sp, line = spec_line, lot=lot)
            if coa.origin_lot != '' and coa.origin_lot != None:
                coaform = coa_form(instance=coa, initial={'origin_lot':coa.origin_lot.number})
            else:
                coaform = coa_form(instance=coa)
            specform = spec_sheet_form(instance=coa.sp)
            zipped = list(zip(coaform, li))

            return render(
                        request,
                        'access/flavor/coa.html',
                        {
                            'zipped':zipped,
                            'micro':micro,
                            'flavor':flavor,
                            'lot':lot,
                            'expiration':expiration,
                            'lineitem':spec_line,
                            'spec':coa.sp,
                            'ingredient_statement':ingredient_statement,
                            'multiple': multiple,
                            'multipleLines':multipleLines,
                            'coaform':coaform,
                            'coa':coa,
                            'speclist':speclist,
                        },
                )
        else:
            multipleLines+='coa doesnt exist for this'
            coaform = coa_form(initial={'flavor':sp.flavor, 'one_off_customer':customer, 'line':spec_line, 'lot':lot, 'sp':sp, 'date': date.today(),})
            zipped = list(zip(coaform, li))
            return render(
                        request,
                        'access/flavor/coa.html',
                        {
                            'zipped':zipped,
                            'micro':micro,
                            'flavor':flavor,
                            'lot':lot,
                            'expiration':expiration,
                            'lineitem':spec_line,
                            'spec':sp,
                            'ingredient_statement':ingredient_statement,
                            'multiple': multiple,
                            'multipleLines':multipleLines,
                            'coaform':coaform,
                            'speclist':speclist,
                        },
                )

def query_list(request):

    invalid_rm_nutri_total_list = [x for x in NutriInfo.objects.exclude(ingredient__discontinued=True).exclude(ingredient__supplier__suppliercode='FDI') if x.invalid_total]

    todays_date = date.today()
    one_year_ago = todays_date - relativedelta(years=1)
    three_years_ago = todays_date - relativedelta(years=3)

    #Nutri field checked but no NutriInfo object
    nutri_field_checked_but_no_nutri_info = Ingredient.objects.filter(nutri=True, nutriinfo=None).exclude(suppliercode='FDI')

    #All suppliers bought from Jan 1, 2017
    supplier_set = set()
    for po in PurchaseOrder.objects.filter(date_ordered__year__gte=2019):
        supplier_set.add(po.supplier)


    #Any query that has to search through RM documentation will go below
    natural_on_file_without_natural_doc = []
    raw_materials_with_no_sds_on_file = []
    docs_contain_alldocs_or_paperwork_keywords = []

    for ing in Ingredient.objects.filter(date_ordered__gte=three_years_ago, discontinued=False).exclude(suppliercode='FDI'):
        documentation_path = '/var/www/static_root/Documentation/%s/' % ing.id

        try:
            top_level_filenames = os.walk(documentation_path).next()[2]

            if ing.art_nati == 'Nat' and ing.natural_document_on_file and \
                            True not in ('nat' in filename.lower() for filename in top_level_filenames):
                natural_on_file_without_natural_doc.append(ing)

            if True not in ('sds' in filename.lower() for filename in top_level_filenames):
                raw_materials_with_no_sds_on_file.append(ing)

            for filename in top_level_filenames:
                if any(keyword in filename.lower() for keyword in ['paperwork', 'all docs', 'alldocs']):
                    docs_contain_alldocs_or_paperwork_keywords.append(ing)

        except: #directory does not exists or is not in the right location
            if ing.art_nati == 'Nat' and ing.natural_document_on_file:
                natural_on_file_without_natural_doc.append(ing)

            raw_materials_with_no_sds_on_file.append(ing)

    #All ingredients with missing gmo data
    rms_with_missing_gmo_data = Ingredient.objects.filter(date_ordered__gte=three_years_ago, discontinued=False, new_gmo='').exclude(suppliercode='FDI')

    #All products with undetermiend phase
    flavors_with_undetermined_phase = Flavor.objects.filter(sold=True, phase='Undetermined')

    #Microsensitive raw materials
    microsensitive_rms = Ingredient.objects.filter(microsensitive='True', discontinued=False).exclude(suppliercode='FDI')

    #Approved experimentals with duplication info
    approved_experimentals_with_duplication_info = \
        ExperimentalLog.objects.filter(flavor__approved=True)\
            .filter(Q(duplication=True)|~Q(duplication_name__in=[None,''])|~Q(duplication_company__in=[None,''])|~Q(duplication_id__in=[None,''])).order_by('duplication_name')

    three_years_ago = date.today() - relativedelta(years=3)
    one_year_ago = date.today() - relativedelta(years=1)

    pm_under_3 = Flavor.objects.filter(sold=True).exclude(rawmaterialcost=0).annotate(pm=F('unitprice')/F('rawmaterialcost')).filter(pm__lt=3).order_by('-pm')

    top_selling_products_with_pm_under_3_5 = []
    for fl in Flavor.objects.filter(sold=True).exclude(rawmaterialcost=0).annotate(pm=F('unitprice')/F('rawmaterialcost')).filter(pm__lt=3.5).order_by('-pm'):
        num_lots = Lot.objects.filter(flavor=fl,date__gte=one_year_ago).count()
        if num_lots > 0:
            total_lot_weight = Lot.objects.filter(flavor=fl,date__gte=one_year_ago).aggregate(Sum('amount'))['amount__sum']
            if total_lot_weight > 1000:
                top_selling_products_with_pm_under_3_5.append([fl, num_lots, total_lot_weight, total_lot_weight/num_lots, fl.pm])

    lowest_selling_products_with_pm_under_4 = []
    for fl in Flavor.objects.filter(sold=True).exclude(rawmaterialcost=0).annotate(pm=F('unitprice')/F('rawmaterialcost')).filter(pm__lt=4).order_by('-pm'):
        num_lots = Lot.objects.filter(flavor=fl,date__gte=one_year_ago).count()
        if num_lots > 0:
            total_lot_weight = Lot.objects.filter(flavor=fl,date__gte=one_year_ago).aggregate(Sum('amount'))['amount__sum']
            if total_lot_weight < 50:
                lowest_selling_products_with_pm_under_4.append([fl, num_lots, total_lot_weight, total_lot_weight/num_lots, fl.pm])

    # The following code will work for future django versions (2.0.0+)
    # top_selling_products_with_pm_under_3_5 = Flavor.objects.filter(sold=True).exclude(rawmaterialcost=0)\
    #     .annotate(average_lot_weight=Avg('lot__amount',filter=Q(lot__date__gte=one_year_ago)))\
    #     .annotate(total_lot_weight=Sum('lot__amount',filter=Q(lot__date__gte=one_year_ago)))\
    #     .annotate(pm=F('unitprice')/F('rawmaterialcost')).filter(pm__lt=3.5)\
    #     .annotate(lot_count=Count('lot',filter=Q(lot__date__gte=one_year_ago)))\
    #     .filter(total_lot_weight__gt=1000).order_by('-pm')
    #
    # lowest_selling_products_with_pm_under_4 = Flavor.objects.filter(sold=True).exclude(rawmaterialcost=0)\
    #     .annotate(average_lot_weight=Avg('lot__amount',filter=Q(lot__date__gte=one_year_ago)))\
    #     .annotate(total_lot_weight=Sum('lot__amount',filter=Q(lot__date__gte=one_year_ago)))\
    #     .annotate(pm=F('unitprice')/F('rawmaterialcost')).filter(pm__lt=4)\
    #     .annotate(lot_count=Count('lot',filter=Q(lot__date__gte=one_year_ago)))\
    #     .filter(total_lot_weight__lt=50).order_by('-pm')

    query_dict = OrderedDict()
    query_dict['invalid_rm_nutri_total'] = {
            'proper_name': "Invalid Nutri Totals",
            'headers': ['Raw Material', 'Nutri Total', 'Edit Nutri'],
            'items': [[x.ingredient, x.total, '<a href="/access/rm_nutri_edit?rm=%s" target="_blank">Edit Nutri</a>' % x.ingredient.id] for x in invalid_rm_nutri_total_list],
            'url': '/access/query_list?category=invalid_rm_nutri_total',
        }
    query_dict['outdated_raw_materials'] = {
            'proper_name': "Outdated Raw Materials",
            'headers': [],
            'items': Ingredient.objects.filter(sub_flavor=None,discontinued=False,purchase_price_update__lt=one_year_ago).exclude(supplier=None).exclude(suppliercode='FDI'),
            'url': '/access/outdated_raw_materials',
        }
    query_dict['natural_on_file_without_natural_doc'] = {
            'proper_name': "RMs bought in the last 3 years with Natural on File checked but no NATURAL documentation",
            'headers': ['Ingredient'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()),] for x in natural_on_file_without_natural_doc],
            'url': '/access/query_list?category=natural_on_file_without_natural_doc'
        }
    query_dict['nutri_field_checked_but_no_nutri_info'] = {
            'proper_name': "RMs with Nutri field checked but no nutri info",
            'headers': ['Ingredient', 'Add Nutri Info'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), '<a href="/access/rm_nutri_edit/?rm=%s" target="_blank">Add Nutri Info</a>' % x.id] for x in nutri_field_checked_but_no_nutri_info],
            'url': '/access/query_list?category=nutri_field_checked_but_no_nutri_info'
        }
    query_dict['raw_materials_with_no_sds_on_file'] = {
            'proper_name': "RMs bought in the last 3 years with no SDS on file",
            'headers': ['Ingredient'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), ] for x in raw_materials_with_no_sds_on_file],
            'url': '/access/query_list?category=raw_materials_with_no_sds_on_file'
        }
    query_dict['docs_contain_alldocs_or_paperwork_keywords'] = {
            'proper_name': "RMs with 'All Docs' or 'Paperwork' in documentation names",
            'headers': ['Ingredient'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), ] for x in docs_contain_alldocs_or_paperwork_keywords],
            'url': '/access/query_list?category=docs_contain_alldocs_or_paperwork_keywords'
        }
    query_dict['suppliers_since_2019'] = {
            'proper_name': "All suppliers bought from since January 1, 2019",
            'headers': ['Supplier'],
            'items': sorted([['%s' % x, PurchaseOrder.objects.filter(supplier=x,date_ordered__year__gte=2019).count()] for x in supplier_set],key=lambda x: -x[1]),
            'url': '/access/query_list?category=suppliers_since_2019'
        }
    query_dict['rms_with_missing_gmo_data'] = {
            'proper_name': "RMs with missing GMO data",
            'headers': ['Ingredient'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), ] for x in rms_with_missing_gmo_data],
            'url': '/access/query_list?category=rms_with_missing_gmo_data'
        }
    query_dict['flavors_with_undetermined_phase'] = {
            'proper_name': "Sold flavors with undetermined Phase",
            'headers': ['Flavor'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), ] for x in flavors_with_undetermined_phase],
            'url': '/access/query_list?category=flavors_with_undetermined_phase'
        }
    query_dict['microsensitive_rms'] = {
            'proper_name': "Microsensitive Raw Materials",
            'headers': ['Raw Material'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), ] for x in microsensitive_rms],
            'url': '/access/query_list?category=microsensitive_rms'
        }
    query_dict['experimentals_with_approved_products_and_duplication_info'] = {

            'proper_name': "Experimentals with Approved Products and Duplication Info",
            'headers': ['Experimental','Approved Product','Duplication','Dup. Name', 'Dup. Company', 'Dup. ID'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.get_absolute_url(), x.__str__()),
                                    '<a href="%s" target="_blank">%s</a>' % (x.flavor.url, x.flavor.__str__()),
                                    x.duplication, x.duplication_name, x.duplication_company, x.duplication_id] for x in approved_experimentals_with_duplication_info],
            'url': '/access/query_list?category=experimentals_with_approved_products_and_duplication_info'
        }
    query_dict['pm_under_3'] = {
            'proper_name': "Products with Profit Margin under 3.0",
            'headers': ['Raw Material','Profit Margin'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x.url, x.__str__()), round(x.unitprice/x.rawmaterialcost, 3)] for x in pm_under_3],
            'url': '/access/query_list?category=pm_under_3'
        }
    query_dict['top_selling_products_with_pm_under_3_5'] = {
            'proper_name': "Top Selling Products with Profit Margin under 3.5",
            'headers': ['Flavor','# of Lots in Last Year', 'Total Amount in Last Year (lbs)', 'Avg. Lot Size in Last Year (lbs)','Profit Margin'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x[0].url, x[0].__str__()), x[1], round(x[2], 3), round(x[3], 3), round(x[4], 3)] for x in top_selling_products_with_pm_under_3_5],
            'url': '/access/query_list?category=top_selling_products_with_pm_under_3_5'
        }
    query_dict['lowest_selling_products_with_pm_under_4'] = {
            'proper_name': "Lowest Selling Products with Profit Margin under 4.0",
            'headers': ['Flavor','# of Lots in Last Year', 'Total Amount in Last Year (lbs)', 'Avg. Lot Size in Last Year (lbs)','Profit Margin'],
            'items': [['<a href="%s" target="_blank">%s</a>' % (x[0].url, x[0].__str__()), x[1], round(x[2], 3), round(x[3], 3), round(x[4], 3)] for x in lowest_selling_products_with_pm_under_4],
            'url': '/access/query_list?category=lowest_selling_products_with_pm_under_4'
        }

    #if there's a category in the url, render the detail page for that category
    category = request.GET.get('category', None)
    if category:

        category_dict = query_dict[category]

        return render(
            request,
            'access/query_list/query_detail.html',
            {
                'page_title': category_dict['proper_name'],
                'headers': category_dict['headers'],
                'items': category_dict['items'],
            }
        )

    #create category rows from query_dict
    query_dict_category_rows = [[x['proper_name'], x['items'], x['url']] for x in list(query_dict.values())]

    return render(
        request,
        'access/query_list/query_list.html',
        {
            'page_title': "Query List",
            'rows': query_dict_category_rows,
        }
    )

def shipping_suggestions(request):
    search = searchForm()

    if request.method == "POST":
        form = searchForm(request.POST)
        if form.is_valid():
            number = int(form.cleaned_data['rm_search'])
            fl = Flavor.objects.get(number = number)

            return render(
                request,
                'access/flavor/shipping_suggestions.html',
                {
                    'search':search,
                    'flavor':fl,

                }
            )

    return render(
        request,
        'access/flavor/shipping_suggestions.html',
        {
            'search':search,
        }
    )


def renumber(request, flavor_number):

    original = Flavor.objects.get(number = flavor_number)
    customers = Customer.objects.all()
    # way to get the next renumber number

    if not len(original.gazinta.all()) > 0:
        return render(
            request,
            'access/flavor/renumber.html',
            {
                'flavor':"Gazinta must be created for this flavor before it can be renumbered.",
            }
        )

    elif request.method == "POST":
        # make new formula
        fl = copy.deepcopy(original)
        memo = "<br> This is a renumber of <a href='../access/"+flavor_number+"'>"+flavor_number+"</a>"
        fl.id = get_next_flavorid()
        fl.number = temp = get_next_renumber()
        fl.save()
        fl.unitprice = Decimal(request.POST['unitprice'])
        customer = None
        if 'customer' in request.POST and request.POST['customer'] != None and request.POST['customer'] != "":
            fl.productmemo += "<br> Customer: "+ request.POST['customer']
            customer = request.POST['customer']


        fl.productmemo += memo
        fl.save()
        fl = Flavor.objects.get(number = temp)

        ing_stmt = IngredientStatement.objects.get(flavor = original)
        is_cpy = copy.deepcopy(ing_stmt)
        is_cpy.id = None
        is_cpy.flavor = fl
        is_cpy.save()

        # temp solution until i can deep copy m2m relation
        renumber_formula = Formula(
            flavor = fl,
            ingredient = original.gazinta.all()[0],
            amount = 1000
        )
        renumber_formula.save()
        recalculate_guts(fl)
        fl.save()

        if not customer == None:
            r = Renumber(a=original, b=fl, customer=Customer.objects.get(companyname=customer))
        else:
            r = Renumber(a=original, b=fl)
        r.save()

        return render(
            request,
            'access/flavor/renumber.html',
            {
                'unitprice':fl.unitprice,
                # 'exclusive_customer':cpy,
                'original':flavor_number,
                'new':fl.number,
                'flavor':fl,
                'customers':customers,
                'admin':True,
            }
        )

    return render(
        request,
        'access/flavor/renumber.html',
        {
            'customers':customers,
            'admin':True,
        }
    )


supplier_specific = ['COI', 'form40', 'form20', 'form20ar', 'form20c']

doctypes = [
                'specsheet',
                'sds',
                'allergen',
                'nutri',
                'GMO',
                'GPVC',
                'LOG',
                'natural',
                'origin',
                'vegan',
                'organic',
                'kosher',
                'halal',
                'COA',
                'COI',
                'form20',
                'form20ar',
                'form20c',
                'form40',
            ]
def latest_docs(rm):
        latest = {}

        doctypes = [
                        'specsheet',
                        'sds',
                        'allergen',
                        'nutri',
                        'GMO',
                        'GPVC',
                        'LOG',
                        'natural',
                        'origin',
                        'vegan',
                        'organic',
                        'organic_cert',
                        'kosher',
                        'halal',
                        # 'COA', special case here
                        'COI',
                        'form20',
                        'form20ar',
                        'form20c',
                        'form40',
                        'ingbreak',
                    ]


        # CHECK NATURAL STATUS HERE
        #
        if not rm.art_nati == 'Nat' and not rm.art_nati == 'NFI-N':
            doctypes.remove('organic')
            # doctypes.remove('vegan')
            doctypes.remove('natural')

        # else:
        #     if not rm.vegan:
        #         doctypes.remove('vegan')
        #     if not rm.organic_compliant:
        #         doctypes.remove('organic')

        # check if qualifed for GPVC
        if not rm.new_gmo == 'GMO Free':
            doctypes.remove('GPVC')

        for i in doctypes:
            # fill list with latest verified documents
            doctype_label = [y for x, y in DOC_TYPES if x == i][0]
            latest[i] = [None, doctype_label]
            docs = Documents.objects.filter(rawmaterial = rm, doctype = i)
            #

            # searches for latest document across all documents if supplier specific
            if i in supplier_specific and Documents.objects.filter(rawmaterial__supplier = rm.supplier, doctype = i).exists():
                latest[i] = [Documents.objects.filter(rawmaterial__supplier= rm.supplier, doctype = i).order_by('-expiration')[0], doctype_label]

            if i == 'LOG':
                product_specific_query = Documents.objects.filter(doctype=i, log_rms__contains=[str(rm.rawmaterialcode)]).order_by('-expiration')
                supplier_specific_query = Documents.objects.filter(rawmaterial__supplier = rm.supplier, doctype = i, log_rms=[]).order_by('-expiration')

                # compare both docs if both queries exists
                if product_specific_query.exists() and supplier_specific_query.exists():
                    if product_specific_query[0].expiration < supplier_specific_query[0].expiration:
                        latest[i] = [supplier_specific_query[0], doctype_label]
                    else:
                        latest[i] = [product_specific_query[0], doctype_label]

                elif product_specific_query.exists():
                    latest[i] = [product_specific_query[0], doctype_label]
                elif supplier_specific_query.exists():
                    latest[i] = [supplier_specific_query[0], doctype_label]


            elif docs.exists():
                latest[i] = [docs.order_by('-expiration')[0], doctype_label]

            else:
                d = [obj for obj in docs if obj.verified == False]
                for x in d:
                    count = DocumentVerification.objects.filter(document = x)
                    if count.count() >= 2:
                        latest[i] = [x, doctype_label]
                    elif count.count() <= 1:
                        latest[i] = [x, doctype_label]

            # doctype_label = [y for x, y in Documents.DOC_TYPES if x == dt][0]
            # doctype_label

        return collections.OrderedDict(latest)


def autoverify(request, doc):
    if IngredientTemp.objects.filter(user_id = request.user.id).filter(temp_rmcode = doc.rawmaterial.rawmaterialcode).exists():
        temp = IngredientTemp.objects.get(user_id = request.user.id, temp_rmcode = doc.rawmaterial.rawmaterialcode)
    else:
        temp = IngredientTemp.objects.create(user = request.user, temp_rmcode = doc.rawmaterial.rawmaterialcode)
        temp.save()

    if NutriInfoTemp.objects.filter(user = request.user).filter(ingredient = doc.rawmaterial).exists():
        ntemp = NutriInfoTemp.objects.get(user = request.user, ingredient = doc.rawmaterial)
    else:
        ntemp = NutriInfoTemp.objects.create(user = request.user, ingredient = doc.rawmaterial)
        ntemp.save()
    docv = DocumentVerification(document = doc, verifier=request.user, temp_ingredient = temp, temp_nutri=ntemp, final = True)
    docv.save()


def convert_to_pdf(word_doc):
    convert_string = 'libreoffice --headless --convert-to pdf ' + word_doc + ' --outdir ' + os.path.dirname(word_doc)
    # creates pdf version of doc
    os.system(convert_string)
    os.remove(word_doc)
    return os.path.splitext(word_doc)[0] +'.pdf'

def document_control(request, pin_number, rm_code, doctype):
    message = ""
    pagetitle = "Document Control"

    if rm_code == -1:
        i = Ingredient.objects.filter(id = pin_number, discontinued = False)
        return render(
            request,
            'access/ingredient/document_control.html',
            {
                'ingredients':i,
                'product':i[0].product_name,
            }
        )

    elif doctype == None:
        # list document objects for RM
        rm = Ingredient.objects.get(rawmaterialcode=rm_code)
        missing_doc = '/access/document_control/'+str(rm.id)+'/'+str(rm.rawmaterialcode)
        d = Documents.objects.filter(rawmaterial = rm).order_by('doctype')
        latest = latest_docs(rm)
        d = [obj for obj in Documents.objects.filter(rawmaterial = rm).order_by('documententry') if obj.verified == False]
        docpending = {}

        for x in d:
            count = DocumentVerification.objects.filter(document = x)
            if count.count() >= 2 and not x.verified and request.user.is_superuser:
                docpending[x] = "Review Required. Verified by "+str(count[0].verifier.username) + " and " + str(count[1].verifier.username)
            elif count.count() == 1:
                docpending[x] = "1 verification. Verified by "+str(count[0].verifier.username)
            else:
                docpending[x] = None

        admin = False

        if request.user.is_superuser:
            admin = True

        coa = Documents.objects.filter(rawmaterial = rm, doctype='COA').order_by('-expiration')
        return render(
            request,
            'access/ingredient/document_control.html',
            {
                'rm':rm,
                'missing_doc':missing_doc,
                'documents':docpending,
                'coa':coa,
                'latest':latest,
                'page_title':pagetitle,
                'admin':admin,
                # 'ss':supplier_specific,
            }
        )

    else:
        # Handle uploads and post
        # form40
        auto = ['GPVC','COI', 'form40', 'form20', 'form20ar', 'form20c', 'ingbreak']
        rm = Ingredient.objects.get(rawmaterialcode = rm_code)
        link = ""
        applicabletypes = [
                        'specsheet',
                        'sds',
                        'allergen',
                        'nutri',
                        'GMO',
                        'GPVC',
                        'LOG',
                        'natural',
                        'origin',
                        'vegan',
                        'organic',
                        'organic_cert',
                        'kosher',
                        'halal',
                        'COA',
                        'COI',
                        'form20',
                        'form20ar',
                        'form20c',
                        'form40',
                        'ingbreak',
                    ]

        if not rm.art_nati == 'Nat' and not rm.art_nati == 'NFI-N':
            applicabletypes.remove('organic')
            # applicabletypes.remove('vegan')
            applicabletypes.remove('natural')
        # else:
        #     if not rm.vegan:
        #         applicabletypes.remove('vegan')
        #     if not rm.organic_compliant:
        #         applicabletypes.remove('organic')

        if not rm.new_gmo == 'GMO Free':
            applicabletypes.remove('GPVC')

        # RENDER UPLOAD CONFIRMATION PAGE
        # Delete after user rejects confirmation
        #
        if 'next' in request.GET and not 'yes' in request.POST:
            list_docs = request.GET.get('next').split(".")
            if list_docs[0] in request.POST and Documents.objects.filter(id = int(list_docs[0])).exists():
                for i in list_docs:
                    delete = Documents.objects.get(id = int(i))
                    DocumentVerification.objects.filter(document=delete).delete()
                    os.remove(delete.uploadfile.path)
                    delete.delete()

            if Documents.objects.filter(id = int(list_docs[0])).exists():
                d = Documents.objects.get(id = int(list_docs[0]))
                if not list_docs[0] in request.POST:
                    return render(
                        request,
                        'access/ingredient/document_control.html',
                        {
                            'uploadmessage':"Is this the correct document to upload?",
                            'doctype':doctype,
                            'rm':rm,
                            'link':link,
                            # 'previous':d.id,
                            'confirmdocupload':d,
                            'page_title':pagetitle,
                        }
                    )



        if request.method == 'POST':
            # USER IS UPLOADING DOCUMENT
            if 'confirm' in request.POST:
                getlink = ""
                savedocs = []
                link = "/access/document_control/"+str(pin_number)+"/"+str(rm_code)+"/"
                d = Documents(rawmaterial=rm,doctype=doctype,uploadfile=request.FILES[doctype], uploader = request.user)
                savedocs.append(d)

                # append other applicable documents to list
                # CHECK IF OTHER APPLICABLE DOCS HAVE DUPLICATES
                for n in doctypes:
                    if request.POST.get(n):
                        temp = Documents(rawmaterial=rm,doctype=n,uploadfile=request.FILES[doctype], uploader = request.user)
                        savedocs.append(temp)


                # Save and create the getlink
                # else:
                for s in savedocs:
                    s.save()
                    # if not os.path.splitext(s.uploadfile.path)[1] == "pdf":
                    #     new_path_to_pdf = convert_to_pdf(s.uploadfile.path)
                    #     f = File(file(new_path_to_pdf))
                    #     f.name = os.path.basename(new_path_to_pdf)
                    #     setattr(s, 'uploadfile', f)
                    #     s.save()
                    #     f.close()
                    #     # hacky way to remove the duplicate :
                    #     os.remove(os.path.splitext(new_path_to_pdf)[0] + '.pdf')
                    #     # f.name = os.path.basename(new_path_to_pdf)
                    #     # s.uploadfile = f

                    getlink += str(s.id)+"."
                    # if s.doctype in auto: #or (n == 'COA' and rm.microsensitive == 'False'):
                    #     autoverify(request, s)

                getlink = getlink.rstrip(".")
                return HttpResponseRedirect('/access/document_control/%s/%s/%s/?next=%s' % (str(pin_number), str(rm_code), doctype, getlink))

            # REDIRECT TO DOCUMENT CONTROL
            elif 'yes' in request.POST:

                dt = datetime.strptime(request.POST['expiration'], '%Y-%m-%d')
                year = timedelta(days = 365)
                expiration = date.today()

                oneyear = ['LOG', 'COI', 'form40', 'kosher', 'halal', 'specsheet', 'sds', 'form20', 'GPVC', 'organic_cert', 'form20ar', 'organic', 'form20c']
                # expiration_date = ['form20c', 'kosher', 'halal']
                threeyears = ['origin', 'GMO', 'vegan', 'allergen', 'nutri', 'natural', 'ingbreak']


                if doctype == 'nutri':
                    expiration = dt.date() + year*5
                elif doctype in oneyear:
                    expiration = dt.date() + year
                else:
                    expiration = dt.date() + year*3

                duplicatelist = ""
                duplicate = "<div class='rednotification'><h2>Upload failed. The following document types have an exisiting document with the same expiration date ("+str(expiration)+").<h2><ul>"
                # redirect to doc control

                list_docs = request.GET.get('next').split(".")

                for i in list_docs:
                    temp = Documents.objects.get(id=int(i))
                    if Documents.objects.filter(expiration=expiration, rawmaterial=rm, doctype=temp.doctype).exists():
                        duplicatelist+= "<li><span name='doctype'>"+ temp.doctype +"</span> - <a href='"+Documents.objects.filter(rawmaterial=rm, expiration=expiration, doctype=temp.doctype)[0].uploadfile.url+"' target='_blank'>View Existing Document</a></li>"

                if duplicatelist and not doctype == 'COA':
                    for i in list_docs:
                        Documents.objects.get(id=int(i)).delete()
                    duplicatelist += "</ul>"
                    duplicate += duplicatelist
                    duplicate += "</div>"
                    messages.info(request, duplicate)
                    return HttpResponseRedirect('/access/document_control/%s/%s' % (str(rm.id), str(rm.rawmaterialcode)))



                for i in list_docs:
                    s = Documents.objects.get(id = int(i))
                    setattr(s, 'expiration', expiration)
                    s.save()

                success = "<div class = 'greennotification'> <h2>Successfully uploaded document </h2><br></div><br>"
                messages.info(request, success)
                return HttpResponseRedirect('/access/document_control/%s/%s' % (str(pin_number), str(rm_code)))



            return render(
                request,
                'access/ingredient/document_control.html',
                {
                    'message':message,
                    'doctype':doctype,
                    'doctypes':applicabletypes,
                    'rm':rm,
                    'link':link,
                    # 'previous':d.id,
                    'page_title':pagetitle,
                }
            )

        if doctype in applicabletypes:
            return render(
                request,
                'access/ingredient/document_control.html',
                {
                    'message':message,
                    'doctype':doctype,
                    'rm':rm,
                    'link':link,
                    'doctypes':applicabletypes,
                    # 'previous':d.id,
                    'page_title':pagetitle,
                }
            )


    return render(
        request,
        'access/ingredient/document_control.html',
        {
            'message':doctype
        }
    )


def countries():
    value = [
        ('US', 'United States'),('AF', 'Afghanistan'),('AL', 'Albania'),('DZ', 'Algeria'),
        ('AS', 'American Samoa'),('AD', 'Andorra'),('AO', 'Angola'),('AI', 'Anguilla'),('AQ', 'Antarctica'),('AG', 'Antigua And Barbuda'),
        ('AR', 'Argentina'),('AM', 'Armenia'),('AW', 'Aruba'),('AU', 'Australia'),('AT', 'Austria'),('AZ', 'Azerbaijan'),
        ('BS', 'Bahamas'),('BH', 'Bahrain'),('BD', 'Bangladesh'),('BB', 'Barbados'),('BY', 'Belarus'),('BE', 'Belgium'),('BZ', 'Belize'),('BJ', 'Benin'),('BM', 'Bermuda'),
        ('BT', 'Bhutan'),('BO', 'Bolivia'),('BA', 'Bosnia And Herzegowina'),('BW', 'Botswana'),('BV', 'Bouvet Island'),('BR', 'Brazil'),('BN', 'Brunei Darussalam'),
        ('BG', 'Bulgaria'),('BF', 'Burkina Faso'),('BI', 'Burundi'),
        ('KH', 'Cambodia'),('CM', 'Cameroon'),('CA', 'Canada'),('CV', 'Cape Verde'),('KY', 'Cayman Islands'),('CF', 'Central African Rep'),('TD', 'Chad'),('CL', 'Chile'),
        ('CN', 'China'),('CX', 'Christmas Island'),('CC', 'Cocos Islands'),('CO', 'Colombia'),('KM', 'Comoros'),('CG', 'Congo'),('CK', 'Cook Islands'),('CR', 'Costa Rica'),
        ('CI', 'Cote D`ivoire'),('HR', 'Croatia'),('CU', 'Cuba'),('CY', 'Cyprus'),('CZ', 'Czech Republic'),
        ('DK', 'Denmark'),('DJ', 'Djibouti'),('DM', 'Dominica'),('DO', 'Dominican Republic'),
        ('TP', 'East Timor'),('EC', 'Ecuador'),('EG', 'Egypt'),('SV', 'El Salvador'),('GQ', 'Equatorial Guinea'),('ER', 'Eritrea'),('EE', 'Estonia'),('ET', 'Ethiopia'),
        ('FK', 'Falkland Islands (Malvinas)'),('FO', 'Faroe Islands'),('FJ', 'Fiji'),('FI', 'Finland'),('FR', 'France'),('GF', 'French Guiana'),('PF', 'French Polynesia'),
        ('TF', 'French S. Territories'),
        ('GA', 'Gabon'),('GM', 'Gambia'),('GE', 'Georgia'),('DE', 'Germany'),('GH', 'Ghana'),('GI', 'Gibraltar'),('GR', 'Greece'),('GL', 'Greenland'),('GD', 'Grenada'),
        ('GP', 'Guadeloupe'),('GU', 'Guam'),('GT', 'Guatemala'),('GN', 'Guinea'),('GW', 'Guinea-bissau'),('GY', 'Guyana'),
        ('HT', 'Haiti'),('HN', 'Honduras'),('HK', 'Hong Kong'),('HU', 'Hungary'),
        ('IS', 'Iceland'),('IN', 'India'),('ID', 'Indonesia'),('IR', 'Iran'),('IQ', 'Iraq'),('IE', 'Ireland'),('IL', 'Israel'),('IT', 'Italy'),
        ('JM', 'Jamaica'),('JP', 'Japan'),('JO', 'Jordan'),
        ('KZ', 'Kazakhstan'),('KE', 'Kenya'),('KI', 'Kiribati'),('KP', 'Korea (North)'),('KR', 'Korea (South)'),('KW', 'Kuwait'),('KG', 'Kyrgyzstan'),
        ('LA', 'Laos'),('LV', 'Latvia'),('LB', 'Lebanon'),('LS', 'Lesotho'),('LR', 'Liberia'),('LY', 'Libya'),('LI', 'Liechtenstein'),('LT', 'Lithuania'),
        ('LU', 'Luxembourg'),
        ('MO', 'Macau'),('MK', 'Macedonia'),('MG', 'Madagascar'),('MW', 'Malawi'),('MY', 'Malaysia'),('MV', 'Maldives'),('ML', 'Mali'),('MT', 'Malta'),
        ('MH', 'Marshall Islands'),('MQ', 'Martinique'),('MR', 'Mauritania'),('MU', 'Mauritius'),('YT', 'Mayotte'),('MX', 'Mexico'),('FM', 'Micronesia'),
        ('MD', 'Moldova'),('MC', 'Monaco'),('MN', 'Mongolia'),('MS', 'Montserrat'),('MA', 'Morocco'),('MZ', 'Mozambique'),('MM', 'Myanmar'),
        ('NA', 'Namibia'),('NR', 'Nauru'),('NP', 'Nepal'),('NL', 'Netherlands'),('AN', 'Netherlands Antilles'),('NC', 'New Caledonia'),('NZ', 'New Zealand'),
        ('NI', 'Nicaragua'),('NE', 'Niger'),('NG', 'Nigeria'),('NU', 'Niue'),('NF', 'Norfolk Island'),('MP', 'Northern Mariana Islands'),('NO', 'Norway'),
        ('OM', 'Oman'),
        ('PK', 'Pakistan'),('PW', 'Palau'),('PA', 'Panama'),('PG', 'Papua New Guinea'),('PY', 'Paraguay'),('PE', 'Peru'),('PH', 'Philippines'),('PN', 'Pitcairn'),
        ('PL', 'Poland'),('PT', 'Portugal'),('PR', 'Puerto Rico'),
        ('QA', 'Qatar'),
        ('RE', 'Reunion'),('RO', 'Romania'),('RU', 'Russian Federation'),('RW', 'Rwanda'),
        ('KN', 'Saint Kitts And Nevis'),('LC', 'Saint Lucia'),('VC', 'St Vincent/Grenadines'),('WS', 'Samoa'),('SM', 'San Marino'),('ST', 'Sao Tome'),('SA', 'Saudi Arabia'),
        ('SN', 'Senegal'),('SC', 'Seychelles'),('SL', 'Sierra Leone'),('SG', 'Singapore'),('SK', 'Slovakia'),('SI', 'Slovenia'),('SB', 'Solomon Islands'),('SO', 'Somalia'),
        ('ZA', 'South Africa'),('ES', 'Spain'),('LK', 'Sri Lanka'),('SH', 'St. Helena'),('PM', 'St.Pierre'),('SD', 'Sudan'),('SR', 'Suriname'),('SZ', 'Swaziland'),('SE', 'Sweden'),
        ('CH', 'Switzerland'),('SY', 'Syrian Arab Republic'),
        ('TW', 'Taiwan'),('TJ', 'Tajikistan'),('TZ', 'Tanzania'),('TH', 'Thailand'),('TG', 'Togo'),('TK', 'Tokelau'),('TO', 'Tonga'),('TT', 'Trinidad And Tobago'),
        ('TN', 'Tunisia'),('TR', 'Turkey'),('TM', 'Turkmenistan'),('TV', 'Tuvalu'),
        ('UG', 'Uganda'),('UA', 'Ukraine'),('AE', 'United Arab Emirates'),('UK', 'United Kingdom'),('UY', 'Uruguay'),('UZ', 'Uzbekistan'),
        ('VU', 'Vanuatu'),('VA', 'Vatican City State'),('VE', 'Venezuela'),('VN', 'Viet Nam'),('VG', 'Virgin Islands (British)'),('VI', 'Virgin Islands (U.S.)'),
        ('EH', 'Western Sahara'),
        ('YE', 'Yemen'),('YU', 'Yugoslavia'),
        ('ZR', 'Zaire'),('ZM', 'Zambia'),('ZW', 'Zimbabwe')
    ]

    country_origin = """
                            <tr id="country_dl_row"><td>Country of Origin</td><td><select id="origin" name="origin" required>"""
    for key, v in value:
        country_origin += '<option value="'+key+'">'+v+'</option>'

    country_origin += '</select></td><td > <button type="button" onclick="add_country()">Add Another Country</button> </td></tr>'
    return country_origin


ing_doctype_dict = {
    'specsheet': [
                    'microsensitive',
                    'rm_ingredient_statement',
                 ],
    'sds':'cas',
    'allergen': [
                    'eggs',
                    'milk',
                    'peanuts',
                    'soybeans',
                    'wheat',
                    'sunflower',
                    'sesame',
                    'mollusks',
                    'mustard',
                    'celery',
                    'lupines',
                    'yellow_5',
                    'fish',
                    'crustacean',
                    'treenuts',
                    'sulfites_ppm',
                ],
    'nutri': 'nutri',
    'GMO': 'new_gmo',
    'GPVC':'',
    'LOG': 'log_rms',
    'natural': 'natural_document_on_file',
    'origin': 'country_of_origin',
    'vegan': 'vegan',
    'organic': 'organic_compliant',
    'organic_cert':'organic_certified',
    'kosher': 'kosher',
    'halal': 'halal',
    'COA': 'salmonella',
    'COI': 'Certificate of Insurance',
    'ingbreak':'Ingredient Breakdown',
    'form40':'',
    'form20':'',
    'form20c':'',
    'form20ar':'',
}

boolean_allergens = [
    'eggs',
    'milk',
    'peanuts',
    'soybeans',
    'wheat',
    'sunflower',
    'sesame',
    'mollusks',
    'mustard',
    'celery',
    'lupines',
    'yellow_5',

]

text_allergens = [
    'fish',
    'crustacean',
    'treenuts',
    'sulfites_ppm',
]

def allergen_form():
    af = """

                <tr>
                    <td>NO ALLERGENS PRESENT</td><td><input type='checkbox' onclick='disable_allergens(this)'></td>
                </tr>
                """
    for b in boolean_allergens:
        af += """<tr>
                    <td>"""+b+"""</td>
                    <td>
                        <input type='checkbox' name='"""+b+"""' class='allergen'/>
                    </td>
                </tr>"""


    for t in text_allergens:
        if t=='sulfites_ppm':
            af += """<tr>
                        <td>"""+t+"""</td>
                        <td>
                            <input type='number'  name='"""+t+"""' class='allergen'/>
                        </td>
                    </tr>"""
        else:
            af += """<tr>
                        <td>"""+t+"""</td>
                        <td>
                            <input type='text'  name='"""+t+"""' class='allergen'/>
                        </td>
                    </tr>"""

    # af += "</table>"

    return af


def allergen_form_submission(request, temp_ing, type):
    for b in boolean_allergens:
        if request.POST.get(b, False):
            setattr(temp_ing, b , True)
        else:
            setattr(temp_ing, b, False)
    for t in text_allergens:
        if t == 'sulfites_ppm':
            if request.POST.get(t, 0):
                setattr(temp_ing, t , int(request.POST[t]))
            else:
                setattr(temp_ing, t, 0)

        else:
            if request.POST.get(t, ""):
                setattr(temp_ing, t ,request.POST[t])
            else:
                setattr(temp_ing, t, "")

    temp_ing.save()


def nutritemp_form_validation(request, temp, type):
    n = nutriFormTemp(request.POST, instance = temp)
    if n.is_valid():
        n.save()
        return True
    return False




def compare_temp(dv1, dv2):
    auto = ['GPVC','COI','form40', 'form20', 'form20ar', 'form20c', 'ingbreak']
    i1 = dv1.temp_ingredient
    i2 = dv2.temp_ingredient
    delta1 = dv1.expiration - date.today()
    delta2 = dv2.expiration - date.today()
    # mismatching expirations
    if not dv1.days_until_expiration == dv2.days_until_expiration:
        return False
    # auto verify auto docs
    elif dv1.document.doctype == dv2.document.doctype and dv1.document.doctype in auto and delta1.days == delta2.days:
        return True

    # date mismatch
    elif not dv1.is_documentdate == dv2.is_documentdate:
        return False

    elif dv1.document.doctype == 'nutri':
        n1 = dv1.temp_nutri
        n2 = dv2.temp_nutri
        fields = [x.name for x in NutriInfoTemp._meta.fields]
        exclude = ['id', 'user']
        for f in fields:
            if not f in exclude and not getattr(n1, f) == getattr(n2, f):
                return False

    # allergen comparison
    elif isinstance(ing_doctype_dict[dv1.document.doctype], list):
        fields = ing_doctype_dict[dv1.document.doctype]
        # allergen comparison
        for f in fields:
            if not getattr(i1, f) == getattr(i2, f):
                return False

    elif dv1.document.doctype == 'COA':
        if not i1.salmonella == i2.salmonella or not dv1.rm_retain.r_number == dv2.rm_retain.r_number:
            return False

    elif dv1.document.doctype == 'origin':
        t1 = i1.country_of_origin.split(',')
        t2 = i2.country_of_origin.split(',')
        if not set(t1) == set(t2):
            return False

    elif dv1.document.doctype == 'LOG':
        if not set(i1.log_rms) == set(i2.log_rms):
            return False

    elif dv1.document.doctype == 'sds':
        if not getattr(i1, ing_doctype_dict[dv1.document.doctype]) == getattr(i2, ing_doctype_dict[dv2.document.doctype]):
            return False
        if not getattr(i1, 'cas2') == getattr(i2, 'cas2'):
            return False
        if not getattr(i1, 'cas2_percentage') == getattr(i2, 'cas2_percentage'):
            return False
    else:
        if not getattr(i1, ing_doctype_dict[dv1.document.doctype]) == getattr(i2, ing_doctype_dict[dv2.document.doctype]):
            return False

    return True


# def determine_expiration(request):
#     expiration = date.today()
#     year = timedelta(days = 365)
#     threeyears = ['origin', 'specsheet', 'GMO', 'sds', 'form20', 'allergen', 'nutri', 'natural']

def save_to_main(dv):
    i = dv.document.rawmaterial
    if NutriInfo.objects.filter(ingredient = i).exists():
        n = NutriInfo.objects.get(ingredient = i)
    else:
        n = NutriInfo(ingredient = i)
        n.save()
    # n = NutriInfo.objects.get(ingredient = i)
    d = dv.document
    dt = dv.document.doctype
    auto = ['GPVC','COI', 'form40', 'form20', 'form20ar', 'form20c', 'ingbreak']
    exp = dv.expiration
    year = timedelta(days = 365)
    oneyear = ['LOG', 'COI', 'form40', 'kosher', 'halal', 'specsheet', 'sds', 'form20', 'GPVC', 'organic_cert', 'form20ar', 'organic', 'form20c']
    expiration_date = ['form20c', 'kosher', 'halal']
    threeyears = ['origin', 'GMO', 'vegan', 'allergen', 'nutri', 'natural', 'ingbreak']
    # expiration in 1 year
    if dv.is_documentdate:
        if dt == 'nutri':
            exp = exp + year*5
        elif dt in oneyear:
            exp = exp + year
        elif not dt in expiration_date:
            exp = exp + year*3
    # else:
    #     exp = exp + year*
    d.expiration = exp
    d.save()

    if dt == 'COA':
        retain = dv.rm_retain
        setattr(retain, 'salmonella_negative_check', dv.temp_ingredient.salmonella)
        setattr(retain, 'coa_document', dv.document)
        setattr(i, 'salmonella_tested_for_negative', )
        # retain.coa_document = dv.document
        # retain.save()
        # retain.salmonella_negative_check = dv.temp_ingredient.salmonella
        retain.save()
    elif dt == 'sds':
        setattr(i, 'cas', getattr(dv.temp_ingredient, 'cas'))

        if getattr(dv.temp_ingredient, 'cas2'):
            setattr(i, 'cas2', getattr(dv.temp_ingredient, 'cas2'))
            setattr(i, 'cas2_percentage', getattr(dv.temp_ingredient, 'cas2_percentage'))

        i.save()

    elif dv.document.doctype == 'nutri':
        nutrifields = [x.name for x in NutriInfo._meta.fields]
        exclude = ['id', 'ingredient']
        for f in nutrifields:
            if not f in exclude:
                setattr(n, f, getattr(dv.temp_nutri, f))
        n.save()

    elif dv.document.doctype == 'LOG':
        # this is where well set the document log rms to empty or populated
        doc = dv.document
        # doc.log_rms = dv.temp_ingredient.log_rms
        setattr(doc, 'log_rms', dv.temp_ingredient.log_rms)
        doc.save()

    elif isinstance(ing_doctype_dict[dt],list):
        fields = ing_doctype_dict[dt]
        for f in fields:
            setattr(i, f, getattr(dv.temp_ingredient, f))
        i.save()

    elif not dv.document.doctype in auto:
        setattr(i, ing_doctype_dict[dt], getattr(dv.temp_ingredient, ing_doctype_dict[dt]))
        i.save()


def single_val_validation(request, temp, type):
    # only being used by gmo
    setattr(temp, 'new_gmo' , request.POST.get(type))
    temp.save()

def halal_validation(request, temp, type):
    # only being used by gmo
    setattr(temp, ing_doctype_dict[type] , request.POST.get(type))
    temp.save()

def kosher_validation(request, temp, type):
    setattr(temp, 'kosher', request.POST.get('kosher'))
    temp.save()

def vegan_validation(request, temp, type):
    if request.POST.get('vegan') == 'true':
        setattr(temp, 'vegan', True)
    else:
        setattr(temp, 'vegan', False)

    temp.save()

def sds_validation(request, temp, type):
    setattr(temp, 'cas', request.POST.get('sds'))
    if 'cas2' in request.POST:
        setattr(temp, 'cas2', str(request.POST.get('cas2')))
        setattr(temp, 'cas2_percentage' , Decimal(request.POST.get('cas2percent')))
        # temp.cas2_percentage = request.POST.get('cas2percent')
        # setattr(temp, 'cas2_percentage', request.POST.get('cas2percent'))
    temp.save()


def coa_validation(request, temp, type):
    if 'salmonella' in request.POST and request.POST.get('salmonella') == 'NA':
        setattr(temp, 'salmonella', False)
    else:
        setattr(temp, 'salmonella', True)
    temp.save()


def spec_sheet_validation(request, temp, type):
    if 'is' in request.POST or 'review' in request.POST:
        setattr(temp, 'rm_ingredient_statement', str(request.POST.get('ingredient_statement')))

    setattr(temp, 'microsensitive', str(request.POST.get('specsheet')))

    temp.save()

def origin_validation(request, temp, type):
    countries = request.POST.getlist('origin')
    concatenate = ""
    for c in countries:
        concatenate += c + ","

    setattr(temp, 'country_of_origin', concatenate[:len(concatenate)-1])
    temp.save()

def organic_compliant_validation(request, temp, type):
    if request.POST.get(type) == 'true':
        setattr(temp, ing_doctype_dict[type], True)
    else:
        setattr(temp, ing_doctype_dict[type], False)

    temp.save()

def log_verification(request, temp, type):
    # arr = ['1', '2']
    if request.POST.get('specification_type') == 'ps':
        product_arr = request.POST.get('products').split("__")
        setattr(temp, 'log_rms', product_arr)

    else:
        setattr(temp, 'log_rms', [])

    temp.save()
    # return HttpResponseRedirect('/access')

def nutriformformat(nutriform):
    major = ["Carbohydrates", "Ash", "Calories", "Protein", "Other Fat", "Water", "Flavor Content", "Alcohol Content"]
    grams = ["Saturated Fat", "Monounsaturated Fat", "Polyunsaturated Fat", "Sugars", "Added Sugars", "Dietary Fiber", 'Ethyl Alcohol', 'Fusel Oil', 'Propylene Glycol', 'Triethyl Citrate', 'Glycerin', 'Triacetin',]
    mcg = ["Vitamin A", "Vitamin D"]
    # formatdict = """<tr>
    #     <td>Document Date</td><td><input type='date' id='expiration' name='expiration' required/></td>
    # </tr>"""
    formatdict = ""
    for row in nutriform:
        if row.label == "Shrt_Desc":
            formatdict += """
                                      <tr>
                                        <td><h3>Raw Material</h3></td>
                                        <td><p>"""+str(row.value)+"""</p></td>
                                        <div class = "hide">"""+str(row)+"""</div>
                                      </tr>"""
        elif row.label == "Calories":
            formatdict += """
                                    <tr>
                                        <td><h3>Calories</h3></td>
                                        <td><p id = "calories"></p></td>
                                        <div class = "hide">"""+str(row)+"""</div>
                                    </tr>"""

        elif row.label in major:
            if row.label == "Other Fat":
                formatdict += """
                                        <tr>
                                            <td><h3>Total Fats</h3></td>
                                            <td> <p id = "total fat"></p></td>
                                        </tr>
                                        <tr>
                                            <tr>
                                              <td class = "subcategory">"""+str(row.label)+"""</td>
                                              <td>"""+str(row)+""" g</td>
                                            </tr>
                                        </tr>"""
            elif row.label == "Carbohydrates":
                formatdict += """
                                        <tr>
                                            <td><h3>"""+str(row.label)+"""</h3></td>
                                            <td> <p id = "totalcarbs"></p></td>
                                        </tr>
                                        <tr>
                                            <tr>
                                              <td class = "subcategory">Other Carbohydrates</td>
                                              <td>"""+str(row)+""" g</td>
                                            </tr>
                                        </tr>"""
            elif row.label == 'Alcohol Content':
                formatdict += """
                                        <tr>
                                            <td><h3>"""+str(row.label)+"""</h3></td>
                                            <td> <span id = "totalalcohol"></span> g</td>
                                        </tr>"""
            else:
                formatdict += """
                                          <tr>
                                            <td><h3>"""+str(row.label)+"""</h3></td>
                                            <td> <p>"""+str(row)+""" g</p></td>
                                          </tr>
                                         """
        else:
            formatdict += """<tr>
                                        <td class = "subcategory">"""+str(row.label)+"""</td>"""
            if row.label in grams:
                formatdict += """
                                            <td>"""+str(row)+""" g</td>
                                          </tr>
                                        """
            elif row.label in mcg:
                formatdict += """
                                            <td>"""+str(row)+""" mcg</td>
                                          </tr>
                                        """
            else:
                formatdict += """
                                            <td>"""+str(row)+""" mg</td>
                                          </tr>
                                        """
    return formatdict+"""  <div class = "totalweight" ><span id = "total"></span> g</div>"""




def list_rnumbers(rm):
    options = ""
    retains = RMRetain.objects.filter(pin = rm.id)
    for r in retains:
        if r.related_ingredient.rawmaterialcode == rm.rawmaterialcode:
            options += "<option value='R"+str(r.r_number)+"-"+str(r.year)+"'>" + str(r.lot)

    return options

def list_products(rm):
    options = ""
    # products = PurchaseOrder.objects.filter(supplier = rm.supplier)
    products = Ingredient.objects.filter(supplier = rm.supplier)

    # products = PurchaseOrder.
    # products = PurchaseOrderLineItem.objects.filter(po__supplier = rm.supplier)
    for p in products:
        options += "<option value='"+str(p.rawmaterialcode)+"'>"+str(p)+"</option>"

    return options

def flavor_datalist():
    fl = Flavor.objects.all()
    dl = """<input list='flavors'>
            <datalist id='flavors'>
            """
    for f in fl:
        dl += "<option value='"+str(f.number)+"'>"

    dl += "</datalist>"

    return dl

def ing_datalist():
    ing = Ingredient.objects.all()
    dl = """<input list='ingredients' required>
            <datalist id='ingredients'>
            """
    for i in ing:
        if i.supplier:
            dl += "<option value='"+str(i.id)+" | "+str(i.supplier.suppliercode)+"'>"

    dl += "</datalist>"
    return dl



def dv_autocomplete(request):
    ing = request.GET.get('pin')
    results = []
    r = {}

    if ing == "":
        return JsonResponse(r)
    else:
        pin = Ingredient.objects.exclude(supplier__suppliercode='FDI').exclude(supplier=None).filter(id__startswith = int(ing))

    if ing.isdigit() and pin.exists():
        for i in pin:
            # if i.supplier:
                results.append(str(i.id) + " | " + str(i.supplier.suppliercode))
            # results += "<option value='"+str(i.id) + " | " + str(i.supplier.suppliercode)+"'>"

        r['results'] = results
        # data = json.dumps(r)
    else:
        r['results'] = []

    return JsonResponse(r)

def json_test_response(request, flavor_number):
    from django.forms.models import model_to_dict
    f = list(Flavor.objects.filter(number = flavor_number).values())
    f = list(f)
    return JsonResponse(f, safe=False)
    # return Jsonf2dict

additionalhtml = """
                    <tr>
                        <td>Please appropriate date type:
                            <ul>
                                <li><input type = 'radio' name = 'doc_date' value = 'document_date' required/> Document Date</li>
                                <li><input type = 'radio' name = 'doc_date' value = 'expiration_date'/> Expiration Date</li>
                            </ul>
                        </td>
                        <td><input type='date' id='expiration' name='expiration' required/></td>
                    </tr>"""

kosheronlyhtml = """
                    <tr>
                        <td>Please enter expiration date:
                            <ul hidden>
                                <li><input type = 'radio' name = 'doc_date' value = 'expiration_date' checked/> Expiration Date</li>
                            </ul>
                        </td>
                        <td><input type='date' id='expiration' name='expiration' required/></td>
                    </tr>"""

docv_dict = {
    'specsheet': """<br><table>"""
                    +additionalhtml+
                    """<tr>
                            <td>
                                Microsensitive?
                            </td>
                            <td>
                                <select name='specsheet' id='specsheet'>
                                    <option value='True'>True</option>
                                    <option value='False'>False</option>
                                </select>
                            </td>
                        </tr>
                        <tr>
                            <td>
                                Does it have an ingredient statement?
                            </td>
                            <td>
                                Check if yes
                                <input type='checkbox' id='is' name='is' onclick='check_is();'/>
                            </td>
                            <td>
                                <textarea id='ingredient_statement' name='ingredient_statement' disabled placeholder='Fill ingredient statement here if applicable.'></textarea>
                            </td>
                        </tr>
                    </table><br>""",
    'sds': """<br>
                <table id = 'cas'>"""+additionalhtml+"""
                    <tr id='firstcasrow'>
                        <td>CAS Number (Leave blank if not required): </td>
                        <td><input type="text" id="sds" name="sds"/></td>
                        <td><button type='button' id='casrowbtn' onclick='secondcas();'>Add Second CAS</button></td>
                    </tr>
                </table>
            <br>""",
    'allergen':"""<table id="list" name="allergen">"""+ additionalhtml + allergen_form() + "</table>",
    'nutri': "<div  class='nutri' oninput = 'checkTotalWeight()'><table>"+additionalhtml+"<tr><td>Total Weight</td> <td><span id = 'totalw'> </span> g </td></tr>"+nutriformformat(nutriFormTemp())+"</table></div>",
    'GMO': """<br><table>"""+additionalhtml+"""

                <tr><td>GMO Status: </td><td><select name='GMO' id ="GMO" required>
                <option disabled selected value> -- select an option -- </option>
                <option value='GMO Free'>GMO Free</option>
                <option value='GMO Non-Detect'>GMO Non-Detect</option>
                <option value='Genetically Modified'>Genetically Modified</option>
            </select></td></tr></table><br>""",
    # 'LOG':"<table>"+additionalhtml+"</table>",
    'natural': "<table>"+additionalhtml+"</table>",
    'origin': "<table id='origin_table'>"+additionalhtml + countries() + "</table>",
    'organic': """<table>"""+additionalhtml+"""
                <tr>
                    <td>Select organic compliance status: </td>
                    <td>
                        <select name='organic' id='organic' required>
                            <option disabled selected value> -- select an option -- </option>
                            <option value='true'>Organic Compliant</option>
                            <option value='false'>Not Organic Compliant</option>
                        </select>
                    </td>
                </tr>
                </table>""",
    'organic_cert': """<table>"""+additionalhtml+"""
                <tr>
                    <td>Select organic certification status: </td>
                    <td>
                        <select name='organic_cert' id='organic_cert' required>
                            <option disabled selected value> -- select an option -- </option>
                            <option value='true'>Organic Certified</option>
                            <option value='false'>Not Organic Certified</option>
                        </select>
                    </td>
                </tr>
                </table>""",
    'kosher':"""<table>"""+kosheronlyhtml+"""
                    <tr>
                        <td>Select kosher status: </td>
                        <td><select name='kosher' id ="kosher" required>
                        <option disabled selected value> -- select an option -- </option>
                        <option value='Not Kosher'>Not Kosher</option>
                        <option value='All'>All</option>
                        <option value='Meat'>Meat</option>
                        <option value='Dairy'>Dairy</option>
                        <option value='Pareve'>Pareve</option>
                        <option value='Passover'>Passover</option>
                    </tr>
                </table>""",
    'halal':"""<table>"""+additionalhtml+"""
                    <tr>
                        <td>Select halal status: </td>
                        <td>
                            <select name='halal' id ="halal" required>
                                <option disabled selected value> -- select an option -- </option>
                                <option value='Not Halal'>Not Halal</option>
                                <option value='Halal Compliant'>Halal Compliant</option>
                                <option value='Halal Certified'>Halal Certified</option>
                            </select>
                        </td>
                    </tr>
                </table>""",
    'vegan':"""<table>"""+additionalhtml+"""
                    <tr>
                        <td>Select vegan status: </td>
                        <td>
                            <select name='vegan' id='vegan' required>
                                <option disabled selected value> -- select an option -- </option>
                                <option value='true'>Vegan</option>
                                <option value='false'>Not Vegan</option>
                            </select>
                        </td>
                    </tr>
                </table>""",
    'COI': "<table>"+additionalhtml+"</table>",
    'form20':"<table>"+additionalhtml+"</table>",
    'form20ar':"<table>"+additionalhtml+"</table>",
    'form20c':"<table>"+additionalhtml+"</table>",
    'form40':"<table>"+additionalhtml+"</table>",
    'ingbreak':"<table>"+additionalhtml+"</table>",
    'GPVC':"<table>"+additionalhtml+"</table>",
}

def document_verification(request, doc_id):
    pagetitle = "Document Verification"
    docbytype = [
        'origin',
        'specsheet',
        'GMO',
        'GPVC',
        'LOG',
        'sds',
        'kosher',
        'halal',
        'allergen',
        'nutri',
        'COI',
        'organic',
        'organic_cert',
        'vegan',
        'natural',
        'COA',
        'ingbreak',
        'form20',
        'form20ar',
        'form20c',
        'form40',
    ]

    # REFUSE UNAUTHORIZED USERS
    if not request.user.has_perm('access.can_verify'):
            return render(
                request,
                'access/ingredient/document_verification.html',
                {
                    'message':'Not authorized to verify documents',
                }
            )

    # REDIRECT TO DOCUMENT CONTROL VIA PINSEARCH
    if request.method == 'POST' and 'pinsearch' in request.POST:
        return HttpResponseRedirect('/access/document_control/'+str(request.POST.get('pin_search'))+"/")

    admin = False

    if request.user.is_superuser:
        admin = True



# Ingredient.objects.filter(doctype=b, rawmaterialcode = i).latest('-expiration')
#
#
    if request.GET:
        # display by doctype
        three_years_ago = date.today() - relativedelta(years=3)
        # rawmaterials bought in last three years that are not discontinued
        rms = PurchaseOrderLineItem.objects.filter(raw_material__discontinued=False, due_date__range=[three_years_ago, date.today()]).order_by().values_list('raw_material', flat=True).distinct()
        d = []
        for b in docbytype:
            # LIST UNVERIFIED DOCUMENTS BY DOCTYPE
            if b in request.GET:
                # d = [obj for obj in Documents.objects.filter(doctype = b).exclude(rawmaterial__discontinued=True) if obj.verified == False and obj.dv_count < 2 and not request.user.username in obj.get_verifiers]
                for r in rms:
                    doc = Ingredient.objects.get(rawmaterialcode=r).get_latest_document(b)
                    if doc:
                        if doc.dv_count < 2 and request.user.username not in doc.get_verifiers:
                            d.append(doc)
                if d:
                    message = ""
                else:
                    message = "No documents of type "+b+" need to be verified."
                    d = None
                return render(
                    request,
                    'access/ingredient/document_verification.html',
                    {
                        'message':message,
                        'documents':d,
                        'admin':admin,
                    }
                )

            # LIST ALL DOCUMENTS FOR DOCREVIEW BY DOCTYPE
            elif "review_"+b in request.GET:
                # d = [obj for obj in Documents.objects.filter(doctype = b).exclude(rawmaterial__discontinued=True) if obj.verified == False and obj.dv_count==2 and not request.user.username in obj.get_verifiers]
                for r in rms:
                    doc = Ingredient.objects.get(rawmaterialcode=r).get_latest_document(b)

                    if doc:
                        if doc.dv_count == 2 and not doc.verified and request.user.username not in doc.get_verifiers:
                            d.append(doc)

                if d:
                    message = ""
                else:
                    message = "No documents of type "+b+" need to be verified."
                    d = None
                return render(
                    request,
                    'access/ingredient/document_verification.html',
                    {
                        'message':message,
                        'documents':d,
                        'admin':admin,
                    }
                )

            # list upload links for docs for specific rms
            elif "rm_"+b in request.GET:
                rms = []
                # three_years_ago = date.today() - relativedelta(years=3)

                rawmaterialcodes = PurchaseOrderLineItem.objects.filter(due_date__range=[three_years_ago, date.today()]).values_list('raw_material',flat=True).distinct()
                rm_queryset = Ingredient.objects.filter(rawmaterialcode__in=rawmaterialcodes, discontinued = False).exclude(documents__doctype=b).exclude(supplier__suppliercode='FDI')


                # if b == 'natural':
                #     rm_queryset = rm_queryset.filter(art_nati="Nat")

                if b == 'vegan':
                    rm_queryset = rm_queryset.exclude(milk=True).exclude(eggs=True).exclude(id=266)

                # elif b == 'organic':
                #     rm_queryset = rm_queryset.filter(organic_compliant=True)

                auto = ['COI', 'form40', 'form20', 'form20ar', 'form20c']
                f20 = ['form20', 'form20ar', 'form20c']

                if b in auto:
                    # queryset of distinct suppliers
                    if b in f20:
                        s = Supplier.objects.filter(ingredient__documents__doctype__in=f20)
                    else:
                        s = Supplier.objects.filter(ingredient__documents__doctype=b)
                    rm_queryset = rm_queryset.exclude(supplier__in=s)


                for rm in rm_queryset:
                    # if not rm in rms and not Documents.objects.filter(doctype=b, rawmaterial=rm, rawmaterial__discontinued=False).exists():
                    if not rm.get_latest_document('b'):
                        rms.append(rm)

                if len(rms) > 0:
                    message = ""
                else:
                    message = "No documents of type "+b+" need to be verified."

                return render(
                    request,
                    'access/ingredient/document_verification.html',
                    {
                        'message':message,
                        'docsby_rm':rms,
                        'doctype':b,
                        'documents':None,
                        'admin':admin,
                    }
                )



    message = ""
    prev = ""
    # d = [obj for obj in Documents.objects.exclude(rawmaterial=None).exclude(rawmaterial__discontinued=True) if obj.verified == False and not request.user.username in obj.get_verifiers]

    if doc_id:
        doc = Documents.objects.get(id= doc_id)

        docv_dict['COA'] = """<br><table>
                                """+additionalhtml+"""
                                <tr>
                                    <td>
                                        Has this been tested negative for salmonella?
                                    </td>
                                    <td>
                                        <select name='salmonella' id ="salmonella" required>
                                                    <option disabled selected value> -- select an option -- </option>
                                                    <option value='Yes'>Yes</option>
                                                    <option value='NA'>Not applicable</option>
                                                </select>
                                    </td>
                                </tr>
                                <tr>
                                    <td>
                                        Select appropriate R Number:
                                    </td>
                                    <td>
                                        <input list ="rnumbers" name="rnumbers" required>
                                        <datalist id ="rnumbers">
                                        """+ list_rnumbers(doc.rawmaterial) +"""
                                        </datalist>
                                    </td>
                                </tr>
                            </table><br>"""

        docv_dict['LOG'] = """<br><table>
                                """+additionalhtml+"""
                                <tr>
                                    <td>
                                        <input type = 'radio' onChange='toggle()' name='specification_type' value='ss'> Supplier Specific <br>
                                        <input type = 'radio' onChange='toggle()' name='specification_type' value='ps' checked> Product Specific
                                    </td>
                                    <td>
                                        <input type='text'
                                           placeholder='add and select applicable product'
                                           class='flexdatalist'
                                           data-min-length='1'
                                           multiple='multiple'
                                           list='product_list'
                                           name='products'
                                           id = 'product_list_id'
                                           required
                                           >
                                        <datalist id ="product_list">
                                        """+ list_products(doc.rawmaterial) +"""
                                        </datalist>
                                    </td>
                                </tr>
                            </table><br>"""
        # CURRENT USER HAS ALREADY VERIFIED
        #
        if DocumentVerification.objects.filter(document=doc, verifier=request.user).exists():

            return render(
                request,
                'access/ingredient/document_verification.html',
                {
                    'message':'Already verified this document',
                    # 'documents':d,
                }
            )


        # document not verified by two peeps yet
        elif not request.method == "POST" and DocumentVerification.objects.filter(document = doc).count() < 2:
            f = docv_dict[doc.doctype]
            if not doc.doctype == "nutri":
                f += """<input type="submit" value="Submit Verification"/><br>
                        <br>
                        <h3>Document Preview</h3>
                        <br>

                            <iframe title='"""+str(doc.filename)+"""' src='"""+str(doc.uploadfile.url)+"""'  style="height: 100vh; width: 100%;"></iframe>
                        """

            else:
                f += """<div class='nutrisubmit'>
                            <input type="submit" value="Submit Verification"/>
                        </div>

                        <div><iframe src='"""+str(doc.uploadfile.url)+"""'style="height: 100%; width: 45%;" class='nutriiframe'>
                        </iframe></div><br>"""


            prev = request.META.get('HTTP_REFERER')
            return render(

                request,
                'access/ingredient/document_verification.html',
                {
                    'message':"",
                    # 'documents':d,
                    'previous':prev,
                    'form':f,
                    'doc':doc,
                    'page_title':pagetitle,
                    # 'ingredients':ing_datalist(),
                }
            )

        elif request.method == "POST":
            # HANDLE DOCV SUBMISSION
            #

            # move doc to another RM/doctype
            if 'doc_change' in request.POST:
                 # get rawmaterial and DOC_TYPES
                 new_ingredient = request.POST.get('correct_ing')
                 new_ingredient = new_ingredient.split(" | ")
                 new_dt = request.POST.get('correct_type')
                 doc = Documents.objects.get(id=int(request.POST.get('moving_doc')))
                 ing = Ingredient.objects.get(id=int(new_ingredient[0]), supplier__suppliercode=new_ingredient[1])
                 doc.rawmaterial = ing
                 doc.doctype = new_dt
                 doc.save()
                 return HttpResponseRedirect('/access/document_verification/'+str(doc.id))

            # discard coas that dont need to be verified
            if 'discardcoa' in request.POST:
                doc = Documents.objects.get(id=int(request.POST.get('discardcoa')))
                doc.delete()
                return HttpResponseRedirect('/access/document_verification/?COA')

            temp = IngredientTemp(user = request.user, temp_rmcode = doc.rawmaterial.rawmaterialcode, new_gmo="")
            ntemp= NutriInfoTemp(user = request.user, ingredient = doc.rawmaterial)
            rmretain = None
            is_documentdate = True
            expiration = request.POST.get('expiration')
            expiration = datetime.strptime(expiration, "%Y-%m-%d").date()
            date_type = request.POST.get('doc_date')

            if date_type == 'expiration_date':
                is_documentdate = False

            # CREATE OR GET INGREDIENTTEMP AND NUTRIINFOTEMP
            if IngredientTemp.objects.filter(user_id = request.user.id).filter(temp_rmcode = doc.rawmaterial.rawmaterialcode).exists():
                temp = IngredientTemp.objects.get(user_id = request.user.id, temp_rmcode = doc.rawmaterial.rawmaterialcode)
            # else:
            #     temp = IngredientTemp(user = request.user, temp_rmcode = doc.rawmaterial.rawmaterialcode, new_gmo="")
            #     temp.save()

            if NutriInfoTemp.objects.filter(user = request.user).filter(ingredient = doc.rawmaterial).exists():
                ntemp = NutriInfoTemp.objects.get(user = request.user, ingredient = doc.rawmaterial)
            # else:
            #     # ntemp = NutriInfoTemp(user = request.user, ingredient = doc.rawmaterial)
            #     ntemp.save()
            auto = ['natural','GPVC','COI', 'form40', 'form20', 'form20ar', 'form20c', 'ingbreak']
            case_switch = {
                'specsheet':spec_sheet_validation,
                'sds':sds_validation,
                'allergen':allergen_form_submission,
                'nutri':nutritemp_form_validation,
                'origin':origin_validation,
                # 'GMO':single_val_validation(temp, doc.doctype , str(request.POST.get(doc.doctype))), #(request, temp)
                'GMO':single_val_validation,
                'LOG':log_verification,
                # 'natural':"",
                'kosher':kosher_validation,
                'halal':halal_validation,
                'vegan':vegan_validation,
                'COA':coa_validation,
                # 'COI':"",
                # 'form20':"",
                # 'form20ar':"",
                # 'form20c':"",
                # 'form40':"",
                # 'ingbreak':"",
                # 'GPVC':"",
                'organic':organic_compliant_validation,
                'organic_cert':organic_compliant_validation,
            }

            # log_verification(request, temp, 'LOG')

            if doc.doctype == 'nutri':
                case_switch[doc.doctype](request, ntemp, 'nutri')
            elif not doc.doctype in auto:
                case_switch[doc.doctype](request, temp, doc.doctype)

            # FOR COA'S. ASSIGN RETAIN TO DV WHEN APPLICABLE
            if 'rnumbers' in request.POST:
                rnumyear = request.POST.get('rnumbers')[1:].split("-")
                rmretain = RMRetain.objects.get(pin=doc.rawmaterial.id, r_number = int(rnumyear[0]), year= int(rnumyear[1]))

            temp.save()
            ntemp.save()
            docv = None
            submitmessage = ""
            # HANDLE DOCREVIEW
            if 'review' in request.POST:
                docv = DocumentVerification(document = doc, verifier=request.user, temp_ingredient = temp, temp_nutri=ntemp, rm_retain =rmretain, expiration=expiration, final=True, is_documentdate=is_documentdate)

                docv.save()
                # only save if it is the latest document
                if Documents.objects.filter(rawmaterial=doc.rawmaterial, doctype = doc.doctype).latest('expiration') == docv.document or doc.doctype=='COA':
                    submitmessage = "<div class='greennotification'><h2>Document verified.</h2></div>"
                    save_to_main(docv)
                else:
                    submitmessage = "<div class='rednotification'><h2>There exists a newer document for this document type and rawmaterial. Changes to database will not be made.</h2></div>"

            else:
                docv = DocumentVerification(document = doc, verifier=request.user, temp_ingredient = temp, temp_nutri=ntemp, rm_retain =rmretain, expiration=expiration, is_documentdate=is_documentdate)
                docv.save()


            # CHECK AND COMMIT HERE
            #

            dv = DocumentVerification.objects.filter(document = doc)
            # normal DV submission
            if not 'review' in request.POST and dv.count() == 1:
                submitmessage = "<div class='greennotification'><h2>Document verified.</h2></div>"
            # two DVs but data mismatch
            elif not 'review' in request.POST and dv.count() == 2 and not compare_temp(dv[0], dv[1]):
                submitmessage = "<div class='rednotification'><h2>Document verfied, but conflicting verifications for this document. Please get an admin to do a final review.</h2></div>"
            # when two DVs are identical

            elif dv.count() == 2 and compare_temp(dv[0], dv[1]):
                dv.update(final=True)
                dv[0].save()
                dv[1].save()
                if Documents.objects.filter(rawmaterial=doc.rawmaterial, doctype = doc.doctype).latest('expiration') == dv[0].document:
                    save_to_main(dv[0])
                    submitmessage = "<div class='greennotification'><h2>Document verification between two users is identical. Commiting changes to database.<h2></div>"
                else:
                    submitmessage = "<div class='rednotification'><h2>There exists a newer document for this document type and rawmaterial. Changes to database will not be made.</h2></div>"


            # d = [obj for obj in Documents.objects.all() if obj.verified == False and not DocumentVerification.objects.filter(document=obj, verifier=request.user).exists()]

            # redirect back to previous page (DV or DC) to continue workflow
            if 'next' in request.GET and not request.GET.get('next') == "" and not request.GET.get('next') == None:
                # redirect to previous
                messages.info(request, submitmessage)
                return HttpResponseRedirect(request.GET.get('next'))

            return render(
                request,
                'access/ingredient/document_verification.html',
                {
                    'message':submitmessage,
                    # 'documents':d,
                    'doc':doc,
                    'page_title':pagetitle,
                    'previous':prev,
                    'admin':admin,
                }
            )



        else:
            # DOCREVIEW VIEW
            #

            # USER NOT AUTHORIZED TO DOCREVIEW
            #
            if not request.user.is_superuser:
                    return render(
                        request,
                        'access/ingredient/document_verification.html',
                        {
                            'message':'Not authorized to do final review on documents',

                        }

                    )

            # CREATE APPROPRIATE DOCREVIEW BY DOCTYPE
            auto = ['natural','GPVC','COI', 'form40', 'form20', 'form20ar', 'form20c', 'ingbreak']
            datetd = """ <td>Please appropriate date type:
                                    <ul>
                                        <li><input type = 'radio' name = 'doc_date' value = 'document_date' required/> Document Date</li>
                                        <li><input type = 'radio' name = 'doc_date' value = 'expiration_date'/> Expiration Date</li>
                                    </ul>
                                    <input type='date' id='expiration' name='expiration' required/></td>
                                    </tr>"""
            review = DocumentVerification.objects.filter(document = doc)
            # additionalhtml = """
            #                     <tr>
            #                         <td>Document Date</td><td><input type='date' id='expiration' name='expiration' required/></td>
            #                     </tr>"""
            reviewhtml = """<div class='review'>
                                            <table id='reviewtable'>
                                                <tr>
                                                    <td>Verifier</td>
                                                    <td>"""+review[0].verifier.username+"""</td>
                                                    <td>"""+review[1].verifier.username+"""</td>
                                                    <td>"""+request.user.username+"""</td>
                                                </tr>
                                                <tr>
                                                    <td>Entered Document Date?</td>
                                                    <td>"""+str(review[0].is_documentdate)+"""</td>
                                                    <td colspan='2'>"""+str(review[1].is_documentdate)+"""</td>
                                                </tr>
                                                <tr>
                                                    <td>Document Expiration Date</td>
                                                    <td>"""+str(review[0].expiration)+"""</td>
                                                    <td>"""+str(review[1].expiration)+"""</td>



                        """
            if not doc.doctype in auto:
                # ALLERGEN DOCREVIEW
                #
                if isinstance(ing_doctype_dict[doc.doctype], list):
                    fields = ing_doctype_dict[doc.doctype]
                    reviewhtml += datetd
                    for f in fields:
                        reviewhtml += """
                                                    <tr>
                                                        <td>"""+f+"""</td>
                                                        <td>"""+str(getattr(review[0].temp_ingredient, f))+"""</td>
                                                        <td>"""+str(getattr(review[1].temp_ingredient, f))+"""</td>"""
                        if f in boolean_allergens:
                            reviewhtml += """
                                                        <td><input type='checkbox' id='"""+f+"""' name='"""+f+"""'/></td>
                                                    </tr>"""
                        elif f in text_allergens:
                            if f == 'sulfites_ppm':
                                reviewhtml += """
                                                            <td><input type='number' step='.01' id='"""+f+"""' name='"""+f+"""'/></td>
                                                        </tr>"""
                            else:
                                reviewhtml += """
                                                            <td><input type='text' id='"""+f+"""' name='"""+f+"""'/></td>
                                                        </tr>"""
                        elif f == 'microsensitive':
                            reviewhtml += """
                                                        <td>
                                                            <select name='specsheet' id='specsheet'>
                                                                <option value='True'>True</option>
                                                                <option value='False'>False</option>
                                                            </select>
                                                        </td>
                                                    </tr>"""

                        elif f == 'rm_ingredient_statement':
                            reviewhtml += """
                                                        <td>
                                                            <textarea name='ingredient_statement' id = 'ingredient_statment'></textarea>
                                                        </td>
                                                    </tr>"""

                    reviewhtml+="""</table>"""
                elif doc.doctype == 'nutri':
                    n1 = review[0].temp_nutri
                    n2 = review[1].temp_nutri
                    meta = []
                    nutriform = nutriFormTemp()
                    meta = [x.name for x in NutriInfoTemp._meta.fields]
                    reviewhtml +=""" <td>Please appropriate date type:
                        <ul>
                            <li><input type = 'radio' name = 'doc_date' value = 'document_date' required/> Document Date</li>
                            <li><input type = 'radio' name = 'doc_date' value = 'expiration_date'/> Expiration Date</li>
                        </ul>
                        <input type='date' id='expiration' name='expiration' required/></td>
                                            </tr>"""
                    for row in nutriform:
                        if not row.label == "Calories":
                            reviewhtml +="""
                                                    <tr>
                                                        <td>"""+str(row.label)+"""</td>
                                                        <td>"""+str(getattr(n1, row.name))+"""</td>
                                                        <td>"""+str(getattr(n2, row.name))+"""</td>
                                                        <td>"""+str(row)+"""</td>
                                                    </tr>"""
                    reviewhtml +="""
                                                </table>
                                            </td>
                                        </tr>
                                    </table>"""


                elif doc.doctype == 'COA':
                    reviewhtml += """<td rowspan="3" class= "coa_subrow">"""+docv_dict[doc.doctype]+"""</td></tr>
                                    <tr>
                                        <td>Salmonella Tested for Negative Result</td>
                                        <td>"""+str(getattr(review[0].temp_ingredient, ing_doctype_dict[doc.doctype]))+"""</td>
                                        <td>"""+str(getattr(review[1].temp_ingredient, ing_doctype_dict[doc.doctype]))+"""</td>

                                    </tr>
                                    <tr>
                                        <td>RM Retain</td>
                                        <td>"""+str(review[0].rm_retain)+"""</td>
                                        <td>"""+str(review[1].rm_retain)+"""</td>
                                    </tr>
                                    </table>
                                    """

                elif doc.doctype == 'LOG':
                    reviewhtml += """<td rowspan="3">"""+docv_dict[doc.doctype]+"""</td></tr>
                                    <tr>
                                        <td> List applicable rawmaterials: </td>
                                        <td><ul>"""+ review[0].temp_ingredient.list_log_rms +"""</ul></td>
                                        <td><ul>"""+ review[1].temp_ingredient.list_log_rms +"""</ul></td>
                                    </tr></table>"""


                elif doc.doctype == 'sds':

                    if getattr(review[0].temp_ingredient, 'cas2') or getattr(review[1].temp_ingredient, 'cas2'):
                        reviewhtml += """
                                            <td rowspan='5' class='coa_subrow'>"""+docv_dict[doc.doctype]+"""</td>
                                        </tr>
                                        <tr>
                                            <td>First CAS Percetage</td>
                                            <td>
                                                """+str(Decimal(100.00) - getattr(review[0].temp_ingredient, 'cas2_percentage'))+"""
                                            </td>

                                            <td>
                                                """+str(Decimal(100.00) - getattr(review[1].temp_ingredient, 'cas2_percentage'))+"""
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Second CAS Number</td>
                                            <td>"""+getattr(review[0].temp_ingredient, 'cas2')+"""</td>
                                            <td>"""+getattr(review[1].temp_ingredient, 'cas2')+"""</td>
                                        </tr>
                                        <tr>
                                            <td>Second CAS Percetage</td>
                                            <td>
                                                """+str(getattr(review[0].temp_ingredient, 'cas2_percentage'))+"""
                                            </td>

                                            <td>
                                                """+str(getattr(review[1].temp_ingredient, 'cas2_percentage'))+"""
                                            </td>
                                        """
                    else:
                        reviewhtml +=    "<td rowspan='2' class='coa_subrow'>"+docv_dict[doc.doctype]+"</td>"

                    reviewhtml += """</tr><tr>
                                        <td>CAS Number</td>
                                        <td>"""+str(getattr(review[0].temp_ingredient, 'cas'))+"""</td>
                                        <td>"""+str(getattr(review[1].temp_ingredient, 'cas'))+"""</td>

                                        """
                    reviewhtml+="</tr></table>"

                elif doc.doctype in auto:
                    reviewhtml += """<td rowspan="4" class='coa_subrow'>"""+docv_dict[doc.doctype]+"""</td></tr>
                                                    <tr>
                                                        <td>"""+ing_doctype_dict[doc.doctype]+"""</td>
                                                        <td>"""+str(review[0].expiration)+"""</td>
                                                        <td>"""+str(review[1].expiration)+"""</td>

                                                    </tr>
                                                </table>"""
                else:
                    reviewhtml += """<td rowspan="5" class='coa_subrow'>"""+docv_dict[doc.doctype]+"""</td></tr>
                                                    <tr>
                                                        <td>"""+ing_doctype_dict[doc.doctype]+"""</td>
                                                        <td>"""+str(getattr(review[0].temp_ingredient, ing_doctype_dict[doc.doctype]))+"""</td>
                                                        <td>"""+str(getattr(review[1].temp_ingredient, ing_doctype_dict[doc.doctype]))+"""</td>

                                                    </tr>

                                                </table>"""


            else:
                # reviewhtml += "</tr></table>"
                reviewhtml += datetd + "</table>"

            # end of review page based on doctype

            if not doc.doctype =='nutri':
                reviewhtml+="""<br>
                                <input type="submit" name='review' id='review' value="Submit Review"/>
                                <br>
                                <h3>Document Preview</h3>
                                                <div class="docpreview" >
                                                    <iframe src='"""+str(doc.uploadfile.url)+"""'  style="height: 100vh; width: 100%;"></iframe>
                                                </div>
                            </div>"""
            else:
                reviewhtml += """

                                <iframe src='"""+str(doc.uploadfile.url)+"""'style="height: 100%; width: 45%;" class='nutriiframe' onload="addnutriclass();"></iframe><br>
                                <div class='nutrisubmit'>
                                    <input type="submit" type="submit" name='review' id='review' value="Submit Review"/>
                                </div>"""



            prev = request.META.get('HTTP_REFERER')

            return render(
                request,
                'access/ingredient/document_verification.html',
                {
                    'message':"Document Review",
                    # 'documents':d,
                    'review': reviewhtml,
                    'doc':doc,
                    'page_title':pagetitle,
                    'previous':prev,
                    'admin':admin,
                    'ingredients':Ingredient.objects.all(),
                }
            )

    else:
        # list all RMs without docs bought in last three years
        supplier_specific = ['COI','form40', 'form20', 'form20ar', 'form20c']
        f20 = ['form20', 'form20ar', 'form20c']
        # unverifieddocs = {}
        three_years_ago = date.today() - relativedelta(years=3)
        # rawmaterials bought in last three years that are not discontinued
        rms = PurchaseOrderLineItem.objects.filter(raw_material__discontinued=False, due_date__range=[three_years_ago, date.today()]).order_by().values_list('raw_material', flat=True).distinct()
        # d = [obj for obj in Documents.objects.exclude(rawmaterial=None).exclude(rawmaterial__discontinued=True) if obj.verified == False and not request.user.username in obj.get_verifiers]

        # count RMS without docs, exlude certain docs based on art_nati

        # dict, doctype points to array of number of [unverified, docs need for review, no documents] count
        # unverifieddocs[dt] = [unverified_count, review_count, no_docs.count(), doctype_label]
        unverifieddocs = OrderedDict([
            ('specsheet'        ,  [ 0, 0, 0  , 'Specsheet']),
            ('sds'              ,  [ 0, 0, 0  , 'SDS']),
            ('allergen'         ,  [ 0, 0, 0  , 'Allergen']),
            ('nutri'            ,  [ 0, 0, 0  , 'Nutri']),
            ('GMO'              ,  [ 0, 0, 0  , 'GMO']),
            ('GPVC'             ,  [ 0, 0, 0  , 'GMO Project Verified Certificate']),
            ('LOG'              ,  [ 0, 0, 0  , 'Letter Of Guarantee']),
            ('natural'          ,  [ 0, 0, 0  , 'Natural']),
            ('origin'           ,  [ 0, 0, 0  , 'Origin']),
            ('vegan'            ,  [ 0, 0, 0  , 'Vegan']),
            ('organic'          ,  [ 0, 0, 0  , 'Organic Compliance']),
            ('organic_cert'     ,  [ 0, 0, 0  , 'Organic Certified']),
            ('kosher'           ,  [ 0, 0, 0  , 'Kosher']),
            ('halal'            ,  [ 0, 0, 0  , 'Halal']),
            ('COA'              ,  [ 0, 0, 0  , 'Certificate of Analysis']),
            ('COI'              ,  [ 0, 0, 0  , 'Certificate of Insurance']),
            ('ingbreak'         ,  [ 0, 0, 0  , 'Ingredient Breakdown']),
            ('form20'           ,  [ 0, 0, 0  , 'Form #020']),
            ('form20ar'         ,  [ 0, 0, 0  , 'Form #020 Audit Report']),
            ('form20c'          ,  [ 0, 0, 0  , 'Form #020 Certification']),
            ('form40'           ,  [ 0, 0, 0  , 'Form #040']),
        ])


        # for r in rms:
        #     ing = Ingredient.objects.get(rawmaterialcode=r)
        #     for dt in docbytype:
        #         if not Documents.objects.filter(rawmaterial=ing, doctype=dt).exists():
        #              unverifieddocs[dt][2] += 1
        #         else:
        #             latest = Documents.objects.filter(rawmaterial=ing, doctype=dt).latest('expiration')
        #             if latest.dv_count < 2 and request.user.username not in latest.get_verifiers:
        #                 unverifieddocs[dt][0] += 1
        #             elif latest.dv_count == 2 and not latest.verified and request.user.username not in latest.get_verifiers:
        #                 unverifieddocs[dt][1] += 1
        # # for r in rms:
        # #     ing = Ingredient.objects.get(rawmaterialcode=r)
        #
        #
        curr_user_verified = Documents.objects.filter(verifications__verifier=request.user)
        # document ids that are verified
        doc_ids = Documents.objects.filter(verifications__final=True).values_list('id', flat=True).distinct()
        for dt in docbytype:
            # doc ids of documents that are not verified, latest of each doc by rawmaterial
            # docs = Documents.objects.filter(doctype=dt, rawmaterial__rawmaterialcode__in=rms).exclude(id__in =doc_ids).exclude(id__in=curr_user_verified).order_by('rawmaterial_id', '-expiration').distinct('rawmaterial')
            # COAs work a little differently. list ALL coa, not just latest
            if dt == "COA":
                uv = Documents.objects.annotate(num_dv=Count('verifications')).filter(num_dv__lte=1, doctype=dt,rawmaterial__rawmaterialcode__in=rms).exclude(id__in=curr_user_verified)
                review = Documents.objects.annotate(num_dv=Count('verifications')).filter(num_dv__gte=2, doctype=dt, rawmaterial__rawmaterialcode__in=rms).exclude(id__in=doc_ids).exclude(id__in=curr_user_verified)
            else:
                # documents distinct by rawmaterial, latest by expiration
                distinct_docs = Documents.objects.filter(rawmaterial__rawmaterialcode__in=rms, doctype=dt).order_by('rawmaterial_id', '-expiration').distinct('rawmaterial')
                uv = Documents.objects.annotate(num_dv=Count('verifications')).filter(num_dv__lte=1, doctype=dt,rawmaterial__rawmaterialcode__in=rms, id__in=distinct_docs).exclude(id__in=curr_user_verified)
                review = Documents.objects.annotate(num_dv=Count('verifications')).filter(num_dv__gte=2, doctype=dt, rawmaterial__rawmaterialcode__in=rms, id__in=distinct_docs).exclude(id__in=doc_ids).exclude(id__in=curr_user_verified)
                # rawmaterials that have been verified for this document type

            rms_w_docs = Documents.objects.filter(doctype=dt, rawmaterial__rawmaterialcode__in=rms).distinct('rawmaterial')

            unverifieddocs[dt][0] = uv.count()
            unverifieddocs[dt][1] = review.count()
            unverifieddocs[dt][2] = rms.count() - rms_w_docs.count()
        #
        #     # idk why i have this
        ingredients = Ingredient.objects.all().distinct("id")


        return render(
            request,
            'access/ingredient/document_verification.html',
            {
                'message':'',
                # 'documents':d,
                'unverified':unverifieddocs,
                'page_title':pagetitle,
                'ingredients':ingredients,
                'previous':prev,
                'admin':admin,
            }
        )

def RMS_PurchasedLastThreeYears():
    three_years_ago = date.today() - relativedelta(years=3)
    # rawmaterials bought in last three years that are not discontinued
    rms = PurchaseOrderLineItem.objects.filter(raw_material__discontinued=False, due_date__range=[three_years_ago, date.today()]).exclude(raw_material__supplier__suppliercode='FDI').order_by().values_list('raw_material', flat=True).distinct()
    return rms

def rep_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def mass_upload(request):
    multiplesupps = {}
    success = []
    multiples = []
    name_err = []
    doctype =''
    # request get for pin numbers with multiple suppliers

    pending = Documents.objects.filter(rawmaterial=None)
    pendingdocs = {}
    for p in pending:
        f = File(open(p.uploadfile.path))
        f.name = os.path.basename(f.name)
        temp = f.name.split('_')
        i = Ingredient.objects.filter(id=int(temp[0]))
        pendingdocs[p] = i



    if request.method == "POST":
        docbytype = [
            'origin',
            'specsheet',
            'gmo',
            'gpvc',
            'log',
            'sds',
            'kosher',
            'form20',
            'form20ar',
            'form20c',
            'halal',
            'allergen',
            'nutri',
            'coi',
            'organic',
            'vegan',
            'natural',
            'form40',
            'coa',
            'ingbreak',
        ]

        # Country of Origin       = coo
        # specsheet               = spec
        # GMO                     = GMO
        # GMO Certification       = GMOCERT
        # Letter of Guarantee     = LOG
        # SDS                     = SDS
        # Kosher                  = kosher
        # Form20                  = form20
        # Form20-Audit Report     = form20ar
        # Form20 Certificate      = form20c
        # Halal                   = Halal
        # Allergen                = Allergen
        # Nutri                   = Nutri
        # Cerificate of Insurance = COI
        # Organic Compliance      = oc
        # Vegan                   = vegan
        # Natural                 = nat
        # Form40                  = form40
        # Cerificate of Analysis  = COA
        # Ingredient Breakdown    = ingbreak
        dtod = {
            'coo':'origin',
            'spec':'specsheet',
            'gmo':'GMO',
            'gmocert':'GPVC',
            'log':'LOG',
            'sds':'sds',
            'kosher':'kosher',
            'form20':'form20',
            'form20ar':'form20ar',
            'form20c':'form20c',
            'halal':'halal',
            'allergen':'allergen',
            'nutri':'nutri',
            'coi':'COI',
            'oc':'organic',
            'vegan':'vegan',
            'nat':'natural',
            'form40':'form40',
            'coa':'COA',
            'ingbreak':'ingbreak',

        }

        temps = []

        if 'massupload' in request.POST:

            for f in request.FILES.getlist('doc'):
                # filename = open(f.path)
                docinfo = f.name[0:-4].split('_')

                if(rep_int(docinfo[0]) and Ingredient.objects.filter(id=int(docinfo[0])).exists()):
                    # doctype = docinfo[1].lower()
                    i = Ingredient.objects.filter(id=int(docinfo[0]))
                    # if document of that name already exists
                    if Documents.objects.filter(uploadfile__icontains="/"+f.name).exclude(uploadfile__icontains="/Temp").exists():
                        name_err.append(f.name)
                    elif(len(i) > 1):
                        multiples.append(f.name)
                        # multiplesupps[f] = i
                        t = Documents(uploader=request.user, uploadfile=f)
                        t.save()
                        multiplesupps[t] = i

                    elif len(docinfo[1:]) > 1:
                        tempf = File(f)
                        validtag = False
                        for dt in docinfo[1:]:
                            if dt.lower() in list(dtod.keys()):
                                d = Documents(rawmaterial=i[0], doctype=dtod[dt.lower()], uploader=request.user, uploadfile=tempf)
                                # d.save()
                                # instead of saving, attach to temps array and save location_entry
                                temps.append(d)
                                validtag = True

                        if not validtag:
                            name_err.append(f.name)
                        else:
                            success.append(f.name)

                    else:
                        d = Documents(rawmaterial=i[0], doctype=dtod[docinfo[1].lower()], uploader=request.user, uploadfile=f)
                        # d.save()
                        # instead of saving, attach to temps array and save location_entry
                        temps.append(d)
                        success.append(f.name)


                else:
                    name_err.append(f.name)

            # save all appeded saves here if the loop can go through all files
            if temps:
                for t in temps:
                    t.save()
            if multiplesupps:
                return render(
                    request,
                    'access/ingredient/mass_upload.html',
                    {
                        # 'files':request.FILES.getlist("doc"),
                        # 'file_list':files,
                        # 'pending':pendingdocs,
                        'success':success,
                        'multiples':multiples,
                        'multiplesupps':multiplesupps,
                        'doctype':doctype,
                        'misnamed':name_err,
                    }
                )

# how to get doctype???
        elif 'choosesupplier' in request.POST or 'pending' in request.POST:
            # dt = request.POST.get('doctype')
            # blankdocs = Documents.objects.filter(uploader=request.user, rawmaterial=None)
            for c in request.POST.getlist('supplist'):
                if c == 'idk':
                    continue
                spl = c.split("__")
                filename = spl[1]
                i = Ingredient.objects.get(rawmaterialcode = int(spl[0]))

                # if len(blankdoc) > 1:
                blankdoc = Documents.objects.filter(uploadfile__icontains="/"+filename, rawmaterial=None).filter(uploadfile__icontains='Temp')
                assignfile = File(open(blankdoc[0].uploadfile.path))
                assignfile.name = os.path.basename(assignfile.name)
                blankdoc.delete()
                # os.rename(assignfile.name, os.path.basename(assignfile.name))
                if i and assignfile:
                    dtypes = filename[0:-4].split("_")
                    dtypes.pop(0)
                    for dt in dtypes:
                        try:
                            # blankdoc = Documents.objects.filter(uploadfile__icontains=filename, rawmaterial=None, uploader=request.user).filter(uploadfile__icontains='Temp')
                            # blankdoc.update(rawmaterial = i, doctype=dtod[dt], uploadfile= assignfile)
                            d = Documents(rawmaterial = i, doctype=dtod[dt.lower()], uploadfile= assignfile, uploader=request.user)
                            d.save()
                            blankdoc.delete()
                        except:
                            continue

                else:
                    return render(
                        request,
                        'access/ingredient/mass_upload.html',
                        {
                            'message':"no ingredient",
                            # 'files':request.POST.getlist('supplist'),
                            # # 'file_list':files,
                        #     'success':request.POST.getlist('supplist'),
                        #     'multiples':blankdocs,
                        #     # 'multiplesupps':multiplesupps,
                        #     'misnamed':dt,
                        }
                    )

            return render(
                request,
                'access/ingredient/mass_upload.html',
                {
                    # 'files':request.POST.getlist('supplist'),
                    # # 'file_list':files,
                    'success':request.POST.getlist('supplist'),
                    # 'pending':pendingdocs,
                    # 'multiples':blankdocs,
                    # 'multiplesupps':multiplesupps,
                    # 'misnamed':dt,
                }
            )



    return render(
        request,
        'access/ingredient/mass_upload.html',
        {
            'files':request.FILES.getlist("doc"),
            # 'file_list':files,
            'success':success,
            'multiples':multiples,
            'multiplesupps':multiplesupps,
            'misnamed':name_err,
            'pending':pendingdocs,
        }
    )


def flavor_copier(request):
    page_title = "Mariana's Flavor tool. Don't touch unless you're Mariana!"
    alist = ['flashpoint', 'color', 'organoleptics', 'spg']
    if request.method == "POST":
        if 'copy' in request.POST:
        # post to copy/edit values into new flavor_review
            ofl = Flavor.objects.get(number = int(request.POST.get('onumber')))
            nfl = Flavor.objects.get(number = int(request.POST.get('nnumber')))
            for a in alist:
                # check if attribute was checked
                # if checked, copy attr to new flavor
                # else use value in textfield
                if request.POST.get(a):
                    setattr(nfl, a, getattr(ofl, a))
                elif request.POST.get(a+'text'):
                    if a == 'flashpoint' or a =='spg':
                        setattr(nfl, a, Decimal(request.POST.get(a+'text')))
                    else:
                        setattr(nfl, a, request.POST.get(a+'text'))

            with reversion.create_revision():
                nfl.save()
                reversion.set_comment("Flavor attribute copies: %s => %s" % (ofl, nfl))
                reversion.set_user(User.objects.get(username=request.user))

                # for fl in changed_flavor_list:
                #     fl.save()
                #
                # reversion.set_comment("RM Replacement: %s => %s" % (old_ingredient, new_ingredient))
                # reversion.set_user(User.objects.get(username='matta'))
                #         nfl.save()

            return render(
                request,
                'access/flavor/flavor_copier.html',
                {
                    'initial':True,
                    'flavors':Flavor.objects.all(),
                    'page_title':page_title,
                }

            )
        # two flavors were selected, return and set up view to copy and/or edit
        oflavor = Flavor.objects.get(number = int(request.POST.get('oflavor')))
        nflavor = Flavor.objects.get(number = int(request.POST.get('nflavor')))
        oflavor_list = [getattr(oflavor, 'flashpoint'),getattr(oflavor, 'color'),getattr(oflavor, 'organoleptics'),getattr(oflavor, 'spg')]
        nflavor_list = [getattr(nflavor, 'flashpoint'),getattr(nflavor, 'color'),getattr(nflavor, 'organoleptics'),getattr(nflavor, 'spg')]

        return render(
            request,
            'access/flavor/flavor_copier.html',
            {
                # 'initial':True,
                'flavors':Flavor.objects.all(),
                'oflavor':oflavor,
                'nflavor':nflavor,
                'olist':oflavor_list,
                'nlist':nflavor_list,
                'flist':list(zip(alist, oflavor_list, nflavor_list)),
                'page_title':page_title,

            }
        )

    return render(
        request,
        'access/flavor/flavor_copier.html',
        {
            'initial':True,
            'flavors':Flavor.objects.all(),
            'page_title':page_title,
        }

    )

@login_required
def training(request):
    page_title = 'Training Log'
    test_types = Training._meta.get_field('test_type').choices
    train = Training.objects.filter(tester= request.user)



    group = {
            'Production':['sensory'],
            'Lab':['facemask', 'fltv', 'fltdt' , 'osha'],
            'Sales':['sensory','facemask','fltv','fltdt' , 'osha'],
            'Customer Service':['facemask', 'fltv', 'fltdt' , 'osha'],
    }
    fs = [  'bacteria',
            'foodborne',
            'personalhygiene',
            'haccp',
            'sanitation',
            'time',
            'foreign',
            'cross',
            'allergens',
            'pest',
            'security'
        ]
    admin = [
            'facemask',
            'sensory',
            'firedrill',
            'fltdt'
        ]

    # filter tests based on user group
    t=unfinished_training_log(request.user, request.user.groups.all()[0].name)
    # for test in test_types:
    #     to = Training.objects.filter(tester=request.user, passed=True, test_type = test[0])
    #     # if test[0] in group[u.groups.all()[0].name]:
    #     #     continue
    #     if (not to.exists() or to[0].test_renewal > 0) and not test[0] in group[request.user.groups.all()[0].name]:
    #         t.append(test)
    # test_types = filter(lambda x: not x[0] in group[request.user.groups.all()[0].name] (not to.exists() or to[0].test_renewal > 0) , test_types)

    return render(
        request,
        'access/training/training.html',
        {
            'admin':admin,
            'fs':fs,
            'page_title':page_title,
            'types':t,
            # 'training':training,
        }
    )

def expiration_check(rdate, years):
    return (date.today() - date(rdate.year+years, rdate.month, rdate.day)).days

def unfinished_training_log(user, g):
    unfinished = []
    test_types = Training._meta.get_field('test_type').choices
    fs = [  'bacteria',
            'foodborne',
            'personalhygiene',
            'haccp',
            'sanitation',
            'time',
            'foreign',
            'cross',
            'allergens',
            'pest',
            'security'
        ]
    group = {
            'Production':(['sensory',],['colorblind','handbook', 'fltdt'],['facemask','ccp','osha'],['gbpp','wiki','hazcom','fooddefense', 'firedrill', 'fltv', 'wpsafety',]+fs,[]),
            'Lab':(['sensory','facemask','osha', 'fltv', 'fltdt',],['colorblind','handbook', 'sensory', ],['ccp',],['gbpp', 'wiki', 'hazcom', 'fooddefense', 'firedrill', 'wpsafey',]+fs,[]),
            'Customer Service':(['sensory', 'facemask', 'osha', 'fltv', 'fltdt'],['wiki', 'hazcom', 'colorblind','handbook', 'ccp',]+fs,[],['fooddefense', 'firedrill','wpsafety'],['gbpp']),
            'Sales':(['sensory', 'facemask', 'osha', 'firedrill', 'fltv', 'fltdt'],['gbpp', 'wiki', 'hazcom', 'colorblind', 'handbook', 'fooddefense','ccp', 'wpsafety',]+fs,[],[],[]),
    }
    exp = group[g]
    never = exp[0]
    once = exp[1]
    annual = exp[2]
    biennial = exp[3]
    quadrennial = exp[4]

    for t in test_types:
        if not t[0] in never:
            training = Training.objects.filter(tester=user, test_type=t[0])
            if not training.exists():
                unfinished.append(t)

            elif t[0] in annual and expiration_check(training[0].completion_date, 1) > 0:
                unfinished.append(t)
            elif t[0] in biennial and expiration_check(training[0].completion_date, 2) > 0:
                unfinished.append(t)
            elif t[0] in quadrennial and expiration_check(training[0].completion_date, 4) > 0:
                unfinished.append(t)

    return unfinished



def training_overview(request, username):
    page_title = "Employee Training Overview"
    test_types = Training._meta.get_field('test_type').choices
    group = {
            'Production':['sensory'],
            'Lab':['facemask', 'fltv', 'fltdt', 'osha'],
            'Sales':['sensory','facemask','fltv','fltdt' , 'osha', 'fireddrill'],
            'Customer Service':['facemask', 'fltv', 'fltdt' , 'osha'],
    }

    employees = []
    # if username:

    users = User.objects.filter(is_active=True).exclude(username='test').exclude(username='TEST').exclude(username='labtest').order_by('username')
    for u in users:
        # t = Training.objects.filter(tester=u, passed=True)
        # t = [ x for x in test_types if Training.objects.filter(tester=u, passed=True, test_type=x).exists() and Training.objects.get(tester=u, passed=True, test_type=x).test_renewal < 0]
        t = unfinished_training_log(u, u.groups.all()[0].name)
        # for test in test_types:
        #     to = Training.objects.filter(tester=u, passed=True, test_type = test[0])
        #     # if test[0] in group[u.groups.all()[0].name]:
        #     #     continue
        #     if (not to.exists() or to[0].test_renewal > 0) and not test[0] in group[u.groups.all()[0].name]:
        #         t.append(test)
        #     # else:
        #     #     t.append()
        e = (u, t, u.groups.all()[0])
        employees.append(e)


    return render(
        request,
        'access/training/training_overview.html',
        {
            'page_title':page_title,
            'types':test_types,
            'employees':employees,

        }
    )
def admin_individual_training(request):
        page_title = 'Individual Training'
        users = User.objects.filter(is_active=True).exclude(username='test').exclude(username='TEST').exclude(username='labtest').order_by('username')
        tests = Training._meta.get_field('test_type').choices
        if request.method == 'POST':
            testtype = request.POST.getlist('test')
            dates = request.POST.getlist('cdate')
            tester = request.POST.get('user')
            tester = User.objects.get(username=tester)
            for t, c in zip(testtype, dates):
                # u = User.objects.get(username=t)
                if Training.objects.filter(tester=tester, test_type=t).exists():
                    training = Training.objects.get(tester=tester, test_type=t)
                    training.completion_date = c
                    training.save()
                else:
                    training = Training(test_type=t, tester=tester, passed=True, completion_date=c)
                    training.save()
            return render(
                request,
                'access/training/admin_individual_training.html',
                {
                    'page_title':page_title,
                    'users':users,
                    'post':request.POST,
                    'tests':tests,
                }
            )
        return render(
            request,
            'access/training/admin_individual_training.html',
            {
                'page_title':page_title,
                'users':users,
                'tests':tests,
            }
        )

def admin_certification(request):
    page_title = 'Admin Training Certification '
    users = User.objects.filter(is_active=True).exclude(username='test').exclude(username='TEST').exclude(username='labtest').order_by('username')

    if request.method == 'POST':
        testtype = request.POST.get('test')
        testers = request.POST.getlist('user')
        for t in testers:
            u = User.objects.get(username=t)
            if Training.objects.filter(tester=u, test_type=testtype).exists():
                training = Training.objects.get(tester=u, test_type=testtype)
                training.completion_date = date.today()
                training.save()
            else:
                training = Training(test_type=testtype, tester=u, passed=True)
                training.save()
        return render(
            request,
            'access/training/admin_certification.html',
            {
                'page_title':page_title,
                'users':users,
                'post':request.POST,
            }
        )
    return render(
        request,
        'access/training/admin_certification.html',
        {
            'page_title':page_title,
            'users':users,
        }
    )


def glass_and_brittle(request):
    page_title='Glass Policy Agreement #050 ver2016'
    # might be useless
    if request.POST.get('username') == request.user.username and request.user.check_password(request.POST.get('pw')):
    # save training object
        if Training.objects.filter(test_type='gbpp', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='gbpp', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='gbpp', completion_date=date.today(), tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
    if not request.POST.get('signature'):

        return render(
            request,
            'access/training/glass_and_brittle.html',
            {
                'error':'Not signed',
                'page_title':page_title,
            }
        )

    return render(
        request,
        'access/training/glass_and_brittle.html',
        {
            'page_title':page_title,
        }

    )
# basically the same as glass/brittle
def osha_lockout(request):
    page_title = 'Lockout Tagout OSHA Policy #059 ver2016'
    if request.POST.get('username') == request.user.username and request.user.check_password(request.POST.get('pw')):
    # save training object
        if Training.objects.filter(test_type='osha', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='osha', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='osha', completion_date=date.today(), tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
    if not request.POST.get('signature'):

        return render(
            request,
            'access/training/osha.html',
            {
                'error':'Not signed',
                'page_title':page_title,
            }
        )
    return render(
        request,
        'access/training/osha.html',
        {
            'page_title':page_title,
        }

    )

def check_answers(test, answers):
    check = {
        'wiki_review':['manager', 'police', 'manager', 'true', 'true', 'true', 'true'],
        'colorblind':['29','73', '45', '7', '26', '15', '16', '8', '5'],
        'wpsafety':['b','d','c','true','b','c','d','b','a','c','b','a','b','true', 'b', 'c', 'c', 'd', 'b', 'd', 'c'],
        'fooddefense':['d', 'c', 'b', 'true', 'true'],
        'hazcom':[],
        'ccp':[],
        'fltv':['false', 'true', 'true', 'true', 'false', 'false','false','false','false','false', 'true', 'true', 'false','false','true','false','true','true','false'],

        # foodsafety answers
        'bacteria':['a','d', 'd','c','b', 'a','d','b', 'd','d'],
        'foodborne':['c','b','d','d','d','d','d','d','d','d'],
        'personalhygiene':['a','c','d','b','d','b','b','d','c','b'],
        'haccp':['a','b','d','c','c','b','a','b','b','d'],
        'sanitation':['c','d','b','a','c','d','d','b','d','a'],
        'time':['c','d','d','b','d','d','c','b','d','a'],
        'foreign':['b','a','d','d','d','a','d','b','c','d'],
        'cross':['b','d','b','d','d','d','a','d','b','d'],
        'allergens':['b','d','d','c','d','d','d','c','d','a'],
        'pest':['d','a','d','b','d','d','d','c','d','b'],
        'security':['d','d','d','b','d','d','d','b','d','d'],
    }

    food_safety_tests = ['bacteria', 'foodborne', 'personalhygiene', 'haccp','sanitation', 'time', 'foreign', 'cross', 'allergens', 'pest', 'security']


    total = len(check[test])
    count = 0

    for a, b in zip(answers, check[test]):
        # if not a.lower() == b:
            # return False
        if a.lower() == b:
            count += 1

    if (Decimal(count)/Decimal(total)) >= .7:
        return True

    return False

# var_to_trainingq = {
#         # 'gbpp':gbpp,
#
#
#         # food_safety
#         'bacteria':bacteria,
#         'foodborne':foodborne,
#         'personalhygiene':personalhygiene,
#         'haccp':haccp,
#         'sanitation':sanitation,
#         'time':time,
#         'foreign':foreign,
#         'cross':cross,
#         'allergens':allergens,
#         'pest':pest,
#         'security':security,
#
#
# }
section_dict = {
    'wiki':wiki,
    # 'colorblind':colorblind,
    # 'hazcom':hazcom,
    # 'fooddefense':fooddefense,
    # 'ccp':ccp,
    # 'fltv':fltv,

    'bacteria':bacteria,
    'foodborne':foodborne,
    'personalhygiene':personalhygiene,
    'haccp':haccp,
    'sanitation':sanitation,
    'time':time,
    'foreign':foreign,
    'cross':cross,
    'allergens':allergens,
    'pest':pest,
    'security':security,
    'bacteria_sp':bacteria_sp,
    'foodborne_sp':foodborne_sp,
    'personalhygiene_sp':personalhygiene_sp,
    'haccp_sp':haccp_sp,
    'sanitation_sp':sanitation_sp,
    'time_sp':time_sp,
    'foreign_sp':foreign_sp,
    'cross_sp':cross_sp,
    'allergens_sp':allergens_sp,
    'pest_sp':pest_sp,
    'security_sp':security_sp

}

def get_training_answers(request, section):
    answers = []
    questions = section_dict[section]
    for key in range(len(questions)):
        answers.append(request.POST.get(section+str(key)))

    return answers


def save_question_response(training_obj, answers):
    questions = section_dict[training_obj.test_type]
    if Question.objects.filter(training__tester=training_obj.tester, training__test_type = training_obj.test_type).exists():
        Question.objects.filter(training__tester=training_obj.tester, training__test_type = training_obj.test_type).delete()
    for a, b in zip(answers, questions):
        # pass
        if len(b[1]) > 1:
            q = Question(question=b[0], answer = b[1][a], training = training_obj)
        else:
            q = Question(question=b[0], answer = a, training = training_obj)

        q.save()
    # save question and response
    # how am i gonna do this for the foodsafety?!?!?

def wiki_review(request):
    page_title = 'Wiki Review'

    questions = section_dict['wiki']
    if request.method == 'POST':
    # submit Questions

        answers = get_training_answers(request, 'wiki')
        if check_answers('wiki_review', answers):
            # return redirect('/access/')

            if Training.objects.filter(test_type='wiki', tester=request.user, passed=True).exists():
                t = Training.objects.get(test_type='wiki', tester=request.user, passed=True)
                t.completion_date = date.today()
                t.save()
            else:
                t = Training(test_type='wiki', completion_date=date.today(), tester=request.user, passed=True)
                t.save()

            save_question_response(t, answers)
            return redirect('/access/training/')

        # correct submission
        # if Training.objects.filter(test_type='wiki', tester=request.user, passed=True).exists():
        #     t = Training.objects.get(test_type='wiki', tester=request.user, passed=True)
        #     t.completion_date = date.today()
        #     t.save()
        # else:
        #     t = Training(test_type='wiki', completion_date=date.today(), tester=request.user, passed=True)
        #     t.save()
        #


        else:
            return render(
                request,
                'access/training/wikireview.html',
                {
                    'page_title':page_title,
                    'questions':questions,
                    'section':'wiki',
                    'alert':'Did not answer enough correctly. Try again.',
                }
            )
        # if wiki1.lower() == 'manager':

    return render(
        request,
        'access/training/wikireview.html',
        {
            'page_title':page_title,
            'questions':questions,
            'section':'wiki'
        }
    )



def food_safety(request, section):

    page_title = 'Employee Food Safety Handbook 3rd Edition Quiz'
    fs = [
            ('Bacteria Review', 'bacteria'),
            ('Foodborne Illness Review', 'foodborne'),
            ('Personal Hygiene Review', 'personalhygiene'),
            ('HACCP Review', 'haccp'),
            ('Sanitation Review', 'sanitation'),
            ('Time and Temperature Controls Review', 'time'),
            ('Foreign Material Detection Review', 'foreign'),
            ('Cross Contamination Review', 'cross'),
            ('Allergens Review', 'allergens'),
            ('Pest Control Review', 'pest'),
            ('Security Review', 'security')
        ]

    # section_dict = {
    #     'bacteria':bacteria,
    #     'foodborne':foodborne,
    #     'personalhygiene':personalhygiene,
    #     'haccp':haccp,
    #     'sanitation':sanitation,
    #     'time':time,
    #     'foreign':foreign,
    #     'cross':cross,
    #     'allergens':allergens,
    #     'pest':pest,
    #     'security':security,
    #     'bacteria_sp':bacteria_sp,
    #     'foodborne_sp':foodborne_sp,
    #     'personalhygiene_sp':personalhygiene_sp,
    #     'haccp_sp':haccp_sp,
    #     'sanitation_sp':sanitation_sp,
    #     'time_sp':time_sp,
    #     'foreign_sp':foreign_sp,
    #     'cross_sp':cross_sp,
    #     'allergens_sp':allergens_sp,
    #     'pest_sp':pest_sp,
    #     'security_sp':security_sp
    #
    # }
    # arr = []
    # for key in request.POST:
    #     arr.insert(0,request.POST[key])
    section_pdf = {
        'bacteria':'<iframe src="https://drive.google.com/file/d/10-fWm9VsKMhNlaY81_epTHsImF8EnF1y/preview" width="1099.5" height="749"></iframe>',
        'foodborne':'<iframe src="https://drive.google.com/file/d/1X7z8IirWvtJQ7emcpuYGdkA-JvfsNF2y/preview" width="1099.5" height="749"></iframe>',
        'personalhygiene':'<iframe src="https://drive.google.com/file/d/1tRlXPD52Dn2QHVYp22FGByT2Q_kgzE4J/preview" width="1099.5" height="749"></iframe>',
        'haccp':'<iframe src="https://drive.google.com/file/d/1ZByJNdWASqnOya2viuACsvOZeko1sSrt/preview" width="1099.5" height="749"></iframe>',
        'sanitation':'<iframe src="https://drive.google.com/file/d/1nit_JUUprod7DFuMVQD20gmDQR_UHJyu/preview" width="1099.5" height="749"></iframe>',
        'time':'<iframe src="https://drive.google.com/file/d/1rbtcfoTWzdUBt3q5k97oETSf9ooL2fJB/preview" width="1099.5" height="749"></iframe>',
        'foreign':'<iframe src="https://drive.google.com/file/d/1k7y9L7XGofUHKGSIjmXPP8US3tRFhVhq/preview" width="1099.5" height="749"></iframe>',
        'cross':'<iframe src="https://drive.google.com/file/d/1x6G4P-ZTqVkvF8_JSdc1qcqfSDXVp7bg/preview" width="1099.5" height="749"></iframe>',
        'allergens':'<iframe src="https://drive.google.com/file/d/11QTVHybfvVFreAWfx0V30o0bwtVV45di/preview" width="1099.5" height="749"></iframe>',
        'pest':'<iframe src="https://drive.google.com/file/d/11yTyf9CHj9xsS6N2ssIou18hR6IKKXZz/preview" width="1099.5" height="749"></iframe>',
        'security':'<iframe src="https://drive.google.com/file/d/11XnI_AzyaB07gu4eWhgJiQ64Ylhkl0sx/preview" width="1099.5" height="749"></iframe>',
        'bacteria_sp':'<iframe src="https://drive.google.com/file/d/1aDJ6l5GIKTSI-89p2JW41BYhvnDMtYEk/preview" width="1099.5" height="749"></iframe>',
        'foodborne_sp':'<iframe src="https://drive.google.com/file/d/1h2MUmJsWWn5-LOdDzpXrUhd3OBMnwchk/preview" width="1099.5" height="749"></iframe>',
        'personalhygiene_sp':'<iframe src="https://drive.google.com/file/d/1gouApSKF2DU7MzntWZSqk44Rkzk1Zajd/preview" width="1099.5" height="749"></iframe>',
        'haccp_sp':'<iframe src="https://drive.google.com/file/d/1NmtUsJEF-YiRUPnhUHHKjzvHimZU6s26/preview" width="1099.5" height="749"></iframe>',
        'sanitation_sp':'<iframe src="https://drive.google.com/file/d/17rJXtRo12ai1MDm-iozwaZPkTykKQNp-/preview" width="1099.5" height="749"></iframe>',
        'time_sp':'<iframe src="https://drive.google.com/file/d/1H3zX0ZI8PpvX6FdwH1bJly1MKLOgq15i/preview" width="1099.5" height="749"></iframe>',
        'foreign_sp':'<iframe src="https://drive.google.com/file/d/1eRBCsFVv7LxOgoOZ8vzB7S6VD0lNVhGP/preview" width="1099.5" height="749"></iframe>',
        'cross_sp':'<iframe src="https://drive.google.com/file/d/1vBRf7C1JZyAALvMJuCWIRwDpCoScnGWi/preview" width="1099.5" height="749"></iframe>',
        'allergens_sp':'<iframe src="https://drive.google.com/file/d/17sa9_akzuIwtUjteuoEIxQR5nD_Z1PXd/preview" width="1099.5" height="749"></iframe>',
        'pest_sp':'<iframe src="https://drive.google.com/file/d/1MS0YCd-NZipWVsq-iw181d7z_6c_YxC-/preview" width="1099.5" height="749"></iframe>',
        'security_sp':'<iframe src="https://drive.google.com/file/d/1ZSCJCk_4hjNps8EXCknjwvBdv3Q5G83Z/preview" width="1099.5" height="749"></iframe>'
    }
    if section:
        questions = section_dict[section]
        if request.method == 'POST':
            # answers = request.POST.getlist(section)
            answers = []
            for key in range(len(questions)):
                answers.append(request.POST.get(section+str(key)))
            if check_answers(section, answers):
                if Training.objects.filter(test_type=section, tester=request.user, passed=True).exists():
                    t = Training.objects.get(test_type=section, tester=request.user, passed=True)
                    t.completion_date = date.today()
                    t.save()
                else:
                    t = Training(test_type=section, tester=request.user,  passed=True)
                    t.save()

                save_question_response(t , answers)
                return redirect('/access/training/')
            else:
                # return redirect('/access/food_safety/'+section)
                return render(
                    request,
                    'access/training/food_safety.html',
                    {
                        'pdf':section_pdf[section],
                        'section':section,
                        'alert':'Did not answer enough correctly. Try again.',
                        'questions':questions,
                        'page_title':page_title,
                    }
                )


        return render(
            request,
            'access/training/food_safety.html',
            {
                'pdf':section_pdf[section],
                'section':section,
                'questions':questions,
                'page_title':page_title,
            }
        )

    return render(
        request,
        'access/training/food_safety.html',
        {
            # 'current':section,
            'sections':fs,
            'page_title':page_title,
        }
    )



def hazcom(request):
    page_title='Hazcom 2012'
    if request.method == 'POST':
        if Training.objects.filter(test_type='hazcom', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='hazcom', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='hazcom', tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
    return render(
        request,
        'access/training/hazcom.html',
        {
            'page_title':page_title,
        }
    )



def employee_handbook(request):
    page_title='Employee Handbook Confimation'
    # might be useless
    if request.POST.get('username') == request.user.username and request.user.check_password(request.POST.get('pw')):
    # save training object
        if Training.objects.filter(test_type='handbook', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='handbook', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='handbook', completion_date=date.today(), tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
    if not request.POST.get('signature'):

        return render(
            request,
            'access/training/employee_handbook.html',
            {
                'error':'Not signed',
                'page_title':page_title,
            }
        )


    return render(
        request,
        'access/training/employee_handbook.html',
        {
            'page_title':page_title,
        }

    )
def color_blind(request):
    page_title = 'Color Blind Test #024 ver2015'
    arr = ''
    if request.method =='POST':

        # answers = request.POST.getlist('cb_answer')
        # # for a in answers:
        # #     arr.append(a)
        if check_answers('colorblind', request.POST.getlist('cb_answer')):
            if Training.objects.filter(test_type='colorblind', tester=request.user, passed=True).exists():
                t = Training.objects.get(test_type='colorblind', tester=request.user, passed=True)
                t.completion_date = date.today()
                t.save()
            else:
                t = Training(test_type='colorblind', tester=request.user, passed=True)
                t.save()
            return redirect('/access/training/')
        else:
            arr = 'Incorrect answers. Try again.'
        # return render(
        #     request,
        #     'access/training/colorblindtest.html',
        #     {
        #         # 'answers':arr,
        #         'page_title':page_title,
        #     }
        # )

    return render(
        request,
        'access/training/colorblindtest.html',
        {
            'answers':arr,
            'page_title':page_title,
        }
    )
def food_defense(request):
    page_title = 'Food Defense Plan Training #061 ver2016'
    arr = []
    if request.method == "POST":
        responses = request.POST.getlist('fd_response')
        questions = [
                        'What types of suspicious activity should be reported to your supervisor?',
                        'What steps would we use to approve a new supplier?',
                        'Where can a trucker go?',
                        'Where can a contractor go?',
                        'What types of suspicious activity should be reported to your supervisor?What steps would we use to approve a new supplier? Where can a trucker go? Where can a contractor go? What would you do it you have an unfinished batch and it is time to go for the day?',
                    ]
        if Training.objects.filter(test_type='fooddefense', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='fooddefense', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='fooddefense', tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
        # for q, r in zip(questions,responses):
        #     qo = Question(question=q, answer=r,training=t)
        #     qo.save()
        #     arr.append(q)
        #     arr.append(r)
    return render(
        request,
        'access/training/fooddefense.html',
        {
            'answers':arr,
            'page_title':page_title,
        }
    )


################################## NEED ANSWER CHECK (user dict to coordinate answers) #############################################
def ccp_allergen(request):
    page_title = "CCP and Allergen HACCP Questionnaire #060 ver2016"
    if request.method == 'POST':
        if Training.objects.filter(test_type='ccp', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='ccp', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
            t = Training(test_type='ccp', tester=request.user, passed=True)
            t.save()
        return redirect('/access/training/')
        arr = []
        for key in request.POST:
            arr.insert(0,request.POST[key])
        return render(
            request,
            'access/training/ccp_allergen.html',
            {
                'answers':arr,
                'page_title':page_title,
            }
        )
    return render(
        request,
        'access/training/ccp_allergen.html',
        {
            'page_title':page_title,
        }
    )


# def fork_lift(request):
def fork_lift_video(request):
    page_title = 'Fork Lift Quiz'


    if request.method == 'POST':
        if Training.objects.filter(test_type='fltv', tester=request.user, passed=True).exists():
            t = Training.objects.get(test_type='fltv', tester=request.user, passed=True)
            t.completion_date = date.today()
            t.save()
        else:
             t = Training(test_type='fltv', tester=request.user, passed=True)
             t.save()
        return redirect('/access/training/')

    if request.GET.get('spanish'):
            return render(
                request,
                'access/training/fltcert.html',
                {
                    'questions':fltc_sp,
                    'page_title':page_title,
                }
            )

    return render(
        request,
        'access/training/fltcert.html',
        {
            'questions':fltc,
            'page_title':page_title,
        }
    )
def workplace_safety(request):
    page_title="Workplace Safety Quiz"

    if request.method == 'POST':

            if Training.objects.filter(test_type='wpsafety', tester=request.user, passed=True).exists():
                t = Training.objects.get(test_type='wpsafety', tester=request.user, passed=True)
                t.completion_date = date.today()
                t.save()
            else:
                 t = Training(test_type='wpsafety', tester=request.user, passed=True)
                 t.save()
            return redirect('/access/training/')

    return render(
        request,
        'access/training/workplace_safety.html',
        {
            'questions':wps,
            'questions2':wps2,
            'page_title':page_title,
        }
    )

def docreview_comparison(request, document_id):
    doc = Documents.objects.get(id=document_id)
    dv  = DocumentVerification.objects.filter(document=doc)
    temp_ing_dict = list(dv[0].temp_ingredient.__dict__.keys())
    temp_nutri_dict = list(dv[0].temp_nutri.__dict__.keys())


    temp_ing_dict.remove('_state')
    temp_ing_dict.remove('id')
    temp_ing_dict.remove('temp_rmcode')

    # list verifiers in top row
    table = "<h1>"+doc.doctype+"</h1><br><table><tr><td></td>"
    for d in dv:
        if d.final:
            table += "<td>"+d.verifier.username+" - FINAL </td>"
        else:
            table += "<td>"+d.verifier.username+"</td>"
    table += "<td>"+str(doc.rawmaterial)+"</td></tr>"


    if doc.doctype == "nutri":
        for t in temp_nutri_dict:
            table += "<tr><td>"+t+"</td>"
            for d in dv:
                table += "<td>"+str(getattr(d.temp_nutri, t))+"</td>"

            if not t=='user_id':
                table+="<td>"+str(doc.rawmaterial.__dict__[t])+"</td></tr>"
            else:
                table+="<td>n/a</td></tr>"


    else:
        for t in temp_ing_dict:
            table += "<tr><td>"+t+"</td>"
            for d in dv:
                table += "<td>"+str(getattr(d.temp_ingredient, t))+"</td>"

            if not t=='user_id':
                table+="<td>"+str(doc.rawmaterial.__dict__[t])+"</td></tr>"
            else:
                table+="<td>n/a</td></tr>"

    table+="</table>"

    return render(
        request,
        'access/ingredient/document_comparison.html',
        {
            'comparison':table,
        }
    )


# ss = SpecSheetInfo.objects.filter(one_off_customer=None, flavor__phase="Liquid")
#
# for s in ss:
#     setattr(s, 'aerobic_plate_count', '<10,000 gm')
#     setattr(s, 'escherichia_coli', '<10/gm')
#     setattr(s, 'salmonella', 'Negative/375gm')
#     setattr(s, 'yeast', '<100/gm')
#     setattr(s, 'mold', '<100/gm')
#     setattr(s, 'coliforms', '<100/gm')
#     setattr(s, 'listeria', 'Negative/25g')
#     s.save()


def test_api_view(request):
    return render(
        request,
        'access/flavor/test.html',
        {

        }
    )

# @FlavorView(['GET', 'POST', 'PUT'])
class FlavorView(viewsets.ModelViewSet):
    queryset = Flavor.objects.all()
    serializer_class = FlavorSerializer
