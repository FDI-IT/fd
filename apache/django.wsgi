import os
import sys
import django

sys.path.append('/var/www/django/fd')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ["CELERY_LOADER"] = "django"

def application(environ, start_response):
	os.environ['DJANGO_DATABASE_NAME'] = environ['DJANGO_DATABASE_NAME']
	#os.environ['DJANGO_DATABASE_USER'] = environ['DJANGO_DATABASE_USER']
	#os.environ['DJANGO_DATABASE_HOST'] = environ['DJANGO_DATABASE_HOST']
	#os.environ['DJANGO_DATABASE_PASSWORD'] = environ['DJANGO_DATABASE_PASSWORD']
	return _application(environ, start_response)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

    django.setup()