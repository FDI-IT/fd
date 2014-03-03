# Django settings for fd project.
import os
import sys
sys.path.append(os.getcwd())

DEBUG =True 
TEMPLATE_DEBUG = DEBUG

#HAYSTACK_SITECONF = 'search_sites'
#HAYSTACK_SEARCH_ENGINE = 'whoosh'
#HAYSTACK_WHOOSH_PATH = '/usr/local/django/dump/haystack'

THUMBNAIL_FORMAT = 'PNG'
DUMP_DIR = '/usr/local/django/dump'
#FIXTURE_DIRS = '/usr/local/django/fd/fixtures'
CSVSOURCE_PATH = '/usr/local/django/dump/sample_data/sql_files'
MDB_FILE = 'flv.mdb'
CSVTEST_PATH = '/usr/local/django/dump/sql_filestt'
CSVEXCEPTION_PATH = '/usr/local/django/dump/exceptions'
SOUTH_TESTS_MIGRATE = False

AUTH_PROFILE_MODULE = 'personnel.UserProfile'
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

ADMINS = (
    ('Stephan Stachurski', 'steves@flavordynamics.com'),
)

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

LOGIN_URL = '/django/accounts/login/'

MANAGERS = ADMINS

''

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'fd_test'#os.environ['DJANGO_DATABASE_NAME']             # Or path to database file if using sqlite3.
DATABASE_USER = 'www-data'#os.environ['DJANGO_DATABASE_USER']             # Not used with sqlite3.
DATABASE_PASSWORD = 'fdi'#os.environ['DJANGO_DATABASE_PASSWORD']         # Not used with sqlite3.
DATABASE_HOST = '192.168.10.197'#'192.168.1.129'#'10.1.10.182'#os.environ['DJANGO_DATABASE_HOST']             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

'''
#Use os.environ variables to store remote database information #NOT WORKING
DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = os.environ['DJANGO_DATABASE_NAME']             # Or path to database file if using sqlite3.
DATABASE_USER = os.environ['DJANGO_DATABASE_USER']             # Not used with sqlite3.
DATABASE_PASSWORD = os.environ['DJANGO_DATABASE_PASSWORD']         # Not used with sqlite3.
DATABASE_HOST = os.environ['DJANGO_DATABASE_HOST']             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
'''
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
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/media/djangomedia/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/djangomedia/'
#MEDIA_URL = 'http://localhost:8000/djangomedia/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/djangoadminmedia/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=doe#s2k1d0hv+zl9ar*b44rc=(mpl@datvu1h=30h_kg1sclx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)



TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.csrf.middleware.CsrfMiddleware', 
    'django.contrib.csrf.middleware.CsrfViewMiddleware', 
    'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'reversion.middleware.RevisionMiddleware',
    #'history_audit.middleware.MyMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
                 
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/usr/local/django/fd/dtemplates',
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
    #'djcelery',
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
    'sorl.thumbnail',
    'south',
    'formfieldset',
    'reversion',
    #'fdileague',
    'batchsheet',
    'docvault',
    'unified_adapter',
    'reports',
    #'history_audit',
    #'haystack',
)

# Celery configuration
import djcelery
djcelery.setup_loader()
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"  # Maps to redis host.
BROKER_PORT = 6379         # Maps to redis port.
BROKER_VHOST = "0"         # Maps to database number.
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
