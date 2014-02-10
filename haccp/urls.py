from django.conf.urls.defaults import *
from django.views.generic import list_detail

from haccp.views import cipm_list_info
urlpatterns = patterns('haccp.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'index'),
    (r'^cipm/$', list_detail.object_list, cipm_list_info),
    (r'^cipm/(?P<cipm_pk>\d+)/$', 'cipm_detail'),
)
