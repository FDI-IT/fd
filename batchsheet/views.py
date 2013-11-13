# TODO:    change row amounts according to form value
#          change page appearance after print link is pressed

import datetime
import sys
import logging
import hashlib
import os 
import json
from decimal import Decimal
from operator import itemgetter

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
from batchsheet import forms
from batchsheet.forms import BatchSheetForm, NewLotForm, UpdateLotForm, build_confirmation_rows

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


def update_lots(request, lot_pk, amount, extra=1): #change this - if updating one lot from add lots screen, go straight to update confirmation
    if request.method == 'GET':
        #get list of ot numbers and amounts from request.get
        #if list exists:
            #confirmation page
        #else:
            #update page
        
        LotFormSet = formset_factory(forms.UpdateLotForm, extra=extra) #default, empty formset
        formset = LotFormSet()
        
        try:
            LotFormSet = formset_factory(forms.UpdateLotForm, extra=0)
            formset = LotFormSet(request.GET)
            #print 'z'
        except:
            try:
                #redirected from Add Lots page
                if lot_pk != None and amount != None:
                    update_lot = Lot.objects.get(pk = lot_pk)
                    update_row = [{'lot_number': update_lot.number, 'flavor_number': update_lot.flavor.number, 'amount': amount}]
                    
                    LotFormSet = formset_factory(forms.UpdateLotForm, extra = 0)
                    formset = LotFormSet(initial = update_row)
                #print 'y'
            except:
                pass
                #print 'x'
 
        
        #else:    
        #    LotFormSet = formset_factory(forms.UpdateLotForm)
        #    formset = LotFormSet(request.GET)        
        
        if formset.is_valid():
            
                            
            display_info = build_confirmation_rows(formset)
            confirmation_rows = zip(formset.forms, display_info)
                
                
            return render_to_response('batchsheet/lot_update_confirmation.html',
                                        {'formset': formset,
                                         'management_form': formset.management_form,
                                         #'confirmation_info': confirmation_info,
                                         'confirmation_rows': confirmation_rows,
                                         #'confirm': confirm,
                                         },
                                         context_instance=RequestContext(request))    
        else:    
            return render_to_response('batchsheet/update_lots.html',
                                        {'formset': formset,
                                         'management_form': formset.management_form,
                                         },
                                         context_instance=RequestContext(request))      
    elif request.method == 'POST':
        LotFormSet = formset_factory(forms.UpdateLotForm)
        formset = LotFormSet(request.POST)  
        
        if formset.is_valid():
            for form in formset.forms:
                cd = form.cleaned_data
                
                update_lot = Lot.objects.get(number = cd['lot_number'])
                update_lot.amount = cd['amount']
                update_lot.status = 'Created'
                
        
        else:
            print 'AKJSHF'


'''    
    if request.method == 'POST':
        LotUpdateFormSet = formset_factory(UpdateLotForm)
        
        formset = LotUpdateFormSet(request.POST)
        if formset.is_valid():
            new_lots = []
            for form in formset.forms:
                cd = form.cleaned_data
                
                new_lots.append((cd['lot_number'], cd['flavor_number'], cd['amount']))
                
            request.method = 'GET'
            return lot_update_confirmation(request, new_lots)
        else:        
            return render_to_response('batchsheet/lot_update_confirmation.html', 
                                      {'formset': formset,
                                       'management_form': formset.management_form},
                                      context_instance=RequestContext(request))
            
    else:
        if lot_pk != None:
            lot = Lot.objects.get(pk = lot_pk)
        
            lot_list = []
        
            lot_list.append({'lot_number': lot.number, 'flavor_number': lot.flavor.number, 'amount': lot.amount})
            
        
            LotFormSet = formset_factory(forms.UpdateLotForm, extra=0)
            formset = LotFormSet(initial=lot_list)
        
        else:
            LotFormSet = formset_factory(forms.UpdateLotForm, extra=1)
            formset = LotFormSet()            
                
        return render_to_response('batchsheet/add_lots.html',
                                        {'formset': formset,
                                         'management_form': formset.management_form,
                                         },
                                         context_instance=RequestContext(request))
'''
                
def lot_update_confirmation(request, lot_list=None): #go straight here if clicking url from add_lots
    if request.method == 'POST':
        
        LotUpdateFormSet = formset_factory(UpdateLotForm)
        
        formset = LotUpdateFormSet(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                cd = form.cleaned_data
                update_lot = Lot.objects.get(cd['lot_number'])
                
                update_lot.amount = cd['amount']
                update_lot.status = 'Created'
                
                update_lot.save()        
        
            redirect_path = "/django/qc/lots"
            return HttpResponseRedirect(redirect_path)
        
        else:
            return render_to_response('batchsheet/lot_update_confirmation.html', 
                                      {'formset': formset,
                                       'management_form': formset.management_form},
                                      context_instance=RequestContext(request))        
        '''
        for lot_number, flavor_number, amount in lot_list:
            ''''''
            try:
                lot_flavor = Flavor.objects.get(number=lot['flavor_number'])
            except KeyError:
                print "LOT UPDATE CONFIRMATION KEYERROR"
            ''''''
            
            update_lot = Lot.objects.get(number = lot_number)
            
            update_lot.amount = amount
            update_lot.status = 'Created'
            
            update_lot.save()
        
        redirect_path = "/django/qc/lots"
        return HttpResponseRedirect(redirect_path)
        '''
    else:
        if lot_list != None:
            LotFormSet = formset_factory(forms.UpdateLotForm, extra=0)
            formset = LotFormSet(initial=lot_list)
        #else:
        #    formset = None
        
        
        confirm = True
        update_info = []
        for lot_number, flavor_number, amount in lot_list:
            old_amount = Lot.objects.get(number = lot_number).amount
            old_status = Lot.objects.get(number = lot_number).status
            
            if amount == old_amount:
                warning = 'The specified lot already has an amount of %s.' % old_amount
            else:
                warning = None
            
            update_info.append((lot_number, flavor_number, old_amount, old_status, amount, 'Created', warning))
            
            if warning:
                confirm = False
            
        return render_to_response('batchsheet/lot_update_confirmation.html',
                                    {'update_info': update_info,
                                     'formset': formset,
                                     'management_form': formset.management_form,
                                     'confirm': confirm},
                                    context_instance = RequestContext(request))
            
                
            
        

def add_lots(request):
    if request.method == 'POST':
        LotFormSet = formset_factory(NewLotForm)
        
        formset = LotFormSet(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                cd = form.cleaned_data
                #cd['status'] = 'Created'
                
                try:
                    lot_flavor = Flavor.objects.get(number=cd['flavor_number'])
                except KeyError:
                    print "LKJASLDFJAF ERROR"
                                                
                new_lot = Lot(number = cd['lot_number'],
                              flavor = lot_flavor,
                              amount = cd['amount'],
                              status = 'Created')
                
                new_lot.save()
                              
                '''
                lot_list['lot_number'] = cd['lot_number']
                lot_list['flavor_number'] = cd['flavor_number'] 
                lot_list['amount'] = cd['amount']
                lot_list['status'] = cd['status']
                '''
                
            redirect_path = "/django/qc/lots"
            return HttpResponseRedirect(redirect_path)
        
        else:            
            return render_to_response('batchsheet/add_lots.html', 
                                      {'formset': formset,
                                       'management_form': formset.management_form},
                                      context_instance=RequestContext(request))

                
                

    else:        

        lot_checklist = []
        selected_orders = request.GET.getlist('flavor_pks')
        
        for order in selected_orders:
            #this changes the format of the GET request to convert the json strings into python dicts
            lot_checklist.append((json.loads(order.replace('\'','!').replace('\"','\'').replace('!','\"')))[0]) 

        #print lot_checklist
        
        lot_number = get_next_lot_number()
        
        #assign lot numbers to new lots 
        for lot in lot_checklist:
            #if lot['amount'][-2:] == '00':
            #    lot['amount'] = lot['amount'][:-1] #get rid of the second decimal digit in amount, since the lot model only takes one
            #lot['amount'] = int(lot['amount'])
            lot['lot_number'] = lot_number
            lot_number = lot_number + 1
            
        
        LotFormSet = formset_factory(forms.NewLotForm, extra=0)
        
        formset = LotFormSet(initial=lot_checklist)
        #lot_list = formset.forms
        
        return render_to_response('batchsheet/add_lots.html',
                                        {'formset': formset,
                                         'management_form': formset.management_form,
                                         },
                                         context_instance=RequestContext(request))
        
        '''
    # else:
    initial_data, label_rows = forms.build_formularow_formset_initial_data(flavor)
    if len(label_rows) == 0:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=1)
        label_rows.append({'cost': '', 'name': ''})
    else:
        FormulaFormSet = formset_factory(forms.FormulaRow, extra=0)
        
    filterselect = FormulaEntryFilterSelectForm(request.GET.copy())

    formset = FormulaFormSet(initial=initial_data)
    formula_rows = zip(formset.forms,
                       label_rows )
  
    
    return render_to_response('access/flavor/formula_entry.html', 
                                  {'flavor': flavor,
                                   'filterselect': filterselect,
                                   'status_message': status_message,
                                   'window_title': page_title,
                                   'page_title': page_title,
                                   'formula_rows': formula_rows,
                                   'management_form': formset.management_form,
                                   },
                                   context_instance=RequestContext(request))
    
        '''


def lot_notebook(request):
    pass

def sales_order_list(request, status_message=None):
    page_title="Sales Orders - Production"
    help_link = "/wiki/index.php/Sales_orders"
    hundredths = Decimal('0.00')
    orders= {}
    for order in LineItem.objects.filter(salesordernumber__open=True):
        try:
            orders[order.flavor] += [order]
        except KeyError:
            orders[order.flavor] = [order]
           # 
    summarized_orders = []
    for flavor, details in orders.items():
        total = Decimal('0')
        for detail in details:
            total += detail.quantity
        try:
            totalcost = flavor.rawmaterialcost * total
            totalcost = totalcost.quantize(hundredths, rounding=ROUND_HALF_UP)
            #flavor.update_cost()
        except:
            totalcost = 0
        summarized_orders.append({'flavor': flavor,
                                  'total': total,
                                  'details':details,
                                  'totalcost':totalcost,
                                  })
    summarized_orders = sorted(summarized_orders, key=itemgetter('total'))
    resultant_orders = summarized_orders

    return render_to_response('batchsheet/sales_order_production.html',
                              {
                               'window_title': page_title,
                               'accept_link': 'javascript:document.forms["salesorder_selections"].submit()',
                               'orders':resultant_orders,
                               'help_link': help_link,
                               'status_message': status_message,
                               'page_title':page_title,
                               'get': request.GET,},
                               context_instance=RequestContext(request))

    



