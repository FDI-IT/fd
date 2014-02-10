# TODO: RETURN THE PATH OF PREVIEW AND FULL
#        ADD THE FULL IMAGE TO A HIDDEN ELEMENT
#        FADE EFFECT BETWEEN IMAGES WHEN FORMS SWITCH FOCUSx

# TODO: retain checklist to pull targets.

import datetime

import re

from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.views.generic import list_detail
from django.views.generic.date_based import archive_index
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Count, Sum

from access.models import Flavor, FormulaTree

from reports import forms

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
