from django.conf.urls.defaults import *
from django import forms

urlpatterns = patterns('performance_appraisal.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^(?P<appraisal_id>\d+)/$', 'appraisal_review'),

)