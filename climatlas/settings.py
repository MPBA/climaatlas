# -*- coding: utf-8 -*-
"""
Django settings for climatlas project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SITE_NAME = "ClimaAtlas"
SITE_ID = 1
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9dvjjlf)u%dw!1!7(li9=xy0xfut2xno)52&xck-nq+1srrv6h'

DEBUG = True

# SECURITY WARNING: don't run with debug turned on in production!
# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)


# Application definition

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.gis',
    'django_hstore',
    'redactor',
    'export_xls',
    'dataupload',
    'menu',
    'climatlas',
    'analysis',
    'exhibit'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.static",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "climatlas.context_processors.custom_settings",
)

ROOT_URLCONF = 'climatlas.urls'

WSGI_APPLICATION = 'climatlas.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases



# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
UPLOAD_PATH = 'files/'

FILE_UPLOAD_MAX_MEMORY_SIZE = 5221440

FILE_UPLOAD_HANDLERS = (
    "django.core.files.uploadhandler.MemoryFileUploadHandler",
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

STATIC_ROOT = ''
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),

)

##################
# FILE UPLOADER  #
##################
import re
FILE_EXT = re.compile(r'^.*?[.](?P<ext>\.zip|tar\.gz|tar\.bz2|\w+)$')
VALID_EXTTENSIONS = ['zip']
STAZIONI_NAMES = ['site.dbf', 'site.fpt', 'site.cdx']
DATI_NAMES = ['pioggia.txt', 'tempmax.txt', 'tempmin.txt']

####################
# MAPPE CLIMATICHE #
####################
LAYER_TYPE = (
    ('p', 'Precipitazione'),
    ('t', 'Temperatura'),
)

LAYER_TYPE_ANOMALIE = (
    ('p', 'Precipitazione assoluta', 'd'),
    ('p', 'Precipitazione percentuale', 'p'),
    ('t', 'Temperatura assoluta', 'd'),
)
LAYER_SUFFIX = (
    ('d', 'Differenza assoluta'),
    ('p', 'Differenza in percentuale')
)

LAYER_PERIOD = (
    ('1961-1990'),
    ('1971-2000'),
    ('1981-2010'),
)

LAYER_YEAR = range(1941, 2011, 1)

LAYER_MONTH = (
    ('01', 'Gennaio', 'PrecipitazioniMensili', 'M'),
    ('02', 'Febbraio', 'PrecipitazioniMensili', 'M'),
    ('03', 'Marzo', 'PrecipitazioniMensili', 'M'),
    ('04', 'Aprile', 'PrecipitazioniMensili', 'M'),
    ('05', 'Maggio', 'PrecipitazioniMensili', 'M'),
    ('06', 'Giugno', 'PrecipitazioniMensili', 'M'),
    ('07', 'Luglio', 'PrecipitazioniMensili', 'M'),
    ('08', 'Agosto', 'PrecipitazioniMensili', 'M'),
    ('09', 'Settembre', 'PrecipitazioniMensili', 'M'),
    ('10', 'Ottobre', 'PrecipitazioniMensili', 'M'),
    ('11', 'Novembre', 'PrecipitazioniMensili', 'M'),
    ('12', 'Dicembre', 'PrecipitazioniMensili', 'M'),
    ('', 'Annuale', 'PrecipitazioniAnnuali', 'A'),
    ('1win', 'Inverno', 'PrecipitazioniStagionali', 'S'),
    ('2spr', 'Primavera', 'PrecipitazioniStagionali', 'S'),
    ('3sum', 'Estate', 'PrecipitazioniStagionali', 'S'),
    ('4aut', 'Autunno', 'PrecipitazioniStagionali', 'S'),
)


GEOSERVER_URL = 'https://climatlas.fbk.eu/geoserver'
OSM_URL = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

MAPS_ATTRIBUTION_FBK = '@ PAT Climatrentino'
MAPS_ATTRIBUTION_OSM = '© <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'

EXPORT_MAP_BASE_PATH = '/media/datapart/fbk/code/climaatlas/climaatlas/analysis/'


##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
try:
    from local_settings import *
except ImportError:
    pass