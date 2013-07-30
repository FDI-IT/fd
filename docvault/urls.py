import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

from docvault.models import Doc
doc_list_info = {
        'queryset':Doc.objects.all(),
        'pageinate_by':100,
        'extra_context': dict({
            'page_title': 'Scanned Docs',
        },)
    }

urlpatterns = patterns('newqc.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', redirect_to, {'url': '/django/docvault/docs/'}),
    (r'^docs/$', login_required(list_detail.object_list), doc_list_info),
    
#    (r'^lots/$', login_required(list_detail.object_list), lot_list_info),
#    (r'^lots/(\d{4})/(\d{2})/$', 'lots_by_month'),
#    (r'^lots/(?P<lot_pk>\d+)/$', 'lot_detail'),
#    (r'^lots/(?P<status>\w+)/$', 'lots_by_status'),
#    
#    (r'^retains/$', login_required(list_detail.object_list), retain_list_info),
#    (r'^retains/(\d{4})/(\d{2})/$', 'retains_by_month'),
#    (r'^retains/today/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(date=datetime.date.today()),
#                                                                    'extra_context': dict({
#                                                                        'page_title': 'QC Retains',
#                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
#                                                                        'month_list': retain_month_list,
#                                                                    }, **STATUS_BUTTONS),}),
#    (r'^retains/today/not_passed/$', login_required(list_detail.object_list), {'queryset':Retain.objects.filter(date=datetime.date.today()).filter(~Q(status="Passed")),
#                                                                    'extra_context': dict({
#                                                                        'page_title': 'QC Retains',
#                                                                        'print_link': 'javascript:document.forms["retain_selections"].submit()',
#                                                                        'month_list': retain_month_list,
#                                                                    }, **STATUS_BUTTONS),}),

)
