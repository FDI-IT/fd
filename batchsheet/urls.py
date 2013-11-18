import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

urlpatterns = patterns('batchsheet.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'batchsheet_home'),
    (r'^batchsheet_print/(?P<flavor_number>\d+)/$', 'batchsheet_print'),
    (r'^lot_init/$', 'lot_init'),
    (r'^next_lot/$', 'next_lot'),
    (r'^lot_notebook/$', 'lot_notebook'),
    (r'^barcode/(?P<barcode_contents>[a-zA-Z0-9_-]+)/$', 'get_barcode'),
    (r'^sales_orders/$', 'sales_order_list'),
    (r'^add_lots/$', 'add_lots'),
    (r'^update_lots/$', 'update_lots'),
    (r'^update_lots/(?P<lot_pk>\d+)/(?P<amount>\d+(\.\d{1,2})?)/$', 'update_lots'),
    (r'^lot_update_confirmation/$', 'lot_update_confirmation'),
    (r'^batchsheet_batch_print/$', 'batchsheet_batch_print'),
    (r'^check_lot_number/$', 'check_lot_number'),

)
#(r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),