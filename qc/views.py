from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from fd.qc.models import Retain
from fd.flavorbase.models import Flavor
from django.core.paginator import Paginator, InvalidPage, EmptyPage
import time
from django.views.generic import list_detail
import datetime
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect, HttpResponse
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
import logging
from fd.qc.forms import *
from django.template.loader import get_template
import sys
from django.contrib.auth.decorators import login_required
from django.db import connection

#LOG_FILENAME = '/home/stachurski/workspace/FDI/fd/qc/import.log'
#if(os.path.exists(LOG_FILENAME)):
#    os.remove(LOG_FILENAME)
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

def build_navbar(currentpath):
    splitpath = currentpath.rsplit("/")


def get_last_retain():
    current_year = time.localtime()[0]
    current_retains = Retain.objects.filter(date__year=2009)
    last_retain = current_retains[0]
    return last_retain

@login_required
def addretains(request):
    try: 
        last_retain = get_last_retain().retain
    except:
        last_retain = 0
    valid_form = False
    FlavorRetainFormSet = formset_factory(NewFlavorRetainForm, extra=20,
                                         formset=BaseFlavorFormSet)
    if request.method == 'POST':
        formset = FlavorRetainFormSet(request.POST, request.FILES)
        if formset.is_valid():
            valid_form = True
            for form in formset.forms:
                print form.cleaned_data
                try:

                    sampled_flavor = get_object_or_404(Flavor,
                                                       pk=form.cleaned_data['flavor_choice'])
                    last_retain+=1
                    sampled_flavor.retains.create(
                                        retain=last_retain,
                                        date=datetime.date.today(),
                                        lot=form.cleaned_data['lot'],
                                        sub_lot=form.cleaned_data['sub_lot'],
                                        status="Pending",
                                        amount=form.cleaned_data['amount'])

                except Exception, err:
                    print err
                    print err.message

            
            return HttpResponseRedirect('/qc/')

    else:
        formset = FlavorRetainFormSet()

    return render_to_response('qc/addretains.html', 
                              {'current_retain': last_retain,
                               'formset': formset,
                               'valid_form': valid_form,
                               'pagetitle': 'Add Retains'},
                              context_instance=RequestContext(request))

def build_filter_kwargs(qdict):
    string_kwargs = {}
    for key in qdict.keys():
        if key == 'page':
            pass
        else:
            keyword = '%s__in' % (key)
            string_kwargs[str(keyword)] = [] 
            for key_arg in qdict.getlist(key):
                string_kwargs[keyword].append(str(key_arg))

    return string_kwargs

@login_required
def index(request):
    RetainStatusFormSet = modelformset_factory(Retain,
                                               RetainStatusChangeForm,
                                               extra=0)

    if request.method == 'GET':
        if len(request.GET.items()) == 0:
            statusselect = RetainFilterSelectForm({'status':['Pending',]})
            CustomQuerySet = Retain.objects.select_related().filter(status="Pending")
        else:
            statusselect = RetainFilterSelectForm(request.GET)
            CustomQuerySet = Retain.objects.select_related().filter(
                **build_filter_kwargs(request.GET))

    paginator = Paginator(CustomQuerySet, 50)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    try:
        retains = paginator.page(page)
    except (EmptyPage, InvalidPage):
        retains = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        print request.POST
        formset = RetainStatusFormSet(request.POST, request.FILES,)
        if formset.is_valid():
            instances = formset.save()
            return HttpResponseRedirect('/qc')
    else:
        formset = RetainStatusFormSet(queryset=retains.object_list)

    return render_to_response('qc/index.html', 
                              {'formset': formset,
                               'statusselect': statusselect,
                               'list_items': retains,
                               'pagetitle': 'QC Retains'},
                              context_instance= RequestContext(request))


@login_required
def retains_by_status(request, status):

    cursor = connection.cursor()
    cursor.execute("""
                   SELECT DISTINCT status
                   FROM qc_retain""")

    return list_detail.object_list(
        request,
        queryset = Retain.objects.filter(status__iexact=status),
        paginate_by = 50,
        template_name = "qc/retains_by_status.html",
        template_object_name = "retain",
        extra_context = {"status": status,
                         "statuslinks": cursor.fetchall(),}
    )
