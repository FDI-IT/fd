import datetime

from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to, direct_to_template
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F

urlpatterns = patterns('history_audit.views',

    (r'^$', 'history_home'),
    (r'^by_user/$', 'user_list'),
    url(r'^by_user/(?P<user_id>\d+)/$', 'user_info'),
    (r'^by_model/$', 'model_list'),   
    url(r'^by_model/(?P<type_id>\d+)/$', 'model_info'),
    url(r'^revision_details/(?P<revision_id>\d+)/$', 'revision_info', name="revision_paginated"),
    url(r'^revision_details/(?P<revision_id>\d+)/show_all/(?P<pagination_count>\d+)/$', 'revision_info', name="show_all"),
    url(r'^version_details/(?P<version_pk>\d+)/$', 'version_info', name="version_details"),
    url(r'^version_details/(?P<version_pk>\d+)/redirected/(?P<redirect>.+)', 'version_info', name="version_redirect")
    
)