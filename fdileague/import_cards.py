import os
import sys
from lxml import html
from lxml import etree 

import re

import glob
import datetime
import logging
import codecs

from copy import copy

from sets import Set

from decimal import InvalidOperation
from decimal import Decimal, ROUND_HALF_UP

from lxml.cssselect import CSSSelector


from xlrd import open_workbook
from xlrd import xldate_as_tuple

from django.core.files import File
from django.db import connection, transaction, IntegrityError
from django.db.models import Sum
#from django.db.models import Q

from fdileague.models import *

csss_table = CSSSelector('table')
csss_tr = CSSSelector('tr')
csss_td = CSSSelector('td')
csss_a = CSSSelector('a')

team_re = re.compile('\/teams\/([a-zA-Z]+?)\/(\d{4})\.htm')
player_re = re.compile('\/players\/([a-zA-Z]+?)\/(\d+?)\.htm')

def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

class MyBaseException:
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)
    def __str__(self):
        return repr(self.parameter)
    
class PlayerException(MyBaseException):
    pass

class PlayerImport:
    """
    A class to help importing of QC Cards
    """
    def __init__(self, path):
        """
        Read the spreadsheet from path and populate a dictionary flavor_info
        
        self.
            path
            wb
            flavor_info
            special_cells
            my_style
        """
        
        delete_all_crap()
        print(Player.objects.all().count())
        self.path = path
        self.wb = open_workbook(path)
        nullcount = 0
        for s in self.wb.sheets():
            print(s.name)
            position = s.name
            header_cols = {}
            nullheadercount = 0
            for header_col in range(1,s.ncols):
                v = s.cell(0,header_col).value
                try:
                    header_cols[header_col] = int(v)
                except:
                    pass
            for r in range(1,s.nrows):
                lname =  s.cell(r,2).value
                fname = s.cell(r,3).value
                if lname == "" and fname == "":
                    nullcount += 1
                    if nullcount > 5:
                        nullcount = 0
                        
                        break
                else:
                    p = Player(lastname=lname, firstname=fname, position=position)
                    p.save()
                    for c, year in header_cols.items():
                        score = None
                        try:
                            score = int(s.cell(r,c).value)
                        except:
                            pass
                        if score is not None and score > -1:
                            ys = YearScore(player=p, year=year, score=int(s.cell(r,c).value))
                            ys.save()
            print(Player.objects.all().count())
            print(YearScore.objects.all().count())
        normalize_player_scores()
        
def normalize_player_scores():
    """If a player has no score objects, we give them one with a score zero"""
    players = Player.objects.annotate(Sum('yearscore__score')).order_by('-yearscore__score__sum')
    for p in players:
        if p.yearscore__score__sum is None:
            ys = YearScore(player=p, year=1900, score=0)
            ys.save()
        else:
            break
    
def delete_all_crap():
    YearScore.objects.all().delete()
    Player.objects.all().delete()
    
def try_globs():
    Scoring.objects.all().delete()
    TeamStats.objects.all().delete()
    Game.objects.all().delete()
    os.chdir('/var/www/django/fdileague/')
    file_list = []
    for f in glob.glob('*.htm'):
        file_list.append(f)
    file_list = sorted(file_list)
    file_list.reverse()
    for f in file_list:
        print(try_boxscore(f))
    
def try_boxscore(file_path="/var/www/django/fdileague/201112180crd.htm"):
    try:
        return parse_boxscore(file_path)
    except Exception as e:
        return e

def parse_boxscore(file_path="/var/www/django/fdileague/201112180crd.htm"):
    p, h = get_parser_objs(file_path)
    g = parse_scoring(p,h,file_path)
    
    return g
    
def parse_scoring(p,h,file_path):
    """Parse a boxscore.htm file.
    
    The first table probably has the week data.
    """
    
    g = {}
    #g['html_file'] = File(open(file_path, 'r'))
    g['week'] = get_week(p)
    g['game_date'] = get_date(p)
    away_team_link, home_team_link = get_team_links(h)
    g['away_team'],created = Team.objects.get_or_create(**parse_team_link(away_team_link))
    g['home_team'],created = Team.objects.get_or_create(**parse_team_link(home_team_link))
    
    ts_away, ts_home = parse_teamstats(h)
    g['teamstats_away'],created=TeamStats.objects.get_or_create(**ts_away)
    g['teamstats_home'],created=TeamStats.objects.get_or_create(**ts_home)

    game,created = Game.objects.get_or_create(**g)
    game.html_file = File(open(file_path, 'r'))
    game.save()
    
    scoring_list = parse_scoring_table(h)
    for sl in scoring_list:
        s = Scoring(game=game, **sl)
        s.save()
            
    prr_list = parse_prr(h)
    for prr in prr_list:
        prr = PRR(game=game, **prr)
        prr.save()
        
    dr_list = parse_dr(h)
    for dr in dr_list:
        dr = DR(game=game, **dr)
        dr.save()
        
    kp_list = parse_kp(h)
    for kp in kp_list:
        kp = KP(game=game, **kp)
        kp.save()
    return g
    
def get_parser_objs(file_path="/var/www/django/fdileague/201112180crd.htm"):
    p = html.parse(file_path)
    h = CSSSelector('html')(p)[0]
    return (p, h)

def get_week(p):
    tables = csss_table(p)
    week_table = tables[0]
    week_cell = csss_td(week_table)[0]
    return week_cell.text

def get_date(p):
    raw_date_string = str(p.xpath('//h1/following-sibling::*')[0].getchildren()[0].text_content())
    return datetime.datetime.strptime(raw_date_string, "%A, %B %d, %Y")

def get_team_links(h):
    linescore = h.get_element_by_id('linescore')
    links = csss_a(linescore)
    return (links[0], links[1])

def parse_team_link(link):
    match = team_re.match(list(link.values())[0])
    if match:
        team_dict = {}
        g = match.groups()
        team_dict['city_slug'] = g[0]
        team_dict['year'] = datetime.date(int(g[1]),1,1)
        team_dict['full_name'] = str(link.text_content())
        team_dict['name'] = team_dict['full_name'].split(' ')[-1]
        return team_dict
    
def parse_scoring_table(h):
    scoring_table = h.get_element_by_id('scoring')
    scoring_list = []
    quarter = "1st"
    i = 0
    for tr in scoring_table.getchildren()[1:]:
        sld = {}
        cells = tr.getchildren()
        if cells[0] != "":
            quarter = str(cells[0].text_content())
        sld['quarter'] = quarter 
        sld['team'] = str(cells[1].text_content())
        summary_raw = etree.tostring(cells[2])
        l_index = summary_raw.find('>')+1
        r_index = summary_raw.rfind('<')        
        sld['summary'] = summary_raw[l_index:r_index]
        sld['away_score'] = str(cells[3].text_content())
        sld['home_score'] = str(cells[4].text_content())
        sld['index'] = i
        scoring_list.append(sld)
        i += 1
    return scoring_list

def test_ts():
    p,h = get_parser_objs()
    return parse_teamstats(p,h)

def parse_teamstats(h):
    teamstats_table = h.get_element_by_id('team_stats')
    ts_away = {}
    ts_home = {}
    
    rows = []
    for tr in teamstats_table.getchildren()[1:]:
        rows.append(tr.getchildren())
    
    def parse_column(i):
        d={}
        d['first_downs'] = rows[0][i].text_content()
        d['rushes'],d['rush_yards'],d['rush_tds'] = rows[1][i].text_content().split('-')
        d['pass_comp'],d['pass_att'],d['pass_yards'],d['pass_tds'],d['pass_int'] = rows[2][i].text_content().split('-')
        d['sacks'],d['sack_yards'] = rows[3][i].text_content().split('-') 
        d['net_pass_yards'] = rows[4][i].text_content()
        d['total_yards'] = rows[5][i].text_content()
        d['fumbles'],d['fumbles_lost'] = rows[6][i].text_content().split('-')
        d['turnovers'] = rows[7][i].text_content()
        d['penalties'],d['penalties_yards'] = rows[8][i].text_content().split('-')
        return d
    
    ts_away = parse_column(1)
    ts_home = parse_column(2)

    return (ts_away, ts_home)

def test_prr():
    p,h = get_parser_objs()
    return parse_prr(h)


def parse_prr(h):
    prr_table = h.get_element_by_id('skill_stats')
    prr_list = []
    i=0
    for tr in csss_tr(prr_table)[2:]:
        cells = tr.getchildren()
        player_cell = cells[0]
        firstname=str(player_cell.text_content())
        try:
            url=list(csss_a(player_cell)[0].values())[0]
            p,c = Player.objects.get_or_create(firstname=firstname, url=url)
        except:
            continue
        d = {}
        d['player'] = p
        d['team'] = str(cells[1].text_content())
        try:
            d['p_cmp'] = int(cells[2].text_content())
        except:
            d['p_cmp'] = None
        try:
            d['p_att'] = int(cells[3].text_content())
        except:
            d['p_att'] = None
        try:
            d['p_yds'] = int(cells[4].text_content())
        except:
            d['p_yds'] = None
        try:
            d['p_tds'] = int(cells[5].text_content())
        except:
            d['p_tds'] = None
        try:
            d['p_int'] = int(cells[6].text_content())
        except:
            d['p_int'] = None
        try:
            d['p_lng'] = int(cells[7].text_content())
        except:
            d['p_lng'] = None
        try:
            d['ru_att'] = int(cells[8].text_content())
        except:
            d['ru_att'] = None
        try:
            d['ru_yds'] = int(cells[9].text_content())
        except:
            d['ru_yds'] = None
        try:
            d['ru_td'] = int(cells[10].text_content())
        except:
            d['ru_td'] = None
        try:
            d['ru_lng'] = int(cells[11].text_content())
        except:
            d['ru_lng'] = None
        try:
            d['re_rec'] = int(cells[12].text_content())
        except:
            d['re_rec'] = None
        try:
            d['re_yds'] = int(cells[13].text_content())
        except:
            d['re_yds'] = None
        try:
            d['re_td'] = int(cells[14].text_content())
        except:
            d['re_td'] = None
        try:
            d['re_lng'] = int(cells[15].text_content())
        except:
            d['re_lng'] = None  
        d['index'] = i
        i+=1         
        prr_list.append(d)
    return prr_list

def test_dr():
    p,h = get_parser_objs()
    return parse_dr(h)


def parse_dr(h):
    def_table = h.get_element_by_id('def_stats')
    def_list = []
    i=0
    for tr in csss_tr(def_table)[2:]:
        cells = tr.getchildren()
        player_cell = cells[0]
        firstname=str(player_cell.text_content())
        try:
            url=list(csss_a(player_cell)[0].values())[0]
            p,c = Player.objects.get_or_create(firstname=firstname, url=url)
        except:
            continue
        d = {}
        d['player'] = p
        d['team'] = str(cells[1].text_content())
        try:
            d['sk'] = int(cells[2].text_content())
        except:
            d['sk'] = None
        try:
            d['interceptions'] = int(cells[3].text_content())
        except:
            d['interceptions'] = None
        try:
            d['int_yds'] = int(cells[4].text_content())
        except:
            d['int_yds'] = None
        try:
            d['int_td'] = int(cells[5].text_content())
        except:
            d['int_td'] = None
        try:
            d['int_lng'] = int(cells[6].text_content())
        except:
            d['int_lng'] = None
        try:
            d['fumble_fr'] = int(cells[7].text_content())
        except:
            d['fumble_fr'] = None
        try:
            d['fumble_yds'] = int(cells[8].text_content())
        except:
            d['fumble_yds'] = None
        try:
            d['fumble_td'] = int(cells[9].text_content())
        except:
            d['fumble_td'] = None
        try:
            d['fumble_ff'] = int(cells[10].text_content())
        except:
            d['fumble_ff'] = None
        try:
            d['kickreturn_rt'] = int(cells[11].text_content())
        except:
            d['kickreturn_rt'] = None
        try:
            d['kickreturn_yds'] = int(cells[12].text_content())
        except:
            d['kickreturn_yds'] = None
        try:
            d['kickreturn_yrt'] = Decimal(str(cells[13].text_content()))
        except:
            d['kickreturn_yrt'] = None
        try:
            d['kickreturn_td'] = int(cells[14].text_content())
        except:
            d['kickreturn_td'] = None
        try:
            d['kickreturn_lng'] = int(cells[15].text_content())
        except:
            d['kickreturn_lng'] = None
        try:
            d['puntreturn_ret'] = int(cells[16].text_content())
        except:
            d['puntreturn_ret'] = None
        try:
            d['puntreturn_yds'] = int(cells[17].text_content())
        except:
            d['puntreturn_yds'] = None
        try:
            d['puntreturn_yr'] =  Decimal(str(cells[18].text_content()))
        except:
            d['puntreturn_yr'] = None        
        try:
            d['puntreturn_td'] = int(cells[19].text_content())
        except:
            d['puntreturn_td'] = None        
        try:
            d['puntreturn_lng'] = int(cells[20].text_content())
        except:
            d['puntreturn_lng'] = None        
        d['index']=i
        i+=1  
        def_list.append(d)
    return def_list

def test_kp():
    p,h = get_parser_objs()
    return parse_kp(h)


def parse_kp(h):
    kp_table = h.get_element_by_id('kick_stats')
    kp_list = []
    i=0
    for tr in csss_tr(kp_table)[2:]:
        cells = tr.getchildren()
        player_cell = cells[0]
        firstname=str(player_cell.text_content())
        try:
            url=list(csss_a(player_cell)[0].values())[0]
            p,c = Player.objects.get_or_create(firstname=firstname, url=url)
        except:
            continue
        d = {}
        d['player'] = p
        d['team'] = str(cells[1].text_content())
        try:
            d['pat_xpm'] = int(cells[2].text_content())
        except:
            d['pat_xpm'] = None
        try:
            d['pat_xpa'] = int(cells[3].text_content())
        except:
            d['pat_xpa'] = None
        try:
            d['fg_fgm'] = int(cells[4].text_content())
        except:
            d['fg_fgm'] = None
        try:
            d['fg_fga'] = int(cells[5].text_content())
        except:
            d['fg_fga'] = None
        try:
            d['p_pnt'] = int(cells[6].text_content())
        except:
            d['p_pnt'] = None
        try:
            d['p_yds'] = int(cells[7].text_content())
        except:
            d['p_yds'] = None
        try:
            d['p_yp'] = Decimal(str(cells[8].text_content()))
        except:
            d['p_yp'] = None
        try:
            d['p_lng'] = int(cells[9].text_content())
        except:
            d['p_lng'] = None
        d['index'] = i
        i+=1
        kp_list.append(d)
    return kp_list
     
#    
##        sld['quarter'] = quarter 
##        sld['team'] = str(cells[1].text_content())
##        summary_raw = etree.tostring(cells[2])
##        l_index = summary_raw.find('>')+1execve
##        r_index = summary_raw.rfind('<')        
##        sld['summary'] = summary_raw[l_index:r_index]
##        sld['away_score'] = str(cells[3].text_content())
##        sld['home_score'] = str(cells[4].text_content())
#        teamstats_list = i
#        scoring_list[i] = sld
#        i += 1
#    return scoring_list
#    for t in csss_table(p):
#        for tr in csss_tr(t):
#            for td in csss_td(tr):
#                return td
#                
#    return td
#    for tr in trs:
#        for c in tr.iterchildren():
#            for td in td_sel(c):
#                print td.text

    