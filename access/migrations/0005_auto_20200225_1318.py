# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-25 13:18
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0004_auto_20200225_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='answer_options',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, default=b'', max_length=2000), blank=True, default=[], null=True, size=None),
        ),
        migrations.AddField(
            model_name='question',
            name='correct_answer',
            field=models.CharField(default=b'', max_length=2000),
        ),
        migrations.AddField(
            model_name='question',
            name='spanish_version',
            field=models.BooleanField(default=False),
        ),
    ]