# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-25 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0009_auto_20200225_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='answer',
            field=models.CharField(default=b'', max_length=500, null=True),
        ),
    ]
