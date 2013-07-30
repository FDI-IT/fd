from django.conf.urls.defaults import *

urlpatterns = patterns('mysearch.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
   # (r'^$', 'index'),
    (r'^$', 'search'),
    (r'^access/alternate_rm/$', 'alternate_rm'),
    (r'^access/new_pin_flavor/$', 'new_pin_flavor'),
    (r'^print/$', 'print_search'),
    
)
