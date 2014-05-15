#!/usr/bin/env python

import os
import cStringIO

from subprocess import call
from optparse import make_option
from operator import attrgetter

from django.db import connection, transaction
from django.core.files.uploadedfile import InMemoryUploadedFile 
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import get_models, get_app
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError

from salesorders import models, report_parser

class Command(BaseCommand):
    args = "<fd.salesorders.models.* ...>"
    help = ("Deletes any model objects and imports a test report (PRN).")
    option_list = BaseCommand.option_list + (
        make_option('--report', action='store', 
                    dest='report', 
                    default='/var/www/django/dump/report.PRN',
                    type='string',
                    help='Path to report file (PRN) to use.'),
    )
    requires_model_validation = True
    can_import_settings = True              
    
    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute('DROP TABLE "salesorders_lineitem", "salesorders_salesordernumber", "salesorders_salesorderreport", "salesorders_savedreport" CASCADE;')
        transaction.commit_unless_managed()
        call(['python', 'manage.py', 'syncdb'])
        # delete all model objects
#        
#        for m in get_models(get_app('salesorders')):
#            m.objects.all().delete()
            
        report_path = options.get('report')
        report_file = open(report_path, 'r')
        report_parser.parse_orders(report_file)