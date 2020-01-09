import io
import re

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, QueryDict
import json
from django.db.models import Count

from access.models import Ingredient, Flavor, ExperimentalLog, LocationCode
from access.views import ingredient_autocomplete

from lab.forms import FinishedProductLabelForm, RMLabelForm, ExperimentalForm
from newqc.models import ReceivingLog
from lab.glabels_scripts import rm_label, solution_label, experimental_label, solution_print, finished_product_label, rm_sample_label

INVENTORY_CHOICES = (
    ('SL-8','SL-8'),
    ('SL-4','SL-4'),
    ('SLF-L','SLF-L'),
    ('SLF-O','SLF-O'),
    ('SD Lab','SD Lab'),
    ('Concentrates','Concentrates'),
    ('Sample Lab','Sample Lab'),
    ('OC','OC'),
    ('Refrigerator','Refrigerator'),
    ('None','None',),
)

def rm_sample_labels(request):
    receiving_log = ReceivingLog.objects.all()[0]
    pdf_file = open(rm_sample_label(receiving_log),'rb')
    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="label.pdf"'
    return response 

def experimental_labels(request):
    page_title = "Experimental Labels"
    if 'experimental_number' in request.GET:
        experimental = ExperimentalLog.objects.get(experimentalnum=request.GET['experimental_number'])

        if experimental.flavor == None or experimental.flavor.formula_set.all().count() == 0:
            return redirect('%s?status_message=Unable to print label because a formula must be entered.' % experimental.get_absolute_url())
        if 'inventory_slot' in request.GET and request.GET['inventory_slot'] != "":
            if experimental.location_code == "" or experimental.location_code == "" or experimental.location_code is None:
                loc_code = LocationCode.get_next_location_code(request.GET['inventory_slot'])
                lc = LocationCode(
                            location_code = loc_code,
                            content_object = experimental.flavor        
                        )
                lc.save()
            else:
                return redirect('%s?status_message=Unable to print label because a location code was requested, but this flavor already has one.' % experimental.get_absolute_url())
        pdf_file = open(experimental_label(request.GET['experimental_number']),'rb')
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="label.pdf"'
        return response
    else:
        
        experimental_form = ExperimentalForm()
        return render(
            request,
            'lab/experimental_labels.html',
            {
                'page_title':page_title,
                'form':experimental_form,
            }
        )

def finished_product_labels(request):
    page_title = "Finished Product Labels"
    if 'production_number' in request.GET:
        flavor = Flavor.objects.get(number=request.GET['production_number'])
        
        if 'inventory_slot' in request.GET and request.GET['inventory_slot'] != "":
            if flavor.location_code == "" or flavor.location_code == "" or flavor.location_code is None:
                loc_code = LocationCode.get_next_location_code(request.GET['inventory_slot'])
                lc = LocationCode(
                            location_code=loc_code,
                            content_object=flavor
                        )
                lc.save()
            else:
                return redirect('%s?status_message=Unable to print label because a location code was requested, but this flavor already has one.' % flavor.get_absolute_url())
                                                                
        pdf_file = open(finished_product_label(request.GET['production_number']),'rb')
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="label.pdf"'
        return response
    else:
        form = FinishedProductLabelForm()
        return render(
            request,
            'lab/finished_product_labels.html',
            {
                'page_title':page_title,
                'form':form,
            }
        )
    
def inventory(request):
    # TODO
    page_title = "Sample Inventory"
    if 'loc_code' in request.GET:
        loc_code_query = request.GET.get('loc_code',"")
        if loc_code_query == "other":
            queryset = LocationCode.objects.exclude(location_code="").exclude(
                location_code__iexact="x").exclude(
                location_code__istartswith="sl-8").exclude(
                location_code__istartswith="sl-4").exclude(
                location_code__istartswith="slf-l").exclude(
                location_code__istartswith="slf-o").exclude(
                location_code__istartswith="sd").exclude(
                location_code__istartswith="conc").exclude(
                location_code__istartswith="refri").order_by('location_code')
        else:
            queryset = LocationCode.objects.exclude(location_code="").exclude(location_code__iexact="x").filter(location_code__istartswith=loc_code_query).order_by('location_code')
        return render(
            request,
            'lab/inventory.html',
            {
                'queryset':queryset,
                'page_title':page_title,
            }
        )

    else:
        return render(
            request,
            'lab/inventory_select.html',
            {
                'page_title':page_title,
            }
        )

def rm_labels(request):
    page_title = "Raw Material Labels"
    if 'pin' in request.GET:
        pdf_file = open(rm_label(request.GET['pin']),'rb')
        response_dict = {}
        response_dict['ajax'] = True
        if 'preview' in request.GET:
            return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')    
        else:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="label.pdf"'
            return response
    else:
        form = RMLabelForm()
        return render(
            request,
            'lab/rm_labels.html',
            {
                'page_title':page_title,
                'form':form,
            }
        )

def solution(request):
    page_title = "Solution Labels"
    if 'product_name' in request.GET:
        pdf_file = open(solution_label(request),'rb')
        response_dict = {}
        response_dict['ajax'] = True
        if 'preview' in request.GET:
            return HttpResponse(json.dumps(response_dict), content_type='application/json; charset=utf-8')    
        else:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="label.pdf"'
            return response
    else:
        solution_form = SolutionForm()
        return render(
            request,
            'lab/solution.html',
            {
                'page_title':page_title,
                'form':solution_form,
            }
        )

def ingredient_label(request):
    ingredient_id = request.GET['ingredient_id']
    ingredient = Ingredient.objects.get(id=ingredient_id)
    ingredient_json = {}
    ingredient_json['nat_art'] = ingredient.art_nati
    ingredient_json['pf'] = ingredient.prefix
    ingredient_json['product_name'] = ingredient.product_name
    ingredient_json['product_name_two'] = ingredient.part_name2
    return HttpResponse(json.dumps(ingredient_json), content_type='application/json; charset=utf-8')


def experimentals_by_customer(request):
    queryset = ExperimentalLog.objects.values('customer').annotate(Count('customer')).order_by('customer')
    return render(
        request,
        'lab/experimentals_by_customer.html',
        {'queryset':queryset},
    )
    
def experimentals_by_customer_specific(request, customer):
    queryset = ExperimentalLog.objects.filter(customer=customer)
    return render(
        request,
        'lab/experimentals_by_customer_specific.html',
        {'queryset':queryset},
    )
