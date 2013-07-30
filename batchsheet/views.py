# TODO:    change row amounts according to form value
#          change page appearance after print link is pressed

import datetime
import sys
import logging
import hashlib
import os 
from decimal import Decimal

from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.http import Http404
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.views.generic import list_detail
from django.views.generic.date_based import archive_index
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType

from sorl.thumbnail import get_thumbnail

from elaphe import barcode

from access.models import Flavor
from newqc.models import Lot, get_next_lot_number
from salesorders.models import SalesOrderNumber, LineItem

from access.views import flavor_info_wrapper
from batchsheet.forms import BatchSheetForm

def batchsheet_home(request):
    batch_sheet_form = BatchSheetForm({
       'batch_amount':0,
       # 'lot_number':get_next_lot_number()
    })
    return render_to_response('batchsheet/batchsheet_home.html',
                              {
                               'batch_sheet_form': batch_sheet_form,
                               },
                              context_instance=RequestContext(request))

def next_lot(request):
    return HttpResponse(simplejson.dumps({'lot_number':get_next_lot_number()}), content_type='application/json; charset=utf-8')

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
        return HttpResponse(simplejson.dumps({'lot_number':l.number}), content_type='application/json; charset=utf-8')
    except Exception as e:
        return HttpResponse(simplejson.dumps({'err':str(e)}), content_type='application/json; charset=utf-8')
#    else:
#        return HttpResponse(simplejson.dumps("NOTHING TO DO HERE"))

class Bubble():
    def __init__(self, headline, contents):
        self.headline = headline
        self.contents = contents
    
pounds_grams_conversion = Decimal("453.59237")
def weighted_formula_set(f,wf):
    for fr in f.formula_set.all():
        fr.amount = fr.amount * wf
        fr.totalweight = fr.amount * pounds_grams_conversion
        yield fr
                     
def get_barcode(request, barcode_contents):
    barode_string = "BATCHSHEET_LOT-%s" % str(barcode_contents)
    x = barcode('qrcode', barode_string, options=dict(version=4, eclevel='M'),margin=0, data_mode='8bits')
    #x = barcodeImg(codeBCFromString(str(retain_pk)))
    response = HttpResponse(mimetype="image/png")
    x.save(response, "PNG")
    return response
                     
@flavor_info_wrapper
def batchsheet_print(request, flavor):
    json_dict = {}
    json_dict['batchsheet'] = ""
    json_dict['sidebar'] = ""
     
    try:
        
        batch_sheet_form = BatchSheetForm(request.GET)
        t = loader.get_template('batchsheet/batchsheet_print.html')
            
        if batch_sheet_form.is_valid():
            dci =  flavor.discontinued_ingredients
            qv = flavor.quick_validate()
            if qv != True:
                c = Context({'flavor':u"%s -- NOT APPROVED -- %s" % (flavor.__unicode__(), qv)})
                json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)
            elif len(dci) != 0:
                c = Context({'flavor':u"%s -- NOT APPROVED -- Contains discontinued ingredients: %s" % (flavor.__unicode__(), ", ".join(dci))})
                json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)            
            elif flavor.approved == False:
                c = Context({'flavor':u"%s -- NOT APPROVED" % flavor.__unicode__()})
                json_dict['batchsheet'] = loader.get_template('batchsheet/batchsheet_print.html').render(c)
            else:
                
                
                try:
                    batch_amount = Decimal(batch_sheet_form.cleaned_data['batch_amount'])
                except:
                    batch_amount = Decimal("0")
                if 'get_next_lot' in request.GET:
                    lot_number = get_next_lot_number()
                    json_dict['lot_number'] = lot_number
                else:
                    lot_number = batch_sheet_form.cleaned_data['lot_number']
                
                if flavor.yield_field and flavor.yield_field != 100:
                    batch_amount = batch_amount/(flavor.yield_field/Decimal("100"))
                
                weight_factor = batch_amount / Decimal("1000")
                c = Context({
                    'flavor': flavor,
                    'weighted_formula_set':weighted_formula_set(flavor,weight_factor),
                    'lot_number': lot_number,
                    'batch_amount': batch_amount
                })
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
                        Bubble('<a href="/django/access/%s/" target="_blank">Flavor Info</a>' % flavor.number, [
                                "Flash point: %s" % flavor.flashpoint,
                                "Yield: %s" % flavor.yield_field,
                                "Allergens: %s" % flavor.allergen,
                                "Solvent: %s" % flavor.solvent,
                                "Kosher: %s" % flavor.kosher,
                                "Organic: %s" % flavor.organic,
                            ]),
                        Bubble('Summary', [
                                "Open orders: %s" % LineItem.objects.filter(flavor=flavor).filter(salesordernumber__open=True).count(),
                                "Total weight: %s" % LineItem.objects.filter(flavor=flavor).filter(salesordernumber__open=True).aggregate(Sum('quantity'))['quantity__sum'],
                            ]),
                        Bubble('<a href="/django/salesorders/" target="_blank">Open Sales Orders</a>', soli_bubble), 
                    ]       
                c = Context({
                    'bubbles':bubbles,
                })
                json_dict['sidebar'] = loader.get_template('batchsheet/batchsheet_sidebar.html').render(c)
                
        else:
            c = Context({
                    'bsf':batch_sheet_form
                })
            # uh do something
        
        return HttpResponse(simplejson.dumps(json_dict), mimetype="application/json") 
    except Exception as e:
        json_dict['errors'] = repr(e)
        return HttpResponse(simplejson.dumps(json_dict), mimetype="application/json")
    
    return HttpResponse(simplejson.dumps(json_dict), mimetype="application/json")


def lot_notebook(request):
    pass
