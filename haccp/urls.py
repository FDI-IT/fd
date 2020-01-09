from django.conf.urls import url, include
from haccp import views
from django.views.generic.list import ListView

from access.views import SubListView
from haccp.views import cipm_list_info


urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', views.index),
    url(r'^cipm/$', SubListView.as_view(**cipm_list_info)),
    url(r'^cipm/(?P<cipm_pk>\d+)/$', views.cipm_detail),
)
