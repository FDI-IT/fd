from django.conf.urls.defaults import *
from django import forms

urlpatterns = patterns('lab.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^solution$', 'solution'),
    (r'^inventory', 'inventory'),
    (r'^finished_product_labels/', 'finished_product_labels'),
    (r'^rm_labels/', 'rm_labels'),
    (r'^experimental_labels/$', 'experimental_labels'),
    (r'^ingredient_label/$', 'ingredient_label'),
     (r'^rm_sample_label/$', 'rm_sample_labels'),
     (r'^experimentals_by_customer/$', 'experimentals_by_customer'),
     (r'^experimentals_by_customer/(?P<customer>[\w ]+)/$', 'experimentals_by_customer_specific'),
    
)
