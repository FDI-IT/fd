# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-04-07 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0023_documents_manufacturer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documents',
            name='manufacturer',
        ),
        migrations.AddField(
            model_name='flavor',
            name='amount_created_last_year',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flavor',
            name='amount_created_this_year',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='documents',
            name='doctype',
            field=models.CharField(choices=[(b'specsheet', b'Spec Sheet'), (b'sds', b'SDS'), (b'allergen', b'Allergen'), (b'nutri', b'Nutri'), (b'GMO', b'GMO'), (b'GPVC', b'GMO Project Verified Certificate'), (b'LOG', b'Letter Of Guarantee'), (b'natural', b'Natural'), (b'origin', b'Origin'), (b'vegan', b'Vegan'), (b'organic', b'Organic Compliance'), (b'organic_cert', b'Organic Certified'), (b'kosher', b'Kosher'), (b'halal', b'Halal'), (b'COA', b'Certificate of Analysis'), (b'COI', b'Certificate of Insurance'), (b'ingbreak', b'Ingredient Breakdown'), (b'form20', b'Form #020'), (b'form20ar', b'Form #020 Audit Report'), (b'form20c', b'Form #020 Certification'), (b'form40', b'Form #040')], default=b'', max_length=30),
        ),
    ]
