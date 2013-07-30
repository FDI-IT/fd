import StringIO
import re

from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, QueryDict
from django.utils import simplejson
from django.db.models import Count

from access.models import Ingredient, Flavor, ExperimentalLog
from access.views import ingredient_autocomplete

from lab.forms import SolutionForm, FinishedProductLabelForm, RMLabelForm, ExperimentalForm
from newqc.models import ReceivingLog
from lab.glabels_scripts import rm_label, solution_label, experimental_label, solution_print, finished_product_label, rm_sample_label

from unified_adapter.models import ProductInfo

INVENTORY_CHOICES = (
    ('SL-8','SL-8'),
    ('SL-4','SL-4'),
    ('SLF-L','SLF-L'),
    ('SLF-O','SLF-O'),
    ('SD Lab','SD Lab'),
    ('Concentrates','Concentrates'),
    ('Refrigerator','Refrigerator'),
    ('None','None'),
)

number_re = re.compile('\d+')
def calculate_location_code(inventory_choice):
    if inventory_choice[:2] == "SL":
        
        flavor_last_slot = Flavor.objects.filter(location_code__istartswith=inventory_choice).order_by('-location_code')[0]
        experimental_last_slot = ExperimentalLog.objects.filter(location_code__istartswith=inventory_choice).order_by('-location_code')[0]
        
        flavor_last_number = int(number_re.search(flavor_last_slot.location_code).group())
        experimental_last_number = int(number_re.search(experimental_last_slot.location_code).group())
        
        if flavor_last_number > experimental_last_number:
            next_number = flavor_last_number+1
        else:
            next_number = experimental_last_number+1

        return "%s%s" % (inventory_choice, str(next_number+1)[1:])
        
    elif inventory_choice == "":
        return ""
    else:
        return inventory_choice
    
    
def rm_sample_labels(request):
    receiving_log = ReceivingLog.objects.all()[0]
    pdf_file = open(rm_sample_label(receiving_log),'rb')
    response = HttpResponse(pdf_file.read(), mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="label.pdf"'
    return response 

def experimental_labels(request):
    page_title = "Experimental Labels"
    if 'experimental_number' in request.GET:
        experimental = ExperimentalLog.objects.get(experimentalnum=request.GET['experimental_number'])
        
        if experimental.flavor == None:
            return redirect('%s?status_message=Unable to print label because a formula must be entered.' % experimental.get_absolute_url())
        if 'inventory_slot' in request.GET and request.GET['inventory_slot'] != "":
            if experimental.location_code == u"":
                loc_code = calculate_location_code(request.GET['inventory_slot'])
                experimental.location_code = loc_code
                experimental.flavor.location_code = loc_code
                experimental.save()
                experimental.flavor.save()
            else:
                return redirect('%s?status_message=Unable to print label because a location code was requested, but this flavor already has one.' % experimental.get_absolute_url())
        pdf_file = open(experimental_label(request.GET['experimental_number']),'rb')
        response = HttpResponse(pdf_file.read(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="label.pdf"'
        return response
    else:
        
        experimental_form = ExperimentalForm()
        return render_to_response('lab/experimental_labels.html',
                                  {
                                   'page_title':page_title,
                                   'form':experimental_form,
                                   })

def finished_product_labels(request):
    page_title = "Finished Product Labels"
    if 'production_number' in request.GET:
        flavor = Flavor.objects.get(number=request.GET['production_number'])
        
        if 'inventory_slot' in request.GET and request.GET['inventory_slot'] != "":
            if flavor.location_code == u"":
                next_location_code = calculate_location_code(request.GET['inventory_slot'])
                
                
                flavor.location_code = next_location_code
                flavor.save()
                
                for experimental in flavor.experimental_log.all():
                    experimental.location_code = next_location_code
                    experimental.save()
            else:
                return redirect('%s?status_message=Unable to print label because a location code was requested, but this flavor already has one.' % flavor.get_absolute_url())
                                                                
        pdf_file = open(finished_product_label(request.GET['production_number']),'rb')
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="label.pdf"'
        return response
    else:
        form = FinishedProductLabelForm()
        return render_to_response('lab/finished_product_labels.html',
                                  {
                                   'page_title':page_title,
                                   'form':form,
                                   })
    
def inventory(request):
    # TODO
    page_title = "Sample Inventory"
    if 'loc_code' in request.GET:
        loc_code_query = request.GET.get('loc_code',"")
        if loc_code_query == "other":
            queryset = ProductInfo.objects.exclude(location_code="").exclude(
                location_code__istartswith="x").exclude(
                location_code__istartswith="sl-8").exclude(
                location_code__istartswith="sl-4").exclude(
                location_code__istartswith="slf-l").exclude(
                location_code__istartswith="slf-o").exclude(
                location_code__istartswith="sd").exclude(
                location_code__istartswith="conc").exclude(
                location_code__istartswith="refri").order_by('location_code','name')
        else:
            queryset = ProductInfo.objects.exclude(location_code="").exclude(location_code__iexact="x").filter(location_code__istartswith=loc_code_query).order_by('location_code','name')
        return render_to_response('lab/inventory.html',
                                  {
                                   'queryset':queryset,
                                   'page_title':page_title,
                                   })

    else:
        return render_to_response('lab/inventory_select.html',
                                  {
                                   'page_title':page_title,
                                   })

def rm_labels(request):
    page_title = "Raw Material Labels"
    if 'pin' in request.GET:
        pdf_file = open(rm_label(request.GET['pin']),'rb')
        response_dict = {}
        response_dict['ajax'] = True
        if 'preview' in request.GET:
            return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')    
        else:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="label.pdf"'
            return response
    else:
        form = RMLabelForm()
        return render_to_response('lab/rm_labels.html',
                                  {
                                   'page_title':page_title,
                                   'form':form,
                                   })

def solution(request):
    page_title = "Solution Labels"
    if 'product_name' in request.GET:
        pdf_file = open(solution_label(request),'rb')
        response_dict = {}
        response_dict['ajax'] = True
        if 'preview' in request.GET:
            return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')    
        else:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="label.pdf"'
            return response
    else:
        solution_form = SolutionForm()
        return render_to_response('lab/solution.html',
                                  {
                                   'page_title':page_title,
                                   'form':solution_form,
                                   })

def ingredient_label(request):
    ingredient_id = request.GET['ingredient_id']
    ingredient = Ingredient.objects.get(id=ingredient_id)
    ingredient_json = {}
    ingredient_json['nat_art'] = ingredient.art_nati
    ingredient_json['pf'] = ingredient.prefix
    ingredient_json['product_name'] = ingredient.product_name
    ingredient_json['product_name_two'] = ingredient.part_name2
    return HttpResponse(simplejson.dumps(ingredient_json), content_type='application/json; charset=utf-8')


def experimentals_by_customer(request):
    queryset = ExperimentalLog.objects.values('customer').annotate(Count('customer')).order_by('customer')
    return render_to_response('lab/experimentals_by_customer.html',
                              {'queryset':queryset},
                              )    
    
def experimentals_by_customer_specific(request, customer):
    queryset = ExperimentalLog.objects.filter(customer=customer)
    return render_to_response('lab/experimentals_by_customer_specific.html',
                              {'queryset':queryset},
                              )    
