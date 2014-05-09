import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to, direct_to_template
from django.db.models import Q, F

urlpatterns = patterns('export.views',

    (r'^$', 'export_home'),
    url(r'^single_export/(?P<flavor_id>\d+)/$', 'single_export'),
    url(r'^export_all/$', 'export_all'),
    #(r'^by_model/$', 'model_list'),   
    #url(r'^by_model/(?P<type_id>\d+)/$', 'model_info'),
    #url(r'^revision_details/(?P<revision_id>\d+)/$', 'revision_info', name="revision_paginated"),
    #url(r'^revision_details/(?P<revision_id>\d+)/show_all/(?P<pagination_count>\d+)/$', 'revision_info', name="show_all"),
    #url(r'^version_details/(?P<version_pk>\d+)/$', 'version_info', name="version_details"),
    #url(r'^version_details/(?P<version_pk>\d+)/redirected/(?P<redirect>.+)', 'version_info', name="version_redirect")
    
)