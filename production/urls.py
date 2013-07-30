from django.conf.urls.defaults import *
from django import forms

from django.views.generic.simple import direct_to_template


urlpatterns = patterns('production.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'index'),
    (r'^(\w+)/$', 'lots_by_status'),
    (r'^(\w+)/page(?P<page>[0-9]+)/$', 'lots_by_status'),
)
