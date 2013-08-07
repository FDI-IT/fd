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
from django.contrib.auth.decorators import login_required
from django.db import connection

from sorl.thumbnail import get_thumbnail

from elaphe import barcode

from access.barcode import barcodeImg, codeBCFromString
from access.models import Flavor, Ingredient
from access.views import flavor_info_wrapper
from newqc.forms import NewFlavorRetainForm, ResolveTestCardForm, RetainStatusForm, ResolveRetainForm, ResolveLotForm, NewRMRetainForm, ProductInfoForm, LotFilterSelectForm, NewReceivingLogForm, AddObjectsBatch
from newqc.models import Retain, ProductInfo, TestCard, Lot, RMRetain, BatchSheet, ReceivingLog
from newqc.utils import process_jbg, get_card_file, scan_card
from newqc.tasks import walk_scans_qccards

def lot_month_list():
    return Lot.objects.all().dates('date', 'month').reverse()

def batchsheet_month_list():
    return None

def retain_month_list():
    return Retain.objects.all().dates('date', 'month').reverse()

def rm_retain_month_list():
    return RMRetain.objects.all().dates('date', 'month').reverse()

def receiving_log_month_list():
    return ReceivingLog.objects.all().dates('date','month').reverse()

def lot_status_list():    
    cursor = connection.cursor()
    cursor.execute('select distinct "newqc_lot"."status" from "newqc_lot"')
    status_choices = []
    for choice in cursor.fetchall():
        status_choices.append(choice[0])

    return status_choices

MONTHS = {
          '01':'January',
          '02':'February',
          '03':'March',
          '04':'April',
          '05':'May',
          '06':'June',
          '07':'July',
          '08':'August',
          '09':'September',
          '10':'October',
          '11':'November',
          '12':'December',
    }

STATUS_BUTTONS =  {
    'repeat_link': 'javascript:ajax_retain_status_change("Resample")',
    'repeat_link_alt': 'Resample',
    'pause_link': 'javascript:ajax_retain_status_change("Hold")',
    'pause_link_alt': 'Hold',
    'accept_link': 'javascript:ajax_retain_status_change("Passed")',
    'accept_link_alt': 'Pass',
    'del_link': 'javascript:ajax_retain_status_change("Rejected")',
    'del_link_alt': 'Reject',
}
retain_list_info =  {
    'queryset': Retain.objects.all(),
    'paginate_by': 100,
    'extra_context': dict({
        'page_title': 'QC Retains',
        'print_link': 'javascript:document.forms["retain_selections"].submit()',
        'month_list': retain_month_list,
        'admin_link': "/django/admin/newqc/retain/",
    }, **STATUS_BUTTONS),
}
rm_retain_list_info =  {
    'queryset': RMRetain.objects.all(),
    'paginate_by': 100,
    'extra_context': dict({
        'page_title': 'RM Retains',
        'print_link': 'javascript:document.forms["retain_selections"].submit()',
        'month_list': rm_retain_month_list,
        'admin_link': "/django/admin/newqc/rmretain/",
    }, **STATUS_BUTTONS),
}

receiving_log_list_info = {
    'queryset': ReceivingLog.objects.all(),
    'paginate_by': 100,
    'extra_context': dict({
        'page_title': 'Receiving Log',
        'month_list': receiving_log_month_list,
        'admin_link': "/django/admin/newqc/receivinglog/",
    }),                    
}

lot_list_queryset = Lot.objects.extra(select={'lotyear':'extract(year from date)','lotmonth':'extract(month from date)'})
lls = lot_list_queryset.order_by('-lotyear','-lotmonth','-number')
#Lot.objects.extra(select={'lotyear':'YEAR(date)','lotmonth':'MONTH(date)'}, order_by=['lotyear','lotmonth',],),
lot_list_info =  {
                  
    'queryset': lls,
    'paginate_by': 1000,
    'extra_context': dict({
        'page_title': 'Lots',
        'print_link': 'javascript:document.forms["lot_selections"].submit()',
        'month_list': lot_month_list,
        'status_list': lot_status_list,
        'filterselect':LotFilterSelectForm(),
        # fix this javascript...
    }),
}
batchsheet_list_info =  {
    'queryset': BatchSheet.objects.all(),
    'paginate_by': 500,
    'extra_context': dict({
        'page_title': 'Batch sheets',
        'month_list': batchsheet_month_list,
        # fix this javascript...
    }, **STATUS_BUTTONS),
}

lot_list_attn =  {
    'queryset': Lot.objects.filter(retain__status="Not Passed..."),
    'paginate_by': 100,
    'extra_context': dict({
        'page_title': 'Lots',
        'print_link': 'javascript:document.forms["lot_selections"].submit()',
        'month_list': lot_month_list,
        'status_list': lot_status_list,
        # fix this javascript...
    }, **STATUS_BUTTONS),
}
def build_filter_kwargs(qdict, default):
    string_kwargs = {}
    
    for key in qdict.keys():
        if key == 'page':
            pass
        elif key == 'search_string':
            pass
        else:
            keyword = '%s__in' % (key)
            string_kwargs[str(keyword)] = [] 
            for key_arg in qdict.getlist(key):
                string_kwargs[keyword].append(str(key_arg))

    return string_kwargs

@login_required
def lots_by_month(request, year, month):
    queryset = Lot.objects.filter(date__year=year, date__month=month)
    date_field = 'date'
    month_list = Lot.objects.all().dates(date_field, 'month').reverse()
    return archive_index(
        request,
        queryset = queryset,
        date_field = date_field,
        num_latest = 3000,
        extra_context = dict({
            'page_title': 'QC Lots - %s %s' % (MONTHS[month], year),
            'print_link': 'javascript:document.forms["lot_selections"].submit()',
            'month_list': lot_month_list,
            'status_list': lot_status_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def retains_by_month(request, year, month):
    queryset = Retain.objects.filter(date__year=year, date__month=month)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'QC Retains - %s %s' % (MONTHS[month], year),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def retains_by_day(request, year, month, day):
    queryset = Retain.objects.filter(date__year=year, date__month=month, date__day=day)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'QC Retains - %s %s %s' % (MONTHS[month], day, year),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def retains_by_status(request, status):
    queryset = Retain.objects.filter(status=status)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'QC Retains - %s' % (status),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def rm_retains_by_month(request, year, month):
    queryset = RMRetain.objects.filter(date__year=year, date__month=month)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'RMs Retains - %s %s' % (MONTHS[month], year),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': rm_retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def rm_retains_by_day(request, year, month, day):
    queryset = RMRetain.objects.filter(date__year=year, date__month=month, date__day=day)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'RM Retains - %s %s %s' % (MONTHS[month], day, year),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': rm_retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def rm_retains_by_supplier(request,supplier):
    queryset = RMRetain.objects.filter(supplier=supplier)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'RM Retains - %s' % (supplier),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': rm_retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def rm_retains_by_status(request, status):
    queryset = RMRetain.objects.filter(status=status)
    date_field = 'date'
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset = queryset,
        extra_context = dict({
            'page_title': 'RM Retains - %s' % (status),
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': rm_retain_month_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )
    
@login_required
def lots_by_status(request, status):
    queryset = Lot.objects.filter(status=status)
    return list_detail.object_list(
        request,
        queryset = queryset,
        paginate_by = 100,
        extra_context = dict({
            'page_title': 'QC Lots -- %s' % status,
            'print_link': 'javascript:document.forms["retain_selections"].submit()',
            'month_list': lot_month_list,
            'status_list': lot_status_list,
            # fix this javascript...
        }, **STATUS_BUTTONS),
    )

def build_navbar(currentpath):
    splitpath = currentpath.rsplit("/")

def get_last_retain_number():
    current_retains = Retain.objects.filter(date__year=datetime.date.today().year)
    try:
        last_retain = current_retains[0]
    except:
        return 0
    return last_retain.retain

# TODO
def add_objects(request, page_title, ObjectClass, NewObjectForm):
    if request.method == 'GET':
        addobjectsbatch = AddObjectsBatch(request.GET)
        if addobjectsbatch.is_valid():
            number_of_objects = addobjectsbatch.cleaned_data['number_of_objects']
            extra, initial = NewObjectForm.prepare_formset_kwargs(number_of_objects)
            ObjectFormSet = formset_factory(NewObjectForm, 
                                            extra=extra)
            formset = ObjectFormSet(initial=initial)
            return render_to_response(NewObjectForm.template_path, 
                                      {'formset': formset,
                                       'page_title': page_title},
                                      context_instance=RequestContext(request))
        else:
            addobjectsbatch = AddObjectsBatch()
            return render_to_response('qc/add_objects_batch.html',
                                      {'addobjectsbatch': addobjectsbatch,
                                       'page_title': page_title},
                                      context_instance=RequestContext(request))
            
    
    elif request.method == 'POST':
        ObjectFormSet = formset_factory(NewObjectForm)
        formset = ObjectFormSet(request.POST)
        if formset.is_valid():
            td = datetime.date.today()
            for form in formset.forms:
                cd = form.cleaned_data
                cd['date'] = td
                obj = form.create_from_cleaned_data()
                obj.save()
            return HttpResponseRedirect(ObjectClass.browse_url)
        else:
            return render_to_response('qc/add_objects_batch.html', 
                                      {'formset': formset,
                                       'page_title': page_title},
                                      context_instance=RequestContext(request))


@login_required
def add_retains(request):
    #def add_objects(request, page_title, ObjectClass, NewObjectForm):
    return add_objects(request, page_title="Add Retains", ObjectClass=Retain, NewObjectForm=NewFlavorRetainForm)

@login_required
def add_rm_retains(request):
    return add_objects(request, page_title="Add RM Retains", ObjectClass=RMRetain, NewObjectForm=NewRMRetainForm)

@login_required
def add_receiving_log(request):
    return add_objects(request, page_title="Add To Receiving Log", ObjectClass=ReceivingLog, NewObjectForm=NewReceivingLogForm)

def ajax_retain_status_change(request):
    rm_re = re.compile('rm_retains')
    match = rm_re.search(request.META['HTTP_REFERER'])
    if match:
        Retain_Type = RMRetain
    else:
        Retain_Type = Retain
    json_list = request.POST.get('retain_list').split('|')
    new_status = request.POST.get('new_status')
    for pk in json_list:
        r = Retain_Type.objects.get(pk=pk)
        r.status=new_status
        r.save()
    return HttpResponse(
        simplejson.dumps(json_list)                    
    )

def target_sorter(checklist_row):
    try:
        return checklist_row[1][0]
    except IndexError:
        return None

@login_required
def batch_print(request):
    if request.method == 'POST':
        referer_re = re.compile('rm_retains')
        match = referer_re.search(request.META['HTTP_REFERER'])
        if match:
            retain_checklist = []
            retain_pks = request.POST.getlist('retain_pks')
            for pk in retain_pks:
                pin = RMRetain.objects.get(pk=pk).pin
                retain_checklist.append(build_rm_checklist_row(pin))
            
            retain_checklist.sort(key=target_sorter, reverse=True)  
            return render_to_response('qc/ingredient/batch_print.html', 
                                  {
                                   'retain_pks':retain_pks,
                                   'retain_checklist':retain_checklist,
                                   },
                                  context_instance=RequestContext(request))
        else:
            retain_checklist = []
            retain_pks = request.POST.getlist('retain_pks')
            for pk in retain_pks:
                f = Retain.objects.get(pk=pk).lot.flavor
                retain_checklist.append(build_checklist_row(f))
            
            retain_checklist.sort(key=target_sorter, reverse=True)  
            return render_to_response('qc/flavors/batch_print.html', 
                                  {
                                   'retain_pks':retain_pks,
                                   'retain_checklist':retain_checklist,
                                   },
                                  context_instance=RequestContext(request))

def build_checklist_row(flavor):
    return (flavor, flavor.retain_superset().order_by('-date').filter(status="Passed").values_list('date', 'retain', 'notes',)[:2])

def build_rm_checklist_row(pin):
    return (pin, RMRetain.objects.filter(pin=pin).order_by('-date').filter(status="Passed").values_list('date', 'r_number', 'notes',)[:2])
#@login_required
#def analyze_scanned_cards(request):
#    if request.method == 'POST':
#        tc = scan_card()
#        if tc != False:
#            card_thumb = get_thumbnail(tc.large.file, '800')
#            return HttpResponse(
#                simplejson.dumps({
#                    'preview': '<div><img src="%s"></div>' % card_thumb.url,
#                    
#                }), 
#                content_type='application//json; charset=utf-8')
#        else:
#            return HttpResponse(
#                simplejson.dumps({
#                    'preview': '<div><img src="/djangomedia/images/Icons/128x128/delete.png"></div>',
#                    'fail': 'fail'          
#                    
#                }), 
#                content_type='application//json; charset=utf-8')
#
#    return render_to_response('qc/analyze_scanned_cards.html',
#                              {},
#                              context_instance=RequestContext(request))
    
@login_required
def scrape_testcards(request):
    walk_scans_qccards.delay(walk_paths=['/srv/samba/tank/scans/qccards','/srv/samba/tank/scans/batchsheets'])
    return render_to_response('qc/scrape_testcards.html',
                              {},
                              context_instance=RequestContext(request))
    
    
@login_required
def analyze_scanned_cards(request):
    if request.method == 'POST':
        pass
    
    return render_to_response('qc/analyze_scanned_cards.html',
                              {},
                              context_instance=RequestContext(request))
    
def get_barcode(request, retain_pk):
    barode_string = "RETAIN-%s" % str(retain_pk)
    x = barcode('qrcode', barode_string, options=dict(version=4, eclevel='M'),margin=0, data_mode='8bits')
    #x = barcodeImg(codeBCFromString(str(retain_pk)))
    response = HttpResponse(mimetype="image/png")
    x.save(response, "PNG")
    return response

def get_rm_barcode(request, retain_pk):
    barode_string = "RM-%s" % str(retain_pk)
    x = barcode('qrcode', barode_string, options=dict(version=4, eclevel='M'),margin=0, data_mode='8bits')
    #x = barcodeImg(codeBCFromString(str(retain_pk)))
    response = HttpResponse(mimetype="image/png")
    x.save(response, "PNG")
    return response

@login_required
@flavor_info_wrapper
def flavor_history_print(request, flavor):
    page_title = "Flavor Retain History"
    lots = flavor.lot_set.all()[:20]
    context_dict = {
                   'flavor': flavor,
                   #'help_link': help_link,
                   'page_title': page_title,
                   #'weight_factor': weight_factor,
                   #'formula_weight': formula_weight,
                   'lots': lots,
                   }
    return render_to_response('qc/flavors/flavor_history_print.html',
                              context_dict,
                              context_instance=RequestContext(request))

#@login_required
#def resolve_retains_any(request):
#    if request.method == 'POST':
#        f = ResolveRetainForm(request.POST, instance=Retain.objects.get(pk=request.session['retainpk']))
#        if f.is_valid():
#            f.save()
#    try:
#        retain = Retain.objects.filter(status='Pending')[0]
#    except:
#        return HttpResponseRedirect('/django/qc/pending_retains/')
#    request.session['retainpk'] = retain.pk
#    f = ResolveRetainForm(instance=retain)
#    # preview_image = get_thumbnail(test_card.large.file, '800')
#    return render_to_response('qc/retains/resolve.html', 
#                              {
#                               # 'preview_image': preview_image,
#                               'form':f,
#                               'page_title': 'Resolve Retain',
#                               },
#                              context_instance=RequestContext(request))
    
def resolve_retains_any(request):
    try:
        tcs = TestCard.objects.exclude(retain=None).filter(status='Not Passed...')
        testcard = tcs[0]
        testcard_ondeck = tcs[1]
    except:
        return HttpResponseRedirect('/django/qc/')
    
@login_required
def batchsheet_detail(request, lot_pk):
    lot = get_object_or_404(Lot, pk=lot_pk)
    return render_to_response('qc/batchsheets/detail.html',
                              {'lot':lot})

@login_required
def lot_detail(request, lot_pk):
    lot = get_object_or_404(Lot, pk=lot_pk)
    return render_to_response('qc/lots/detail.html',
                              {'lot':lot,
                               'page_title':"Lot %s  --  Issued: %s  --  Status: %s"% (lot.number, lot.date.strftime('%B, %d %Y'), lot.status)},
                              context_instance=RequestContext(request))


@login_required
def old_lot_detail(request, lot_pk):
    lot = get_object_or_404(Lot, pk=lot_pk)
    if request.method == 'POST':
        post_data = simplejson.loads(request.raw_post_data)
        
        product_info_data = post_data['product_info_form']
        product_info = ProductInfo.objects.get(pk=product_info_data['productinfo_pk'])
        changed = False
        for attr in ('organoleptic_properties','appearance','notes','testing_procedure'):
            if product_info_data[attr] != getattr(product_info, attr):
                setattr(product_info, attr, product_info_data[attr])
                changed=True
        if changed:
            product_info.save()
            
        keys = post_data.keys()
        keys.remove('product_info_form')
        for k in keys:
            testcard_info_data = post_data[k]
            testcard = TestCard.objects.get(pk=testcard_info_data['instance_pk'])
            changed = False
            for attr in ('status','notes',):
                if testcard_info_data[attr] != getattr(testcard,attr):
                    setattr(testcard, attr, testcard_info_data[attr])
                    changed=True
            if changed:
                testcard.save()
            

    request.session['lotpk'] = lot_pk
    f = ResolveLotForm(instance=lot)
    product_info,created = ProductInfo.objects.get_or_create(flavor=lot.flavor)
    product_info_form = ProductInfoForm(instance=product_info)
    return render_to_response('qc/lots/detail.html',
                              {
                               'form':f,
                               'product_info_form':product_info_form,
                               'page_title': 'Lot Detail',
                               },
                              context_instance=RequestContext(request))

@login_required
def resolve_retains_specific(request, retain_pk):
    
    retain = get_object_or_404(Retain, pk=retain_pk)
    
    if request.method == 'POST':
        f = ResolveRetainForm(request.POST, instance=retain)
        if f.is_valid():
            f.save()
    
    request.session['retainpk'] = retain.pk
    f = ResolveRetainForm(instance=retain)
    # preview_image = get_thumbnail(test_card.large.file, '800')
    return render_to_response('qc/retains/resolve.html', 
                              {
                               # 'preview_image': preview_image,
                               'form':f,
                               'page_title': 'Resolve Retain',
                               },
                              context_instance=RequestContext(request))

def testcard_list(request):
    queryset = TestCard.objects.all()
    return list_detail.object_list(
        request,
        paginate_by=100,
        queryset=queryset,
        extra_context=dict({
            'page_title': "Test Card List",
        })
    )
    
def resolve_testcards_ajax_post(request):
    if request.is_ajax():
        testcard = TestCard.objects.get(pk=request.POST['instance_pk'])
        productinfo = ProductInfo.objects.get(pk=request.POST['productinfo_pk'])
        f = ResolveTestCardForm(request.POST, instance=testcard)
        product_info_form = ProductInfoForm(request.POST, prefix="product_info", instance=productinfo)
        if f.is_valid():
            f.save()
            product_info_form.save()
            #testcard = TestCard.objects.filter(status='Pending')[1]
            testcard = TestCard.objects.exclude(retain=None).filter(status='Not Passed...')[1]
            testcard_form = ResolveTestCardForm(instance=testcard)
            productinfo,created = ProductInfo.objects.get_or_create(flavor=testcard.retain.lot.flavor)
            productinfo_form = ProductInfoForm(prefix="product_info",instance=productinfo)
            return render_to_response(
                'qc/testcards/resolve_testcard_form.html',
                {'testcard_form':testcard_form,
                 'productinfo_form':productinfo_form,
                 'divclass':'ondeck'},
                context_instance=RequestContext(request),                 
            )
    
    

@login_required
def resolve_testcards_any(request):
    try:
        tcs = TestCard.objects.exclude(retain=None).filter(status='Not Passed...')
        testcard = tcs[0]
        testcard_ondeck = tcs[1]
    except:
        return HttpResponseRedirect('/django/qc/no_testcards_left/')
    return render_to_response('qc/testcards/resolve.html', 
                              {
                               'testcard':testcard,
                               'testcard_ondeck':testcard_ondeck,
                               'page_title': 'Resolve Test Card',
                               },
                              context_instance=RequestContext(request))
    
@login_required
def resolve_testcards_specific(request, testcard_pk):
    
    testcard = get_object_or_404(TestCard, pk=testcard_pk)
    
    if request.method == 'POST':
        f = ResolveTestCardForm(request.POST, instance=testcard)
        if f.is_valid():
            f.save()
    
    return render_to_response('qc/testcards/resolve.html', 
                              {
                               'testcard':testcard,
                               'testcard_ondeck':None,
                               'page_title': 'Resolve Test Card',
                               },
                              context_instance=RequestContext(request))

def passed_finder(request):
    if request.method == "POST":
        all_testcard_pks = []
        checked_pks = []
        for s in request.POST.getlist('all_testcards'):
            all_testcard_pks.append(int(s))
        for s in request.POST.getlist('testcards'):
            checked_pks.append(int(s))
  
        for tc in TestCard.objects.filter(pk__in=all_testcard_pks):
            if tc.pk in checked_pks:
                tc.status = "Passed"
                tc.save()
            else:
                tc.status = "Not Passed..."
                tc.save()

    
    testcards = TestCard.objects.filter(status="Pending")[0:10]
    return render_to_response('qc/testcards/passed_finder.html',
                              {'testcards':testcards},
                              context_instance=RequestContext(request))

def last_chance(request):
   
    return render_to_response('qc/retains/last_chance.html',
                              {
                               
                               },
                              context_instance=RequestContext(request))
    

def review(request):
    return render_to_response('qc/review.html')

def receiving_log_print(request):
    # TODO
    return


#to generate pngs from a pdf file
# convert -geometry 3000x3000 -density 300x300 -quality 100 test.pdf testdf.png

# to generate a card thumbnail
# convert testdf-0.png -resize 15% testdf-0-small.png

#
#def logger_test(request):
#    logging.basicConfig(filename='/usr/local/django/fd/curlprinter.log', level=logging.INFO)
#    
#    result = logger_test_task.delay(request.META['QUERY_STRING'])
#    result.wait()
#    logging.info('Request result: %s' % result.result)
#    return render_to_response('base.html',
#                              {"page_title":result.result})
#    