#!/usr/bin/env python

import os
import sys
import re
import glob
import datetime
import logging

from optparse import make_option
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
#from django.db.models import get_models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError


class Command(BaseCommand):
    args = "<fd.qc.something_useful!.* ...>"
    help = ("Scans a directory of QC cards and imports data")
    option_list = BaseCommand.option_list + (
#        make_option('--testdata', action='store_true', 
#                    dest='testdata', default=False,
#                    help='Uses shortened test data files.'),
#        make_option('--anon', action='store_true', 
#                    dest='anon', default=False,
#                    help='Anonymizes data after importing.'),
    )
    requires_model_validation = True
    can_import_settings = True
    
    #sort the model list so that FK rows exist
                 
    
    def handle(self, *args, **options):
        pass
#        import_flavor_cards()
#        
#        print "Lot count: %s" % Lot.objects.all().count()
#        print "Retain count: %s" % Retain.objects.all().count()