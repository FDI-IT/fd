import datetime

from django.conf.urls import url, include
from django.db.models import Q, F

from batchsheet import views

urlpatterns = (
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', views.batchsheet_home),
    #url(r'^(?P<flavor_number>\d+)/batch_sheet/$', views.batch_sheet),
    url(r'^batchsheet_print/(?P<flavor_number>\d+)/$', views.batchsheet_print),
    url(r'^lot_init/$', views.lot_init),
    url(r'^next_lot/$', views.next_lot),
    url(r'^lot_notebook/$', views.lot_notebook),
    url(r'^barcode/(?P<barcode_contents>[a-zA-Z0-9_-]+)/$', views.get_barcode),
    url(r'^sales_orders/$', views.sales_order_list),
    url(r'^add_lots/$', views.add_lots),
    url(r'^update_lots/$', views.update_lots),
    url(r'^update_lots/(?P<lot_pk>\d+)/(?P<amount>\d+(\.\d{1,2})?)/$', views.update_lots),
    url(r'^lot_update_confirmation/$', views.lot_update_confirmation),
    url(r'^batchsheet_batch_print/$', views.batchsheet_batch_print),
    url(r'^check_lot_number/$', views.check_lot_number),
    url(r'^get_discontinued_orders/$', views.get_discontinued_orders),
    url(r'^(?P<lot_pk>\d+)/$', views.batchsheet_single),
    url(r'^get_last_lot/$', views.get_last_lot),

)
