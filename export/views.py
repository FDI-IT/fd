from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

from export.magento_util import base_export_dict, export_attribute_list
from access.models import Flavor, MagentoFlavor

import datetime
import csv

def export_home(request):
    return render(
        request,
        'export/main.html'
    )   
    
def get_export_keys():
    export_dict = base_export_dict.copy() #this ensures that the keys are in the right order
    return list(export_dict.keys())

def get_export_values(attribute_dict):
    export_dict = base_export_dict.copy()
    export_dict.update(attribute_dict)
    
    export_values = []
    for key in export_dict:
        export_values.append(export_dict[key])
        
    #return export_values
    return list(export_dict.values())


def create_export_dict(attribute_dict):
    export_dict = dict(list(base_export_dict.items()) + list(attribute_dict.items()))
    return export_dict
    
    
def export_all(request): #NEED TO CREATE DEFAULT VALUES FOR SKU, ETC
    export_objects = MagentoFlavor.objects.all()
    export_keys = get_export_keys()
    
    export_values_lists = []
    
    for obj in export_objects:
        attribute_dict = {}
        attribute_dict.update({
            'sku' : obj.sku,
            '_category' : 'Natural Flavors', #change later, can be Natural Flavors or OC Flavors
            'created_at' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'description' : obj.description,
            'flavor_type' : 'Natural', #change later
            'name' : obj.flavor.name,
            'price': obj.price,
            'short_description' : obj.short_description,  
        })
        
        export_values = get_export_values(attribute_dict)
        export_values_lists.append(export_values)
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="magento_flavors_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(export_keys)
    
    for export_row in export_values_lists:
        writer.writerow(export_row)
    
    return response

def single_export(request, flavor_id):
    fl = Flavor.objects.get(number=flavor_id)
    
    attribute_dict = {}
    attribute_dict.update({
        'sku' : fl.number,
        '_category' : 'Natural Flavors', #change later, can be Natural Flavors or OC Flavors
        'created_at' : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'description' : "A flavor with the taste and aroma of %s" % fl.name,
        'flavor_type' : 'Natural', #change later
        'name' : fl.name,
        'price': '36',
        'short_description' : "A flavor with the taste and aroma of %s" % fl.name,
    })
  
    export_keys = list(base_export_dict.keys())
    export_values = get_export_values(attribute_dict)

    
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="flavor%s_export.csv"' % flavor_id
    
    writer = csv.writer(response) 
    writer.writerow(export_keys)
    writer.writerow(export_values)
    
    return response
    