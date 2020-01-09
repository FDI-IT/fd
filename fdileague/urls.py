from django.conf.urls import url, include
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required

from access.views import SubListView
from fdileague.models import Player, YearScore
from fdileague.views import player_list_info, game_list_info, GameYearArchive

urlpatterns = (
    # Example:
    # url(r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^$', redirect_to, {'url': '/qc/retains/'}),

    url(r'^players/$', SubListView.as_view(**player_list_info)),
    url(r'^players/summary/$', 'player_summary'),
    url(r'^players/position_summary/(\w{1,4})/$', 'position_summary'),
    url(r'^players/season_best/$', 'player_season_best'),
    url(r'^players/(?P<player_id>\d+)/$', 'player_detail'),
     url(r'^retains/(\d{4})/(\d{2})/$', 'retains_by_month'),
    url(r'^players/(\w{1,4})/$', 'player_list_by_position'),
    url(r'^games/(?P<game_id>\d+)/$', 'game_detail'),
    url(r'^games/year/(?P<year>\d{4})/$', GameYearArchive.as_view()),
    url(r'^games/$', login_required(SubListView.as_view(**game_list_info))),
)
