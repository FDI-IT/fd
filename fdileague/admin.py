from fdileague.models import *
from django.contrib import admin
from reversion.admin import VersionAdmin

#admin.site.register(Retain)

class PlayerAdmin(VersionAdmin):
    search_fields = ['lastname','firstname']
admin.site.register(Player, PlayerAdmin)

class YearScoreAdmin(VersionAdmin):
    search_fields = []
admin.site.register(YearScore, YearScoreAdmin)

class GameAdmin(VersionAdmin):
    search_fields = []
admin.site.register(Game, GameAdmin)

class ScoringAdmin(VersionAdmin):
    search_fields = []
    list_display = ("game", "index", "quarter", "team", "type", "points")
    
admin.site.register(Scoring, ScoringAdmin)

class TeamAdmin(VersionAdmin):
    search_fields = []
admin.site.register(Team, TeamAdmin)

class PRRAdmin(VersionAdmin):
    search_fields = []
admin.site.register(PRR, PRRAdmin)

class DRAdmin(VersionAdmin):
    search_fields = []
admin.site.register(DR, DRAdmin)

class KPAdmin(VersionAdmin):
    search_fields = []
admin.site.register(KP, KPAdmin)
    