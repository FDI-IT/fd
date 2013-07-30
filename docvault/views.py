## TODO: RETURN THE PATH OF PREVIEW AND FULL
##        ADD THE FULL IMAGE TO A HIDDEN ELEMENT
##        FADE EFFECT BETWEEN IMAGES WHEN FORMS SWITCH FOCUSx
#
## TODO: retain checklist to pull targets.
#
#import datetime
#import sys
#import logging
#import hashlib
#import os 
#
#from django.shortcuts import render_to_response, get_object_or_404
#from django.utils import simplejson
#from django.http import Http404
#from django.core.paginator import Paginator, InvalidPage, EmptyPage
#from django.views.generic import list_detail
#from django.views.generic.date_based import archive_index
#from django.template import RequestContext, Context
#from django.http import HttpResponseRedirect, HttpResponse
#from django.forms.formsets import formset_factory
#from django.forms.models import modelformset_factory
#from django.template.loader import get_template
#from django.contrib.auth.decorators import login_required
#from django.db import connection
#from django.contrib.contenttypes.models import ContentType
#
#from sorl.thumbnail import get_thumbnail
#
#from elaphe import barcode
#
#from access.barcode import barcodeImg, codeBCFromString
#from access.models import Flavor
#from access.views import flavor_info_wrapper
#from newqc.forms import NewFlavorRetainForm, AddRetainBatch, ResolveTestCardForm, RetainStatusForm, ResolveRetainForm, ResolveLotForm
#from newqc.models import Retain, ProductInfo, TestCard, Lot
#from newqc.utils import process_jbg, get_card_file, scan_card
#from newqc.tasks import CurlPrinter
#
#def lot_month_list():
#    return Lot.objects.all().dates('date', 'month').reverse()
#
#def retain_month_list():
#    return Retain.objects.all().dates('date', 'month').reverse()
#
#def lot_status_list():    
#    cursor = connection.cursor()
#    cursor.execute('select distinct "newqc_lot"."status" from "newqc_lot"')
#    status_choices = []
#    for choice in cursor.fetchall():
#        status_choices.append(choice[0])
#
#    return status_choices
#
#MONTHS = {
#          '01':'January',
#          '02':'February',
#          '03':'March',
#          '04':'April',
#          '05':'May',
#          '06':'June',
#          '07':'July',
#          '08':'August',
#          '09':'September',
#          '10':'October',
#          '11':'November',
#          '12':'December',
#    }
#
#STATUS_BUTTONS =  {
#    'repeat_link': 'javascript:ajax_retain_status_change("Resample")',
#    'repeat_link_alt': 'Resample',
#    'pause_link': 'javascript:ajax_retain_status_change("Hold")',
#    'pause_link_alt': 'Hold',
#    'accept_link': 'javascript:ajax_retain_status_change("Passed")',
#    'accept_link_alt': 'Pass',
#    'del_link': 'javascript:ajax_retain_status_change("Rejected")',
#    'del_link_alt': 'Reject',
#}
#retain_list_info =  {
#    'queryset': Retain.objects.all(),
#    'paginate_by': 100,
#    'extra_context': dict({
#        'page_title': 'QC Retains',
#        'print_link': 'javascript:document.forms["retain_selections"].submit()',
#        'month_list': retain_month_list,
#        'admin_link': "/django/admin/newqc/retain/",
#    }, **STATUS_BUTTONS),
#}
#lot_list_info =  {
#    'queryset': Lot.objects.all(),
#    'paginate_by': 100,
#    'extra_context': dict({
#        'page_title': 'QC Lots',
#        'print_link': 'javascript:document.forms["lot_selections"].submit()',
#        'month_list': lot_month_list,
#        'status_list': lot_status_list,
#        # fix this javascript...
#    }, **STATUS_BUTTONS),
#}
#
#def build_filter_kwargs(qdict, default):
#    string_kwargs = {}
#    
#    for key in qdict.keys():
#        if key == 'page':
#            pass
#        elif key == 'search_string':
#            pass
#        else:
#            keyword = '%s__in' % (key)
#            string_kwargs[str(keyword)] = [] 
#            for key_arg in qdict.getlist(key):
#                string_kwargs[keyword].append(str(key_arg))
#
#    return string_kwargs
#
#@login_required
#def lots_by_month(request, year, month):
#    queryset = Lot.objects.filter(date__year=year, date__month=month)
#    date_field = 'date'
#    month_list = Lot.objects.all().dates(date_field, 'month').reverse()
#    return archive_index(
#        request,
#        queryset = queryset,
#        date_field = date_field,
#        num_latest = 3000,
#        extra_context = dict({
#            'page_title': 'QC Lots - %s %s' % (MONTHS[month], year),
#            'print_link': 'javascript:document.forms["lot_selections"].submit()',
#            'month_list': lot_month_list,
#            'status_list': lot_status_list,
#            # fix this javascript...
#        }, **STATUS_BUTTONS),
#    )
#    
#@login_required
#def retains_by_month(request, year, month):
#    queryset = Retain.objects.filter(date__year=year, date__month=month)
#    date_field = 'date'
#    return archive_index(
#        request,
#        queryset = queryset,
#        date_field = date_field,
#        num_latest = 3000,
#        extra_context = dict({
#            'page_title': 'QC Retains - %s %s' % (MONTHS[month], year),
#            'print_link': 'javascript:document.forms["retain_selections"].submit()',
#            'month_list': retain_month_list,
#            # fix this javascript...
#        }, **STATUS_BUTTONS),
#    )
#    
#@login_required
#def lots_by_status(request, status):
#    queryset = Lot.objects.filter(status=status)
#    return list_detail.object_list(
#        request,
#        queryset = queryset,
#        paginate_by = 100,
#        extra_context = dict({
#            'page_title': 'QC Lots -- %s' % status,
#            'print_link': 'javascript:document.forms["retain_selections"].submit()',
#            'month_list': lot_month_list,
#            'status_list': lot_status_list,
#            # fix this javascript...
#        }, **STATUS_BUTTONS),
#    )
#
#def build_navbar(currentpath):
#    splitpath = currentpath.rsplit("/")
#
#def get_last_retain_number():
#    current_retains = Retain.objects.filter(date__year=datetime.date.today().year)
#    try:
#        last_retain = current_retains[0]
#    except:
#        return 0
#    return last_retain.retain
#
#@login_required
#def add_retains(request):
#    page_title = "Add Retains"
#    status_message = ""
#    
#    if request.method == 'GET':
#        addretainbatch = AddRetainBatch(request.GET)
#        if addretainbatch.is_valid():
#            number_of_retains = addretainbatch.cleaned_data['number_of_retains']
#            
#            retain_formset_initial = []
#            last_retain_number = get_last_retain_number()+1
#            for new_retain_number in range(last_retain_number, last_retain_number+number_of_retains):
#                retain_formset_initial.append({'retain_number':new_retain_number})
#            
#            RetainFormSet = formset_factory(NewFlavorRetainForm, 
#                                            extra=0)
#            formset = RetainFormSet(initial=retain_formset_initial)
#            return render_to_response('qc/add_retains.html', 
#                                      {'formset': formset,
#                                       'page_title': page_title},
#                                      context_instance=RequestContext(request))
#        else:
#            addretainbatch = AddRetainBatch()
#            return render_to_response('qc/add_retain_batch.html',
#                                      {'addretainbatch': addretainbatch,
#                                       'page_title': page_title},
#                                      context_instance=RequestContext(request))
#            
#    
#    elif request.method == 'POST':
#        RetainFormSet = formset_factory(NewFlavorRetainForm)
#        formset = RetainFormSet(request.POST)
#        if formset.is_valid():
#            td = datetime.date.today()
#            for form in formset.forms:
#                cd = form.cleaned_data
#                lot_number = cd['lot_number']
#                f = Flavor.objects.get(number=cd['flavor_number'])
#                
#                try:
#                    l = Lot.objects.filter(number=lot_number, flavor=f)[0]
#                except:
#                    l = Lot(date=td,
#                            number=cd['lot_number'],
#                            status='Pending',
#                            amount=cd['weight'],
#                            flavor=f)
#                    l.save()
#                
#                r = Retain(retain=cd['retain_number'],
#                           lot=l,
#                           date=td,
#                           status='Pending',)
#                r.save()
#            return HttpResponseRedirect('/django/qc/retains/')
#        else:
#            return render_to_response('qc/add_retains.html', 
#                                      {'formset': formset,
#                                       'page_title': page_title},
#                                      context_instance=RequestContext(request))
#
#def ajax_retain_status_change(request):
#    json_list = request.POST.get('retain_list').split('|')
#    new_status = request.POST.get('new_status')
#    for pk in json_list:
#        r = Retain.objects.get(pk=pk)
#        r.status=new_status
#        r.save()
#    return HttpResponse(
#        simplejson.dumps(json_list)                    
#    )
#
#def target_sorter(checklist_row):
#    try:
#        return checklist_row[1][0]
#    except IndexError:
#        return None
#
#@login_required
#def batch_print(request):
#    if request.method == 'POST':
#        retain_checklist = []
#        retain_pks = request.POST.getlist('retain_pks')
#        for pk in retain_pks:
#            f = Retain.objects.get(pk=pk).lot.flavor
#            retain_checklist.append(build_checklist_row(f))
#        
#        retain_checklist.sort(key=target_sorter, reverse=True)  
#    return render_to_response('qc/flavors/batch_print.html', 
#                              {
#                               'retain_pks':retain_pks,
#                               'retain_checklist':retain_checklist,
#                               },
#                              context_instance= RequestContext(request))
#
#def build_checklist_row(flavor):
#    return (flavor, flavor.retain_superset().order_by('-date').filter(status="Passed").values_list('date', 'retain', 'notes',)[:2])
##@login_required
##def analyze_scanned_cards(request):
##    if request.method == 'POST':
##        tc = scan_card()
##        if tc != False:
##            card_thumb = get_thumbnail(tc.large.file, '800')
##            return HttpResponse(
##                simplejson.dumps({
##                    'preview': '<div><img src="%s"></div>' % card_thumb.url,
##                    
##                }), 
##                content_type='application//json; charset=utf-8')
##        else:
##            return HttpResponse(
##                simplejson.dumps({
##                    'preview': '<div><img src="/djangomedia/images/Icons/128x128/delete.png"></div>',
##                    'fail': 'fail'          
##                    
##                }), 
##                content_type='application//json; charset=utf-8')
##
##    return render_to_response('qc/analyze_scanned_cards.html',
##                              {},
##                              context_instance=RequestContext(request))
#    
#    
#@login_required
#def analyze_scanned_cards(request):
#    if request.method == 'POST':
#        try:
#            curlprinter.main()
#        except:
#            return HttpResponseRedirect('/djangomedia/js/blueimp-jQuery-File-Upload-2ac23c3/example/index.html')
##        return HttpResponse(simplejson.dumps({
##            ''}))
#    
#    return render_to_response('qc/analyze_scanned_cards.html',
#                              {},
#                              context_instance=RequestContext(request))
#    
#def get_barcode(request, retain_pk):
#    barode_string = "RETAIN-%s" % str(retain_pk)
#    x = barcode('qrcode', barode_string, options=dict(version=4, eclevel='M'),margin=0, data_mode='8bits')
#    #x = barcodeImg(codeBCFromString(str(retain_pk)))
#    response = HttpResponse(mimetype="image/png")
#    x.save(response, "PNG")
#    return response
#
#@login_required
#@flavor_info_wrapper
#def flavor_history(request, flavor):
##    queryset = Lot.objects.filter(status=status)
##    return list_detail.object_list(
##        request,
##        queryset = queryset,
##        paginate_by = 100,
##        extra_context = dict({
##            'page_title': 'QC Lots -- %s' % status,
##            'print_link': 'javascript:document.forms["retain_selections"].submit()',
##            'month_list': lot_month_list,
##            'status_list': lot_status_list,
##            # fix this javascript...
##        }, **STATUS_BUTTONS),
##    )
#    page_title = "Flavor Retain History"
#    queryset = flavor.lot_set.all()
#    return list_detail.object_list(
#            request,
#            queryset=queryset,
#            template_name="qc/flavors/flavor_history.html",
#            extra_context=dict({
#                   'request':request,
#                   'flavor': flavor,
#                   #'help_link': help_link,
#                   'page_title': page_title,
#                   'print_link': '/django/qc/flavors/%s/print/' % flavor.number,
#                   }, **STATUS_BUTTONS),)
#    
#@login_required
#@flavor_info_wrapper
#def flavor_history_print(request, flavor):
#    page_title = "Flavor Retain History"
#    lots = flavor.lot_set.all()[:20]
#    context_dict = {
#                   'flavor': flavor,
#                   #'help_link': help_link,
#                   'page_title': page_title,
#                   #'weight_factor': weight_factor,
#                   #'formula_weight': formula_weight,
#                   'lots': lots,
#                   }
#    return render_to_response('qc/flavors/flavor_history_print.html',
#                              context_dict,
#                              context_instance=RequestContext(request))
#
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
#    
#@login_required
#def lot_detail(request, lot_pk):
#    lot = get_object_or_404(Lot, pk=lot_pk)
#    if request.method == 'POST':
#        # form handling code
#        pass
#
#    request.session['lotpk'] = lot_pk
#    f = ResolveLotForm(instance=lot)
#    return render_to_response('qc/lots/detail.html',
#                              {
#                               'form':f,
#                               'page_title': 'Lot Detail',
#                               },
#                              context_instance=RequestContext(request))
#
#@login_required
#def resolve_retains_specific(request, retain_pk):
#    
#    retain = get_object_or_404(Retain, pk=retain_pk)
#    
#    if request.method == 'POST':
#        f = ResolveRetainForm(request.POST, instance=retain)
#        if f.is_valid():
#            f.save()
#    
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
#
#@login_required
#def resolve_testcards_any(request):
#    if request.method == 'POST':
#        f = ResolveTestCardForm(request.POST, instance=TestCard.objects.get(pk=request.session['tcpk']))
#        if f.is_valid():
#            f.save()
#    try:
#        test_card = TestCard.objects.filter(status='Pending')[0]
#    except:
#        return HttpResponseRedirect('/django/qc/pending_testcards/')
#    request.session['tcpk'] = test_card.pk
#    f = ResolveTestCardForm(instance=test_card)
#    preview_image = get_thumbnail(test_card.large.file, '800')
#    return render_to_response('qc/testcards/resolve.html', 
#                              {
#                               'preview_image': preview_image,
#                               'form':f,
#                               'page_title': 'Resolve Test Card',
#                               },
#                              context_instance=RequestContext(request))
#    
#@login_required
#def resolve_testcards_specific(request, testcard_pk):
#    
#    test_card = get_object_or_404(TestCard, pk=testcard_pk)
#    
#    if request.method == 'POST':
#        f = ResolveTestCardForm(request.POST, instance=test_card)
#        if f.is_valid():
#            f.save()
#    
#    request.session['tcpk'] = test_card.pk
#    f = ResolveTestCardForm(instance=test_card)
#    preview_image = get_thumbnail(test_card.large.file, '800')
#    return render_to_response('qc/testcards/resolve.html', 
#                              {
#                               'preview_image': preview_image,
#                               'form':f,
#                               'page_title': 'Resolve Test Card',
#                               },
#                              context_instance=RequestContext(request))
#    
##to generate pngs from a pdf file
## convert -geometry 3000x3000 -density 300x300 -quality 100 test.pdf testdf.png
#
## to generate a card thumbnail
## convert testdf-0.png -resize 15% testdf-0-small.png
#
##
##def logger_test(request):
##    logging.basicConfig(filename='/usr/local/django/fd/curlprinter.log', level=logging.INFO)
##    
##    result = logger_test_task.delay(request.META['QUERY_STRING'])
##    result.wait()
##    logging.info('Request result: %s' % result.result)
##    return render_to_response('base.html',
##                              {"page_title":result.result})
##    