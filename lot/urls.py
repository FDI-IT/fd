import datetime

from django.conf.urls import url, include
from batchsheet import views

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', views.batchsheet_home),
    url(r'^batchsheet_print/(?P<flavor_number>\d+)/$', views.batchsheet_print),
    url(r'^lot_init/$', views.lot_init),
)
 url(r'^(?P<flavor_number>\d+)/batch_sheet/$', views.batch_sheet),