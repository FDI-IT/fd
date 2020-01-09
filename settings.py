# Django settings for fd project.
from LOCAL_SECRETS import DATABASES, SECRET_KEY

# Django 1.5+: need ALLOWED_HOSTS or else you get BAD REQUEST (400)
# should this be included in local secrets?
ALLOWED_HOSTS = ['*',
                 # 'localhost',
                 # '192.168.10.xx',
                 ]

# SOUTH_TESTS_MIGRATE = True

DEBUG = True
#TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = ('127.0.0.1',)
# def show_toolbar(request):
#     return True
# SHOW_TOOLBAR_CALLBACK = show_toolbar

DEBUG_TOOLBAR_PATCH_SETTINGS = False

# APPEND_SLASH = False

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# AUTH_PROFILE_MODULE = 'personnel.UserProfile' #get_profile is now deprecated (django 1.6)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

ADMINS = (
    ('Matt Araneta', 'matta@flavordynamics.com'),
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

'''
added all this stuff so static files are deployed when using runserver/testserver
i don't know if this interferes with all the 'media' stuff

to create a test server: python manage.py testserver access/fixtures/testdata.json --addrport 0.0.0.0:8000

'''
STATIC_ROOT = '/var/www/static_root'
STATIC_URL = '/static/'
STATICFILES_DIRS = ('/var/www/django/fd/staticmedia',)
                    # '/var/www/django/fd_react/static/js/bundle.js')

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder"
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/www/djangomedia/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/djangomedia/'
# MEDIA_URL = 'http://localhost:8000/djangomedia/'
# MEDIA_URL = '/staticmedia/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
# )
DEFAULT_CHARSET='utf-8'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            '/var/www/django/fd/dtemplates',
        ],
        #'APP_DIRS': True,
        'OPTIONS': {
            'debug': True,
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                # 'django.template.loaders.eggs.Loader',
            ]
        },
    },
]

# TEMPLATES = (
#     'django.contrib.auth.context_processors.auth',
#     'django.template.context_processors.debug',
#     'django.template.context_processors.i18n',
#     'django.template.context_processors.media',
#     'django.contrib.messages.context_processors.messages',
#     'django.template.context_processors.request',
#     'django.template.context_processors.static',
# )

ATOMIC_REQUESTS = True  # this replaces TransactionMiddleware starting at Django 1.6

MIDDLEWARE = (
    'django.middleware.gzip.GZipMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'middleware.dev_cors_middleware',
    # 'corsheaders.middleware.CorsMiddleware',

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # 'django.middleware.transaction.TransactionMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'reversion.middleware.RevisionMiddleware',
    # 'history_audit.middleware.MyMiddleware',
)

# CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_WHITELIST = ('localhost:3000')

ROOT_URLCONF = 'urls'

# TEMPLATE_DIRS = (
#
#     # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
#     # Always use forward slashes, even on Windows.
#     # Don't forget to use absolute paths, not relative paths.
#     '/var/www/django/fd/dtemplates',
# )

# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# HAYSTACK_CONNECTIONS = {
#     'default': {
#         'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
#         'URL': 'http://elasticsearch:9200/',
#         'INDEX_NAME': 'haystack',
#         'EXCLUDED_INDEXES': ['mysearch.search_indexes.FlavorIndex'],
#     },
# }

DJANGO_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

THIRD_PARTY_APPS = (
    # 'corsheaders',
    'djcelery',
    'reversion',
    #'django_extensions',
    'rest_framework',
    'django_filters',
)

LOCAL_APPS = (
    'api',
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
    'hazards',
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        #         'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        #         'rest_framework.permissions.IsAdminUser',
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        # 'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_METADATA_CLASS': 'api.serializers.FDIMetadata',

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'URL_FIELD_NAME': 'api_url',
}

# Celery configuration
import djcelery

djcelery.setup_loader()
BROKER_TRANSPORT = "redis"
BROKER_HOST = "localhost"  # Maps to redis host.
BROKER_PORT = 6379  # Maps to redis port.
BROKER_VHOST = "0"  # Maps to database number.
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

LOG_PATH = '/var/log/django/'
DUMP_DIR = '/var/www/django/dump'
CSVSOURCE_PATH = '/var/www/django/dump/sample_data/sql_files'
MDB_FILE = 'flv.mdb'
CSVTEST_PATH = '/var/www/django/dump/sql_filestt'
CSVEXCEPTION_PATH = '/var/www/django/dump/exceptions'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
