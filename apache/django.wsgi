import os
import sys
sys.path.append('/usr/local/django/fd')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ["CELERY_LOADER"] = "django"
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
