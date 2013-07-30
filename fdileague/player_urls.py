from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.contrib.auth.decorators import login_required

from fdileague.models import Player, YearScore
from fdileague.views import prf_player_detail

urlpatterns = patterns('fdileague.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^$', redirect_to, {'url': '/django/qc/retains/'}),

    (r'(?P<player_url_pref>\w+)/(?P<player_url_slug>\w+)\.htm$','prf_player_detail'),

)
