import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.db.models import Q, F

urlpatterns = patterns('reports.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   # (r'^$', 'reports_home'),
    (r'^lot_summary/$', 'lot_summary'),
    (r'^formula_usage_summary/$', 'formula_usage_summary'),
    

)
#(r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),