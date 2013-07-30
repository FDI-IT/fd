import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

from newqc.models import Retain, Lot
from newqc.views import STATUS_BUTTONS, retain_list_info, lot_list_info, retain_month_list

urlpatterns = patterns('newqc.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', redirect_to, {'url': '/django/qc/retains/'}),
    (r'^add_retains/$', 'add_retains'),
    (r'^batch_print/$', 'batch_print'),
    (r'^analyze_scanned_cards/$', 'analyze_scanned_cards'),
    (r'^barcode/(?P<retain_pk>\d+)/$', 'get_barcode'),
    
    (r'^lots/$', login_required(list_detail.object_list), lot_list_info),
    (r'^lots/(\d{4})/(\d{2})/$', 'lots_by_month'),
    (r'^lots/(?P<lot_pk>\d+)/$', 'lot_detail'),
    (r'^lots/(?P<status>\w+)/$', 'lots_by_status'),
    
    (r'^retains/$', login_required(list_detail.object_list), retain_list_info),
    (r'^retains/(\d{4})/(\d{2})/$', 'retains_by_month'),
    (r'^retains/today/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(date=datetime.date.today()),
                                                                    'extra_context': dict({
                                                                        'page_title': 'QC Retains',
                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
                                                                        'month_list': retain_month_list,
                                                                    }, **STATUS_BUTTONS),}),
    (r'^retains/today/not_passed/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(date=datetime.date.today()).filter(~Q(status="Passed")),
                                                                    'extra_context': dict({
                                                                        'page_title': 'QC Retains',
                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
                                                                        'month_list': retain_month_list,
                                                                    }, **STATUS_BUTTONS),}),
    
    (r'^retains/pending/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(status="Pending"),
                                                                    'extra_context': dict({
                                                                        'page_title': 'QC Retains',
                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
                                                                        'month_list': retain_month_list,
                                                                    }, **STATUS_BUTTONS),}),
    
    (r'^ajax_retain_status_change/$', 'ajax_retain_status_change'),
    
    (r'^flavors/(?P<flavor_number>\d+)/$', 'flavor_history'),
    (r'^flavors/(?P<flavor_number>\d+)/print/$', 'flavor_history_print'),
    
    (r'^resolve_retains/$', 'resolve_retains_any'),
    (r'^resolve_retains/(?P<retain_pk>\d+)/$', 'resolve_retains_specific'),
    
    (r'^resolve_testcards/$', 'resolve_testcards_any'),
    (r'^resolve_testcards/(?P<testcard_pk>\d+)/$', 'resolve_testcards_specific'),
)
