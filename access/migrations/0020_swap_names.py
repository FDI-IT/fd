# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-03-12 13:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0019_auto_20200318_1358'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Supplier',
            new_name='SupplierTemp',
        ),
        migrations.RenameModel(
            old_name='Foo',
            new_name='Supplier',
        ),
    ]