from django.conf.urls.defaults import *
from django import forms

urlpatterns = patterns('invoices.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    (r'^$', 'date_summary'), 
    (r'^upload_report/$', 'upload_report'), 
    (r'^upload_report_lw/$', 'upload_report_lw'), 
    (r'^date_summary/$', 'date_summary'),
    (r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
       'date_detail'),
)