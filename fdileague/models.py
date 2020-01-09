from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import fields

POSITIONS = (
    ('DT','DT'),
    ('K','K'),
    ('TE','TE'),
    ('WR','WR'),
    ('RB','RB'),
    ('QB','QB'),
)

POSITION_LIST = ('DT', 'K', 'TE', 'WR', 'RB', 'QB')


class Player(models.Model):
    """
    Info scrubbed from QC cards about products
    """
    lastname = models.CharField(max_length=100, blank=True, default="")
    firstname = models.CharField(max_length=100, blank=True, default="")
    position = models.CharField(max_length=5, choices=POSITIONS, blank=True, null=True, default="")
    url = models.CharField(max_length=50)

    def __str__(self):
        return "%s %s" % (self.firstname, self.lastname)
    class Meta:
        ordering = ['lastname', 'firstname']

    @property
    def image_url(self):
        image_path = "%s-%s" % (self.firstname, self.lastname)
        return "http://www.fdileague.com/images/Faces/%s.jpg" % image_path.replace(' ','').replace('.','')

class YearScore(models.Model):
    player = models.ForeignKey('Player',on_delete=models.CASCADE)
    year = models.SmallIntegerField()
    score = models.SmallIntegerField()

    class Meta:
        ordering = ['-year']
    def __str__(self):
        return "%s %s %s %s" % (selself.player, self.year, self.score)

class Game(models.Model):
    html_file = models.FileField(upload_to="fdileague")
    game_date = models.DateField()
    week = models.CharField(max_length=20)
    home_team = models.ForeignKey('Team', related_name="home_games",on_delete=models.CASCADE)
    away_team = models.ForeignKey('Team', related_name="away_games",on_delete=models.CASCADE)
    teamstats_home = models.ForeignKey('TeamStats', related_name='tsh',on_delete=models.CASCADE)
    teamstats_away = models.ForeignKey('TeamStats', related_name='tsa',on_delete=models.CASCADE)
    # passing_receiving
    # defense_returns
    # kicking_punting
    class Meta:
        ordering = ['-game_date',]
    def __str__(self):
        return "%s at %s - %s" % (self.away_team.full_name, self.home_team.full_name, self.game_date)

class Team(models.Model):
    year = models.DateField()
    city_slug = models.TextField()
    name = models.TextField()
    full_name = models.TextField()

    class Meta:
        ordering = ['-year', 'full_name']
    def __str__(self):
        return "%s %s" % (self.year.year, self.full_name,)

class Scoring(models.Model):
    game = models.ForeignKey('Game',on_delete=models.CASCADE)
    quarter = models.CharField(max_length=10)
    team = models.CharField(max_length=15)
    type = models.CharField(max_length=20, blank=True, default="")
    summary = models.TextField()
    points = models.SmallIntegerField(null=True,)
    scorer = models.ForeignKey('Player', null=True, related_name="scorer_set",on_delete=models.CASCADE)
    yardage = models.SmallIntegerField(null=True)
    qb = models.ForeignKey('Player', null=True, related_name="qb_set",on_delete=models.CASCADE)
    extra_point = models.ForeignKey('Player', null=True, related_name="extrapoint_set",on_delete=models.CASCADE)
    reason = models.TextField(blank=True, default="")
    away_score = models.SmallIntegerField()
    home_score = models.SmallIntegerField()
    index = models.SmallIntegerField()

    def __str__(self):
        return "%s %s" % (self.quarter, self.summary,)

    class Meta:
        ordering = ['-game__game_date','index']

class TeamStats(models.Model):
    first_downs = models.SmallIntegerField()
    rushes = models.SmallIntegerField()
    rush_yards = models.SmallIntegerField()
    rush_tds = models.SmallIntegerField()
    pass_comp = models.SmallIntegerField()
    pass_att = models.SmallIntegerField()
    pass_yards = models.SmallIntegerField()
    pass_tds = models.SmallIntegerField()
    pass_int = models.SmallIntegerField()
    sacks = models.SmallIntegerField()
    sack_yards = models.SmallIntegerField()
    net_pass_yards = models.SmallIntegerField()
    total_yards = models.SmallIntegerField()
    fumbles = models.SmallIntegerField()
    fumbles_lost = models.SmallIntegerField()
    turnovers = models.SmallIntegerField()
    penalties = models.SmallIntegerField()
    penalties_yards = models.SmallIntegerField()



class PRR(models.Model):
    player = models.ForeignKey('Player',on_delete=models.CASCADE)
    game = models.ForeignKey('Game',on_delete=models.CASCADE)
    team = models.CharField(max_length=5)
    index=models.PositiveSmallIntegerField()
    p_cmp = models.SmallIntegerField(null=True)
    p_att = models.SmallIntegerField(null=True)
    p_yds = models.SmallIntegerField(null=True)
    p_tds = models.SmallIntegerField(null=True)
    p_int = models.SmallIntegerField(null=True)
    p_lng = models.SmallIntegerField(null=True)
    ru_att = models.SmallIntegerField(null=True)
    ru_yds = models.SmallIntegerField(null=True)
    ru_td = models.SmallIntegerField(null=True)
    ru_lng = models.SmallIntegerField(null=True)
    re_rec = models.SmallIntegerField(null=True)
    re_yds = models.SmallIntegerField(null=True)
    re_td = models.SmallIntegerField(null=True)
    re_lng = models.SmallIntegerField(null=True)

    class Meta:
        ordering = ['index']

class DR(models.Model):
    player = models.ForeignKey('Player',on_delete=models.CASCADE)
    game = models.ForeignKey('Game',on_delete=models.CASCADE)
    team = models.CharField(max_length=5)
    index=models.PositiveSmallIntegerField()
    sk = models.SmallIntegerField(null=True)
    interceptions = models.SmallIntegerField(null=True)
    int_yds = models.SmallIntegerField(null=True)
    int_td = models.SmallIntegerField(null=True)
    int_lng = models.SmallIntegerField(null=True)
    fumble_fr = models.SmallIntegerField(null=True)
    fumble_yds = models.SmallIntegerField(null=True)
    fumble_td = models.SmallIntegerField(null=True)
    fumble_ff = models.SmallIntegerField(null=True)
    kickreturn_rt = models.SmallIntegerField(null=True)
    kickreturn_yds = models.SmallIntegerField(null=True)
    kickreturn_yrt = models.DecimalField(decimal_places=1, max_digits=4, null=True)
    kickreturn_td = models.SmallIntegerField(null=True)
    kickreturn_lng = models.SmallIntegerField(null=True)
    puntreturn_ret = models.SmallIntegerField(null=True)
    puntreturn_yds = models.SmallIntegerField(null=True)
    puntreturn_yr = models.DecimalField(decimal_places=1, max_digits=4, null=True)
    puntreturn_td = models.SmallIntegerField(null=True)
    puntreturn_lng = models.SmallIntegerField(null=True)

    class Meta:
        ordering = ['index']

class KP(models.Model):
    player = models.ForeignKey('Player',on_delete=models.CASCADE)
    game = models.ForeignKey('Game',on_delete=models.CASCADE)
    team = models.CharField(max_length=5)
    index=models.PositiveSmallIntegerField()
    pat_xpm = models.SmallIntegerField(null=True)
    pat_xpa = models.SmallIntegerField(null=True)
    fg_fgm = models.SmallIntegerField(null=True)
    fg_fga = models.SmallIntegerField(null=True)
    p_pnt = models.SmallIntegerField(null=True)
    p_yds = models.SmallIntegerField(null=True)
    p_yp= models.DecimalField(decimal_places=1, max_digits=4, null=True)
    p_lng = models.SmallIntegerField(null=True)

    class Meta:
        ordering = ['index']
