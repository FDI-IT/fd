from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to
from django.views.generic.date_based import archive_index
from django.contrib.auth.decorators import login_required

from fdileague.models import Player, YearScore
from fdileague.views import player_list_info, game_list_info, GameYearArchive

urlpatterns = patterns('fdileague.views',
    # Example:
    # (r'^fd/', include('fd.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^$', redirect_to, {'url': '/qc/retains/'}),

    (r'^players/$', list_detail.object_list, player_list_info),
    (r'^players/summary/$', 'player_summary'),
    (r'^players/position_summary/(\w{1,4})/$', 'position_summary'),
    (r'^players/season_best/$', 'player_season_best'),
    (r'^players/(?P<player_id>\d+)/$', 'player_detail'),
    #(r'^retains/(\d{4})/(\d{2})/$', 'retains_by_month'),
    (r'^players/(\w{1,4})/$', 'player_list_by_position'),
    (r'^games/(?P<game_id>\d+)/$', 'game_detail'),
    (r'^games/year/(?P<year>\d{4})/$', GameYearArchive.as_view()),
    (r'^games/$', login_required(list_detail.object_list), game_list_info),
)
