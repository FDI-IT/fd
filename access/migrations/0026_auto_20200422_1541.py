# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-22 15:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0025_auto_20200408_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='is_chemical',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='ingredienttemp',
            name='is_chemical',
            field=models.NullBooleanField(),
        ),
        migrations.AlterField(
            model_name='documents',
            name='doctype',
            field=models.CharField(choices=[(b'specsheet', b'Spec Sheet'), (b'sds', b'SDS'), (b'allergen', b'Allergen'), (b'nutri', b'Nutri'), (b'GMO', b'GMO'), (b'GPVC', b'GMO Project Verified Certificate'), (b'natural', b'Natural'), (b'origin', b'Origin'), (b'vegan', b'Vegan'), (b'organic', b'Organic Compliance'), (b'organic_cert', b'Organic Certified'), (b'kosher', b'Kosher'), (b'halal', b'Halal'), (b'COA', b'Certificate of Analysis'), (b'COI', b'Certificate of Insurance'), (b'ingbreak', b'Ingredient Breakdown'), (b'LOG', b'Letter Of Guarantee'), (b'form20', b'Form #020'), (b'form20ar', b'Form #020 Audit Report'), (b'form20c', b'Form #020 Certification'), (b'form40', b'Form #040'), (b'mLOG', b'Letter Of Guarantee - Manufacturer'), (b'mCOI', b'Certificate of Insurance - Manufacturer'), (b'mform20', b'Form #020 - Manufacturer'), (b'mform20ar', b'Form #020 Audit Report - Manufacturer'), (b'mform20c', b'Form #020 Certification - Manufacturer'), (b'mform40', b'Form #040 - Manufacturer')], default=b'', max_length=30),
        ),
    ]
