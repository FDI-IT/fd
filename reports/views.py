import datetime
from datetime import date
from decimal import Decimal
import re

from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.views.generic import list_detail
from django.views.generic.date_based import archive_index
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

from access.models import Flavor, FormulaTree, ExperimentalLog

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
    return list_detail.object_list(
               request,
              # paginate_by=100,
               queryset=lot_annotations,
               template_name='reports/lots_by_person.html',
               extra_context={
                   'page_title': 'Lots by Person',
                   'date_range_form':date_range_form,
               }                        
           )
    
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
        
    return render_to_response('reports/conversions_by_person.html',
               {
                'object_list':object_list,
                'page_title': 'Conversions by Person',
                'date_range_form':date_range_form,
               },
                context_instance=RequestContext(request)                
           )
        
@permission_required('access.add_indivisibleleafweight')
def experimental_log_exclude(request):
    if 'epk' in request.POST and 'exclude_from_reporting' in request.POST:
        e = ExperimentalLog.objects.get(pk=request.POST['epk'])
        new_val = request.POST['exclude_from_reporting']
        controller.toggle_exclude_from_reporting(e, new_val)
        return HttpResponse(
                            simplejson.dumps(['Success',])                    
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
    return render_to_response('reports/experimental_log.html',
               {
                'experimental_logs':els,
                'page_title': 'Experimental Log',
                'date_range_form':date_range_form,
                'filterselect':filterselect,
                'aggregated_data':aggregated_data,
                #'date_range_form':date_range_form,
               },
                context_instance=RequestContext(request)                
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
    return list_detail.object_list(
               request,
              # paginate_by=100,
               queryset=queryset,
               template_name='reports/lot_summary.html',
               extra_context={
                   'page_title': 'Lot Summary',
               }                        
           )
    
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
    return render_to_response('reports/formula_usage_summary.html',
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
