from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404
from django.views.generic import list_detail
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum, Count, Avg
from django.utils.decorators import method_decorator
from django.views.generic.dates import YearArchiveView
from django.contrib.auth.decorators import login_required
from django.utils import simplejson


from fdileague.models import Player, YearScore, POSITION_LIST, Game

player_list_info =  {
    'queryset': Player.objects.all(),
    'paginate_by': 100,
}

game_list_info = {
    'queryset':Game.objects.all(),
    'paginate_by':100,                  
}

def player_detail(request, player_id):
    player = get_object_or_404(Player, pk=player_id)
    return list_detail.object_detail(
        request,
        queryset=Player.objects.all(),
        object_id=player_id,
    )
    
def prf_player_detail(request, player_url_pref, player_url_slug):
    try:
        player = Player.objects.get(url__icontains=player_url_slug)
    except:
        raise Http404
    return HttpResponseRedirect('/django/admin/fdileague/player/%s/' % player.pk)
#    try:
#        player = Player.objects.get(url__icontains=player_url_slug)
#    except:
#        raise Http404
#    return list_detail.object_detail(
#        request,
#        queryset=Player.objects.all(),
#        object_id=player_id,
#    )
    
def game_detail(request, game_id):
    g = get_object_or_404(Game, pk=game_id)
    return list_detail.object_detail(
        request,
        queryset=Game.objects.all(),
        object_id=game_id,
        template_object_name='game',
    )
    
def position_summary(request, position):
    players = Player.objects.filter(position__iexact=position).annotate(Sum('yearscore__score')).annotate(Count('yearscore')).annotate(Avg('yearscore__score')).order_by('-yearscore__score__sum')[0:50]
    ten_best_totals = players[:10]
    rest_best_totals = players[10:40]
    return render_to_response('fdileague/position_summary.html',
                              {
                                'ten_best_totals':ten_best_totals,
    })
    
def player_summary(request):
    top_scorers = []
    for p in POSITION_LIST:
        top_scorers.append((p, Player.objects.filter(position=p).annotate(Sum('yearscore__score')).annotate(Count('yearscore')).annotate(Avg('yearscore__score')).order_by('-yearscore__score__sum')[0:50]))
    return render_to_response('fdileague/player_summary.html',
                              {
                                'top_scorers': top_scorers,
    })
    
def player_season_best(request):
    top_scorers=[]
    for p in POSITION_LIST:
        players = Player.objects.filter(position=p).annotate(Sum('yearscore__score')).order_by('-yearscore__score')[0:10]
        for player in players:
            player.best_year = YearScore.objects.filter(player=player).filter(score=player.yearscore__score__sum)[0].year
            
        top_scorers.append((p, players))

    return render_to_response('fdileague/player_season_best.html',
                              {
                               'top_scorers': top_scorers,
                               }
                              )
    
def player_list_by_position(request, position):
    if position in POSITION_LIST:
        return list_detail.object_list(
            request,
            queryset=Player.objects.filter(position=position),
            paginate_by=100,
        )
    else:
        raise Http404
    
class GameYearArchive(YearArchiveView):
    template_name = "fdileague/game_year_archive.html"
    model = Game
    date_field = 'game_date'
    context_object_name = "game_list"
    make_object_list = True
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(YearArchiveView, self).dispatch(*args, **kwargs)