# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-03 12:03
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0016_auto_20200303_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='answer_options',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, default=b'', max_length=2000), blank=True, default=[], null=True, size=2), blank=True, default=[], null=True, size=None),
        ),
    ]