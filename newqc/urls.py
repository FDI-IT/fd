import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to, direct_to_template
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

from newqc.models import Retain, Lot
from newqc.views import STATUS_BUTTONS, retain_list_info, rm_retain_list_info, lot_list_info, retain_month_list, lot_list_attn, batchsheet_list_info, receiving_log_list_info

urlpatterns = patterns('newqc.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', redirect_to, {'url': '/django/qc/retains/'}),
    (r'^review/$', 'review'),
    (r'^add_retains/$', 'add_retains'),
    (r'^batch_print/$', 'batch_print'),
    (r'^scrape_testcards/$', 'scrape_testcards'),
    (r'^analyze_scanned_cards/$', 'analyze_scanned_cards'),
    (r'^barcode/rm/(?P<retain_pk>\d+)/$', 'get_rm_barcode'),
    (r'^barcode/(?P<retain_pk>\d+)/$', 'get_barcode'),
    (r'^batchsheets/$', list_detail.object_list, batchsheet_list_info),
    (r'^batchsheets/(?P<lot_pk>\d+)/$$', 'batchsheet_detail'),
    (r'^lots/$', 'lot_list'),
    (r'^lots/paginate(?P<paginate_by>\d+)/$', 'lot_list'),
    (r'^lots_requiring_attention/$', login_required(list_detail.object_list), lot_list_attn),
    (r'^lots/(\d{4})/(\d{2})/$', 'lots_by_month'),
    (r'^lots/(?P<lot_pk>\d+)/$', 'lot_detail'),
    (r'^lots/(?P<status>\w+)/$', 'lots_by_status'),
    
    (r'^retains/$', login_required(list_detail.object_list), retain_list_info),
    (r'^retains/(\d{4})/(\d{2})/$', 'retains_by_month'),
    (r'^retains/(\d{4})/(\d{2})/(\d{2})/$', 'retains_by_day'),
    (r'^retains/(\w+)/$', 'retains_by_status'),
    (r'^retains/today/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(date=datetime.date.today()),
                                                                    'extra_context': dict({
                                                                        'page_title': 'QC Retains',
                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
                                                                        'month_list': retain_month_list,
                                                                    }, **STATUS_BUTTONS),}),

    
    
    (r'^add_rm_retains/$', 'add_rm_retains'),
    (r'^rm_retains/$', login_required(list_detail.object_list), rm_retain_list_info),
    (r'^rm_retains/(\d{4})/(\d{2})/$', 'rm_retains_by_month'),
    (r'^rm_retains/(\d{4})/(\d{2})/(\d{2})/$', 'rm_retains_by_day'),
    (r'^rm_retains/supplier/(\w+)/$', 'rm_retains_by_supplier'),
    (r'^rm_retains/(\w+)/$', 'rm_retains_by_status'),
    
    
    (r'^ajax_retain_status_change/$', 'ajax_retain_status_change'),
    

    (r'^flavors/(?P<flavor_number>\d+)/print/$', 'flavor_history_print'),
    
    (r'^resolve_retains/$', 'resolve_retains_any'),
    (r'^resolve_retains/(?P<retain_pk>\d+)/$', 'resolve_retains_specific'),
    
    (r'^resolve_testcards/$', 'resolve_testcards_any'),
    (r'^resolve_testcards_ajax_post/$', 'resolve_testcards_ajax_post'),
    (r'^resolve_testcards/(?P<testcard_pk>\d+)/$', 'resolve_testcards_specific'),
    (r'^testcard_list/$', 'testcard_list'),
    (r'^passed_finder/$', 'passed_finder'),
    (r'^no_testcards_left/$', direct_to_template, {'template':'qc/no_testcards_left.html'}),
    
    
    (r'^receiving_log/$', login_required(list_detail.object_list), receiving_log_list_info),
    (r'^receiving_log_print/$', 'receiving_log_print'),
    (r'^add_receiving_log/$', 'add_receiving_log'),
)
