# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-25 13:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0006_remove_question_answer_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='question',
            name='correct_answer',
        ),
        migrations.RemoveField(
            model_name='question',
            name='spanish_version',
        ),
    ]