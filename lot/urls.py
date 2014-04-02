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
)
#(r'^(?P<flavor_number>\d+)/batch_sheet/$', 'batch_sheet'),