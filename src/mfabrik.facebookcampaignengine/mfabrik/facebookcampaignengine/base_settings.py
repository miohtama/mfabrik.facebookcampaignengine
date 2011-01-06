import os

# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

SECRET_KEY = 'moowashere'

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.sites',
    'djangotoolbox',

    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
    'mfabrik.facebookcampaignengine'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

ADMIN_MEDIA_PREFIX = '/media/admin/'
TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

ROOT_URLCONF = 'urls'

SITE_ID = 29

# Activate django-dbindexer if available
try:
    import dbindexer
    DATABASES['native'] = DATABASES['default']
    DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
    INSTALLED_APPS += ('dbindexer',)
    DBINDEXER_SITECONF = 'dbindexes'
    MIDDLEWARE_CLASSES = ('dbindexer.middleware.DBIndexerMiddleware',) + \
                         MIDDLEWARE_CLASSES
except ImportError:
    pass

# Facebook settings

#: Facebook keys - you get them after registering your app in Facebook
FACEBOOK_APPLICATION_ID="191057254241074"
FACEBOOK_API_KEY = 'b2b9f2a0f7a00a6c76cd72a40da160e3'
FACEBOOK_SECRET_KEY = '53e242933f872bfc568b6df31cf29fdc'

FACEBOOK_SESSION_KEY = '7a88c3a4b7068cd34b195c59-1230271672'

#: The following appears in URL http://apps.facebook.com/petbook/
FACEBOOK_APP_NAME = "mikkotestcampaign"

# This URL is visible to the application users
FACEBOOK_EXTERNAL_URL="http://apps.facebook.com/" + FACEBOOK_APP_NAME





