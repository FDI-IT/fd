import datetime

from django.conf.urls import url, include
from export import views

urlpatterns = (

    url(r'^$', views.export_home),
    url(r'^single_export/(?P<flavor_id>\d+)/$', views.single_export),
    url(r'^export_all/$', views.export_all),
    #url(r'^by_model/$', views.model_list),
    #url(r'^by_model/(?P<type_id>\d+)/$', views.model_info),
    #url(r'^revision_details/(?P<revision_id>\d+)/$', views.revision_info, name="revision_paginated"),
    #url(r'^revision_details/(?P<revision_id>\d+)/show_all/(?P<pagination_count>\d+)/$', views.revision_info, name="show_all"),
    #url(r'^version_details/(?P<version_pk>\d+)/$', views.version_info, name="version_details"),
    #url(r'^version_details/(?P<version_pk>\d+)/redirected/(?P<redirect>.+)', views.version_info, name="version_redirect")
    
)