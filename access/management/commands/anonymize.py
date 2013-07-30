#!/usr/bin/env python

from optparse import make_option

from django.core.management.base import BaseCommand

from access import models


class Command(BaseCommand):
    args = "<fd.access.models.* ...>"
    help = ("Scans the mbd file indicated in settings for data in the argument models")
    option_list = BaseCommand.option_list + (
        make_option('--testdata', action='store_true', 
                    dest='testdata', default=False,
                    help='Uses shortened test data files.'),
        make_option('--anon', action='store_true', 
                    dest='anon', default=False,
                    help='Anonymizes data after importing.'),
    )
    requires_model_validation = True
    can_import_settings = True

    def handle(self, *args, **options):
        model_list = (models.Flavor, models.Ingredient, models.ExperimentalLog)
        for model in model_list:
            model.anonymize()