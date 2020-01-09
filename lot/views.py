# TODO:    change row amounts according to form value
#          change page appearance after print link is pressed

import datetime
import sys
import logging
import hashlib
import os 

from django.template import Context, loader
from django.shortcuts import render, get_object_or_404
import json
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.template.loader import get_template
from django.db import connection
from django.contrib.contenttypes.models import ContentType


from elaphe import barcode

from access.models import Flavor
from newqc.models import Lot, get_next_lot_number
from salesorders.models import SalesOrderNumber, LineItem

from access.views import flavor_info_wrapper
from batchsheet.forms import BatchSheetForm

def batchsheet_home(request):
    batch_sheet_form = BatchSheetForm({
       'batch_amount':0,
       'lot_number':get_next_lot_number()
    })
    return render(
        request,
        'batchsheet/batchsheet_home.html',
        {
            'batch_sheet_form': batch_sheet_form,
        },
    )

def lot_init(request):
    #if request.is_ajax():
    try:
        lot_number = request.GET.get('lot_number', None)
        if lot_number is None or lot_number is get_next_lot_number():
            l = Lot(
                amount=request.GET['amount'],
                flavor=get_object_or_404(Flavor,number=request.GET['flavor_number']),
            )
            l.save()
        else:
            try:
                test_lot = Lot.objects.get(number=lot_number)
                if test_lot:
                    raise Lot.DoesNotExist
            except:
                l = Lot(
                    number=lot_number,
                    amount=request.GET['amount'],
                    flavor=get_object_or_404(Flavor,number=request.GET['flavor_number']),
                )
                l.save()
        return HttpResponse(json.dumps({'lot_number':l.number}), content_type='application/json; charset=utf-8')
    except Exception as e:
        return HttpResponse(json.dumps({'err':str(e)}), content_type='application/json; charset=utf-8')
#    else:
#        return HttpResponse(json.dumps("NOTHING TO DO HERE"))

class Bubble():
    def __init__(self, headline, contents):
        self.headline = headline
        self.contents = contents
                       
@flavor_info_wrapper
def batchsheet_print(request, flavor):
    json_dict = {}
    json_dict['batchsheet'] = ""
    json_dict['sidebar'] = ""
    try:
        
        batch_sheet_form = BatchSheetForm(request.GET)
        t = loader.get_template('batchsheet/batchsheet_print.html')
            
        if batch_sheet_form.is_valid():
            batch_amount = batch_sheet_form.cleaned_data['batch_amount']
            if batch_amount is None:
                batch_amount = 0
            c = {
                'flavor': flavor,
                'lot_number': batch_sheet_form.cleaned_data['lot_number'],
                'batch_amount': batch_amount
            }
            json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)
            
            soli_bubble=[]
            for soli in LineItem.objects.filter(flavor=flavor).filter(salesordernumber__open=True):
                soli_bubble.append("%s - %s - %s -%s lbs" % (
                        soli.salesordernumber.number, 
                        soli.salesordernumber.customer, 
                        soli.salesordernumber.create_date, 
                        soli.quantity 
                    ))     
            bubbles = [
                    Bubble('Summary', [
                            "Open orders:",
                            "Including gazintas:",
                            "Used last year:",
                            "Average use per year:",
                        ]),
                    Bubble('Open Sales Orders', soli_bubble), 
                ]       
            c = {
                'bubbles':bubbles,
            }
            json_dict['sidebar'] = loader.get_template('batchsheet/batchsheet_sidebar.html').render(c)
            
        else:
            c = {
                    'bsf':batch_sheet_form
                }
            # uh do something
        
        return HttpResponse(json.dumps(json_dict), content_type="application/json") 
    except Exception as e:
        json_dict['errors'] = repr(e)
        return HttpResponse(json.dumps(json_dict), content_type="application/json")
    
    return HttpResponse(json.dumps(json_dict), content_type="application/json")
#    else:
#        raise Http404


#def ajax_retain_status_change(request):
#    json_list = request.POST.get('retain_list').split('|')
#    new_status = request.POST.get('new_status')
#    for pk in json_list:
#        r = Retain.objects.get(pk=pk)
#        r.status=new_status
#        r.save()
#    return HttpResponse(
#        json.dumps(json_list)                    
#    )
