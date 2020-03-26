#!/usr/bin/env python

import os
import sys
import re
import glob
import datetime
import logging
import StringIO
from PIL import Image

from optparse import make_option
from operator import attrgetter

from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError
from django.core.files import File

from newqc.models import TestCard

class Command(BaseCommand):
    args = "<fd.qc.something_useful!.* ...>"
    help = ("Generates thumbnails for testcards.")
    option_list = BaseCommand.option_list + (
#        make_option('--testdata', action='store_true', 
#                    dest='testdata', default=False,
#                    help='Uses shortened test data files.'),
#        make_option('--anon', action='store_true', 
#                    dest='anon', default=False,
#                    help='Anonymizes data after importing.'),
    )

    
    #sort the model list so that FK rows exist
                 
    
    def handle(self, *args, **options):
        for tc in TestCard.objects.all():
            try:
                print "%sx%s" % (tc.thumbnail.height, tc.thumbnail.width)
            except ValueError:
                large = Image.open(tc.large.file.file)
                tn = large.resize((380,490), Image.ANTIALIAS)
                tn_path = "/tmp/%s-tn.png" % os.path.splitext(os.path.basename(tc.large.file.name))[0]
                tn.save(tn_path)
                thumbnail_file = File(open(tn_path,'r'))
                tc.thumbnail = thumbnail_file
                tc.save()
    #            tn.save("/tmp/%s-tn.png" % os.path.splitext(os.path.basename(large))[0], format='PNG')
    #            tn_file = File(thumb_io, None, 'foo.')
    #            thumb
                