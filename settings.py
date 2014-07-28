# Django settings for fd project.

from LOCAL_SECRETS import DATABASES, SECRET_KEY

DEBUG =True 
TEMPLATE_DEBUG = DEBUG

AUTH_PROFILE_MODULE = 'personnel.UserProfile'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ADMINS = (
    ('Stephan Stachurski', 'steves@flavordynamics.com'),
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

LOGIN_URL = '/accounts/login/'

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

STATIC_ROOT = ''
STATIC_URL = '/djangomedia/'
STATICFILES_DIRS = ('/var/www/django/fd/staticmedia',)


# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/djangomedia/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/djangomedia/'
#MEDIA_URL = 'http://localhost:8000/djangomedia/'
#MEDIA_URL = '/staticmedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/djangoadminmedia/'


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)



TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
)


MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', 
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'reversion.middleware.RevisionMiddleware',
    #'history_audit.middleware.MyMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
                 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/django/fd/dtemplates',
)

#
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.databrowse',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.humanize',
    #'django.contrib.admindocs',
    'django.contrib.formtools',
    'django.contrib.comments',
    'django.contrib.databrowse',
    'django.contrib.messages',
    'djcelery',
    'south',
    'reversion',
    'pluggable',
    'homepage', 
    'haccp',
    'access',
    'newqc',
    'personnel',
    'salesorders',
    'invoices',
    'solutionfixer',
    'mysearch',
    'flavor_usage',
    'performance_appraisal',
    'formfieldset',
    'batchsheet',
    'docvault',
    'unified_adapter',
    'reports',
    'hazard_calculator',
    #'history_audit',
)

# Celery configuration
import djcelery
djcelery.setup_loader()
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"  # Maps to redis host.
BROKER_PORT = 6379         # Maps to redis port.
BROKER_VHOST = "0"         # Maps to database number.
CELERY_RESULT_BACKEND = "djcelery.backends.database.DatabaseBackend"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0

from datetime import timedelta
CELERYBEAT_SCHEDULE = {
    "walk_scanned_docs-every-30-seconds": {
        "task": "newqc.tasks.walk_scanned_docs",
        "schedule": timedelta(seconds=5),
        "args": ()
    },
}

SOUTH_TESTS_MIGRATE = False

LOG_PATH = '/var/log/django/'
DUMP_DIR = '/var/www/django/dump'
CSVSOURCE_PATH = '/var/www/django/dump/sample_data/sql_files'
MDB_FILE = 'flv.mdb'
CSVTEST_PATH = '/var/www/django/dump/sql_filestt'
CSVEXCEPTION_PATH = '/var/www/django/dump/exceptions'

