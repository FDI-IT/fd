import datetime
from datetime import date
from decimal import Decimal
import re

from django.shortcuts import render, get_object_or_404
import json
from django.views.generic.list import ListView
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.functional import wraps
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.db import connection
from django.db.models import Count, Sum, Avg
from django.db.models.query import EmptyQuerySet
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import permission_required

from access.views import SubListView
from access.models import Flavor, FormulaTree, ExperimentalLog, Formula

from pluggable.parseintset import parseIntSet 

from reports import forms
from reports import controller

# decorator
def date_range_wrapper(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        if 'date_start' in request.GET:
            date_range_form = forms.DateRangeForm(request.GET)
            if date_range_form.is_valid():
                date_range_form.date_start = date_range_form.cleaned_data['date_start']
                date_range_form.date_end = date_range_form.cleaned_data['date_end']
                request.session['date_start'] = date_range_form.date_start
                request.session['date_end'] = date_range_form.date_end
            else:
                date_range_form = forms.DateRangeForm()
                date_range_form.date_start = date_range_form.fields['date_start'].initial
                date_range_form.date_end = date_range_form.fields['date_end'].initial
        else:
            date_range_form = forms.DateRangeForm()
            date_range_form.date_start = date_range_form.fields['date_start'].initial
            date_range_form.date_end = date_range_form.fields['date_end'].initial
        return view(request, date_range_form, *args, **kwargs)
    return inner

@date_range_wrapper
@permission_required('access.add_indivisibleleafweight')
def lots_by_person(request, date_range_form):
    lot_annotations = ExperimentalLog.objects.filter(datesent__gte=date_range_form.date_start).filter(datesent__lte=date_range_form.date_end).order_by('initials').values('initials').annotate(num_lots=Count('flavor__lot')).annotate(total_weight=Sum('flavor__lot__amount'))
    callable_view = SubListView.as_view(
              # paginate_by=100,
               queryset=lot_annotations,
               template_name='reports/lots_by_person.html',
               extra_context={
                   'page_title': 'Lots by Person',
                   'date_range_form':date_range_form,
               }                        
           )
    
    return callable_view
    
@date_range_wrapper
@permission_required('access.add_indivisibleleafweight')
def conversions_by_person(request, date_range_form):
    # process per initials
    intermediate_qs = ExperimentalLog.objects.filter(datesent__gte=date_range_form.date_start).filter(datesent__lte=date_range_form.date_end)
    object_list = []
    for i in ExperimentalLog.objects.order_by('initials').values_list('initials', flat=True).distinct():
        my_qs = intermediate_qs.filter(initials=i)
        my_values = {
                'initials':i,
                'num_conversions':0,
                'num_successful':0,
                
            }
        for x in my_qs:
            if x.flavor is not None:
                my_values['num_conversions'] += 1
                if x.flavor.lot_set.count() != 0:
                    my_values['num_successful'] += 1
        object_list.append(my_values)
        
    return render(
        request,
        'reports/conversions_by_person.html',
        {
            'object_list':object_list,
            'page_title': 'Conversions by Person',
            'date_range_form':date_range_form,
        },
    )
        
@permission_required('access.add_indivisibleleafweight')
def experimental_log_exclude(request):
    if 'epk' in request.POST and 'exclude_from_reporting' in request.POST:
        e = ExperimentalLog.objects.get(pk=request.POST['epk'])
        new_val = request.POST['exclude_from_reporting']
        controller.toggle_exclude_from_reporting(e, new_val)
        return HttpResponse(
                            json.dumps(['Success',])                    
                            )
        
def report_parse(report_path='/srv/samba/tank/Share folders by role/Quality Control/xx.csv'):
    import csv
    sales_report_file = open(report_path,'rb')
    csvreader = csv.reader(sales_report_file)
    
    header = csvreader.next()
    
    lines = []

    for x in csvreader:
        lines.append(x)
        
    import re
    my_re = re.compile('\d+')

    flavor_number_dict = {}
    for l in lines:
        try:
            my_match = my_re.match(l[0]).group()
        except:
            continue
        if my_match in flavor_number_dict:
            flavor_number_dict[my_match].append(l)
        else:
            flavor_number_dict[my_match] = [l,]
            
    summarized_flavor_dict = {}
    for flavor_number, flavor_lines in flavor_number_dict.iteritems():
        total=0
        for l in flavor_lines:
            total+= int(float(l[2]))
        
        if flavor_number in summarized_flavor_dict:
            summarized_flavor_dict[flavor_number]+= total
        else:
            summarized_flavor_dict[flavor_number] = total
            
    return summarized_flavor_dict

@permission_required('access.add_indivisibleleafweight')
def sales_by_person(request,):
    credit_ranges = {
            'NS':'180050-189999',
            'SC':'140361-149999',
            'DR':'120950-129999',
            'MM':'',     
            'SK':'',  
        }
    
    complete_credit_sets = {}
    credit_reverse_map = {}
    for initials, range_string in credit_ranges.iteritems():
        my_flavors = set()
        my_experimentals = ExperimentalLog.objects.filter(initials=initials).exclude(flavor=None)
        for my_e in my_experimentals:
            my_flavors.add(my_e.flavor)
        for f in Flavor.objects.filter(number__in=parseIntSet(range_string)):
            my_flavors.add(f)
        complete_credit_sets[initials] = my_flavors
        for f in my_flavors:
            credit_reverse_map[f] = initials
            
    for formula_line in Formula.objects.filter(amount=1000).exclude(ingredient__sub_flavor=None):
        my_sub_flavor = formula_line.ingredient.sub_flavor
        if my_sub_flavor in credit_reverse_map:
            my_initials = credit_reverse_map[my_sub_flavor]
            complete_credit_sets[my_initials].add(formula_line.flavor)
            credit_reverse_map[formula_line.flavor] = my_initials
                    
    partial_credit_sets = {}
    for initials, flavors in complete_credit_sets.iteritems():
        partial_flavors = set()
        for f in flavors:
            for ft in FormulaTree.objects.filter(node_flavor=f).exclude(root_flavor=f):
                partial_flavors.add(ft.root_flavor)
        partial_credit_sets[initials] = partial_flavors
  
    summarized_flavor_dict = report_parse()
    sales_per_flavor = {} 
    for flavor_number, total in summarized_flavor_dict.iteritems():
        try:
            flavor = Flavor.objects.get(number=flavor_number)
            sales_per_flavor[flavor_number] = (total, credit_reverse_map[flavor])
        except:
            sales_per_flavor[flavor_number] = (total, "UNK")

    partial_sales_per_person = {}
    for initials, partial_flavors in partial_credit_sets.iteritems():
        my_partial_sales = {}
        for f in partial_flavors:
            k = str(f.number)
            if k in sales_per_flavor:
                if sales_per_flavor[k][1] != initials:
                    my_partial_sales[f] = sales_per_flavor[k][0]
        partial_sales_per_person[initials] = my_partial_sales
        
    partial_totals = {}
    for initials, partial_sales in partial_sales_per_person.iteritems():
        total = 0
        for ps in partial_sales.values():
            total += ps
        partial_totals[initials] = total
            
    sales_per_person = {}
    for flavor_number, details in sales_per_flavor.iteritems():
        total, initials = details
        if initials in sales_per_person:
            sales_per_person[initials] += total
        else:
            sales_per_person[initials] = total
            
    sales_per_person_with_partials = {}
    for initials, partial_sales in partial_sales_per_person.iteritems():
        sales_per_person_with_partials[initials] = sales_per_person[initials] + partial_totals[initials]

    return render(
        request,
        'reports/sales_by_person.html',
        {
            'sales_per_flavor':sales_per_flavor,
            'sales_per_person':sales_per_person,
            'sales_per_person_with_partials':sales_per_person_with_partials,
            'partial_sales_per_person':partial_sales_per_person,
            'page_title': 'Sales by Person',
        },
    )

@date_range_wrapper
@permission_required('access.add_indivisibleleafweight')
def experimental_log(request, date_range_form):
    filterselect = forms.ExperimentalFilterSelectForm(request.GET)
    if filterselect.is_valid():
        string_kwargs = {}
        initials_filter = filterselect.cleaned_data['initials']
        if len(initials_filter) > 0:
            string_kwargs['initials__in'] = initials_filter
    els = ExperimentalLog.objects.filter(**string_kwargs).filter(datesent__gte=date_range_form.date_start).filter(datesent__lte=date_range_form.date_end)
    
    if els.count() > 0:
        for e in els:
            controller.annotate_experimental_log_object(e)
        
        aggregated_data = controller.collect_special_aggregates(els)    
    else:
        aggregated_data = {}  
    return render(
        request,
        'reports/experimental_log.html',
        {
            'experimental_logs':els,
            'page_title': 'Experimental Log',
            'date_range_form':date_range_form,
            'filterselect':filterselect,
            'aggregated_data':aggregated_data,
            #'date_range_form':date_range_form,
        },
    )

def lot_summary(request):
    """This page summarizes how many lot numbers a flavor has, and the total
    weight of those lots.
    """
    queryset = Flavor.objects.filter(valid=True).values('number').annotate(
                     lot_count=Count('lot')).annotate(
                     lot_amount_sum=Sum('lot__amount')).order_by(
                     '-lot_count').exclude(
                     lot_count=0)
    callable_view = SubListView.as_view(
              # paginate_by=100,
               queryset=queryset,
               template_name='reports/lot_summary.html',
               extra_context={
                   'page_title': 'Lot Summary',
               }                        
           )
    
    return callable_view(request)
    
def formula_usage_summary(request):
    """This page summarizes how many times a formula appears if you take the
    lot summary and blow it out. Every time a formula is used as a component
    in another formula, it's counted.
    """
    #date_range_form = forms.DateRangeForm()
    
    """Pseudocode:
    Get the lot summary.
    Get the formula trees queryset.
    component_summary = {}
    For each flavor in the lot summary:
        Get the formula tree of it
        For each component in the formula tree:
            component_summary[component] += lot_count
    """

    
    formula_trees = FormulaTree.objects.filter(
            root_flavor__in=recent_flavors_with_lots_by_pk()).exclude(
            lft=0).exclude(node_flavor=None)
    return render(
        request,
        'reports/formula_usage_summary.html',
        {
           'date_range_form':date_range_form,
        })
    
def recent_flavors_with_lots_by_pk():
    return set(Flavor.objects.filter(
                     valid=True).filter(lot__date__gt='2013-01-01').values_list(
                    'pk',flat=True).annotate(
                    lot_count=Count('lot')).exclude(
                    lot_count=0))
    
def formula_component_summary():
    component_summary = {}
    
    queryset = Flavor.objects.filter(valid=True).values('number').annotate(
                     lot_count=Count('lot')).annotate(
                     lot_amount_sum=Sum('lot__amount')).order_by(
                     '-lot_count').exclude(
                     lot_count=0)
                     
    formula_trees = FormulaTree.objects.filter(
            root_flavor__in=recent_flavors_with_lots_by_pk()).exclude(
            lft=0).exclude(node_flavor=None).values_list('node_flavor__number',flat=True
                                                         )
    for flavor_summary in queryset:
        print flavor_summary
        for ft in formula_trees.filter(root_flavor__number=flavor_summary['number']):
            if ft in component_summary:
                component_summary[ft] += flavor_summary['lot_count']
            else:
                component_summary[ft] = flavor_summary['lot_count']
                
    return component_summary
