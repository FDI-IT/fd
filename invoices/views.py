from decimal import Decimal, ROUND_HALF_UP
import json
import operator
import re
from datetime import date
from operator import itemgetter

from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.utils import simplejson
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.utils.functional import wraps
from django.template import RequestContext
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Sum
from django.views.generic.date_based import archive_day


from reversion import revision

from access.models import Flavor

from invoices.utils import parse_report, parse_report_lw
from invoices.forms import InvoiceReportFileForm
from invoices.models import Invoice,LineItem

@login_required
def upload_report(request):
    if request.method =='POST':
        form = InvoiceReportFileForm(request.POST, request.FILES)
        if form.is_valid():
            total_rmc, flavors_ordered = parse_report(request.FILES['file'])
        return render_to_response('invoices/summary.html',
                                  {
                                   'total_rmc': total_rmc,
                                   'flavors_ordered': flavors_ordered,
                                   },
                                  context_instance=RequestContext(request))
    else:
        form = InvoiceReportFileForm()
    return render_to_response('invoices/upload_report.html', 
                              {'form':form}, 
                              context_instance=RequestContext(request))


@login_required
def upload_report_lw(request):
    if request.method =='POST':
        form = InvoiceReportFileForm(request.POST, request.FILES)
        if form.is_valid():
            total_rmc, flavors_ordered = parse_report_lw(request.FILES['file'])
        return render_to_response('invoices/summary.html',
                                  {
                                   'total_rmc': total_rmc,
                                   'flavors_ordered': flavors_ordered,
                                   },
                                  context_instance=RequestContext(request))
    else:
        form = InvoiceReportFileForm()
    return render_to_response('invoices/upload_report_lw.html', 
                              {'form':form}, 
                              context_instance=RequestContext(request))


# for x in models.Invoice.objects.values('qb_date').annotate(Sum("lineitem__quantity_cost")).order_by('qb_date'):
#    print x

@login_required
@permission_required('invoice.change_invoice')
def date_detail(request,year,month,day):
    d = date(year=int(year),month=int(month),day=int(day))
    queryset = LineItem.objects.filter(invoice__qb_date=d).order_by('invoice__number')
    return render_to_response('invoices/invoice_archive_day.html',
                              {'queryset':queryset,
                               'd':d},
                              context_instance=RequestContext(request))

@login_required
@permission_required('invoice.change_invoice')
def date_summary(request):
    date_data = Invoice.objects.values('qb_date').annotate(Sum("lineitem__quantity_cost")).order_by('qb_date')
    return render_to_response('invoices/date_summary.html',
                              {
                               'date_data':date_data,
                               },
                              context_instance=RequestContext(request))

@login_required
@permission_required('invoice.change_invoice')
def invoice_archive_day(request, year, month, day):
    queryset = Invoice.objects.all()
    return archive_day(
            request,
            year=year,
            month=month,
            day=day,
            queryset=queryset,
            date_field='qb_date',
            extra_context=dict({
                'page_title':"Invoices by date -- %s-%s-%s" % (year,month,date),
                
            },),
            allow_empty=True,
        )

#@login_required 
#def summary(request):
#    page_title="Invoice Summary"
#    # the invoices version of parse_orders hasn't been written yet
#    good_orders, bad_orders = parse_orders()
#    return render_to_response('invoices/summary.html',
#                              {
#                               'good_orders':good_orders,
#                               'bad_orders':bad_orders,
#                               'page_title':page_title,
#                               'window_title':page_title,
#                               },
#                              context_instance=RequestContext(request))