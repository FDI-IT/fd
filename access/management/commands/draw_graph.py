#!/usr/bin/env pythonf
import os
import pygraphviz
from operator import attrgetter
from optparse import make_option

import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt

import networkx as nx

from django.db.models import Q, F
from django.core.management.base import BaseCommand
from django.conf import settings

import settings
from access.models import Flavor, FormulaTree

os.chdir(settings.DUMP_DIR)

class Command(BaseCommand):
    help = "A command to experiment with drawing nx graphs."
    args = "<flavornumber>"
    option_list = BaseCommand.option_list + (
        make_option('--depth',
                    action='store', 
                    dest='depth', default=1,
                    help='The depth at which to construct the tree.'),
    )
    requires_model_validation = True
    can_import_settings = True                

    def handle(self, *args, **options):
#        if options.get('testdata') == True:
#            base_path = settings.CSVTEST_PATH
#        else:
#            base_path = settings.CSVSOURCE_PATH
        
        # clean up the directory where all our exception info is logged
        for flavor_number in args:
            draw_graph(Flavor.objects.get(number=flavor_number))
        
def draw_graph(flavor):
    g = nx.DiGraph()
    onodes = FormulaTree.objects.filter(root_flavor=flavor)
    root = onodes[0]
    print root
    g.add_node(root.row_id)
    g.node[root.row_id]['label'] = "%s" % flavor
    for onode in onodes.filter(~Q(parent_id=None)):
        g.add_node(onode.row_id)
        if onode.node_flavor == None:
            g.node[onode.row_id]['label'] = '%s - %s lbs' % (onode.node_ingredient.id, onode.weight)
        else:
            g.node[onode.row_id]['label'] = '%s - %s lbs' % (onode.node_flavor.number, onode.weight)
        g.add_edge(onode.parent_id, onode.row_id)
 
    pgz = nx.to_agraph(g)
    pgz.layout(prog='dot')
    pgz.draw("/var/www/django/fd/%s.svg" % (flavor.number)) 
