#!/bin/bash
# RUN SQL COMMAND FIRST
cd /var/www/django/fd
python manage.py syncdb
python manage.py migrate
python manage.py migrate reversion 0001 --fake
python manage.py migrate reversion
