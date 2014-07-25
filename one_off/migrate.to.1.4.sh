#!/bin/bash
# RUN SQL COMMAND FIRST
cd /var/www/django/fd
python manage.py syncdb
python manage.py migrate
mv reversion/ /var/www/django/packages/reversion_old
python manage.py migrate reversion 0001 --fake
python manage.py migrate reversion