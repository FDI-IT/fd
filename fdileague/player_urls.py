from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from fdileague.models import Player, YearScore
from fdileague.views import prf_player_detail

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^$', redirect_to, {'url': '/qc/retains/'}),

    url(r'(?P<player_url_pref>\w+)/(?P<player_url_slug>\w+)\.htm$', prf_player_detail),

)
