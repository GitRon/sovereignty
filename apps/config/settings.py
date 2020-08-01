"""
Django settings for apps project.

Generated by 'django-admin startproject' using Django 2.1.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import sys

import environ

# Base paths
ROOT_DIR = environ.Path(__file__) - 2
APPS_DIR = ROOT_DIR.path('../')

env = environ.Env(
    # django
    DJANGO_DEBUG=(bool, False),
    DJANGO_THUMBNAIL_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, 'xsol_k1p3cd1!g&3owtw1)etfy8c=^ts#mk^rm%9_3*pp9i@7p'),
    DJANGO_ADMINS=(list, []),
    DJANGO_ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    DJANGO_SESSION_COOKIE_SECURE=(bool, True),
    DJANGO_SERVER_URL=(str, 'http://localhost:8000'),
    # Files
    DJANGO_STATIC_ROOT=(str, str(APPS_DIR('staticfiles'))),
    DJANGO_MEDIA_ROOT=(str, str(APPS_DIR('media'))),
    # Database
    DJANGO_DATABASE_URL=(str, 'sqlite://sovereignty.db'),
)

environ.Env.read_env()

DEBUG = env.bool("DJANGO_DEBUG")
THUMBNAIL_DEBUG = env.bool("DJANGO_THUMBNAIL_DEBUG")
SECRET_KEY = env('DJANGO_SECRET_KEY')
ADMINS = tuple([tuple(admins.split(':')) for admins in env.list('DJANGO_ADMINS')])
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')
SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE')
SERVER_URL = env('DJANGO_SERVER_URL')

IS_TESTING = False
if 'test' in sys.argv or 'test_coverage' in sys.argv:
    IS_TESTING = True


# Application definition

INSTALLED_APPS = [
    # django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'crispy_forms',

    # Local
    'apps.account',
    'apps.castle',
    'apps.config',
    'apps.core',
    'apps.dynasty',
    'apps.location',
    'apps.messaging',
    'apps.military',
    'apps.naming',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.military.middlewares.RedirectToActiveBattleMiddleware',
]

ROOT_URLCONF = 'apps.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(str(APPS_DIR), 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.current_savegame',
            ],
        },
    },
]

WSGI_APPLICATION = 'apps.config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

# Database
DATABASE_PARAMS = env.db('DJANGO_DATABASE_URL')
DATABASES = {
    'default': DATABASE_PARAMS
}

if DATABASES['default']['ENGINE'] != 'django.db.backends.sqlite3':
    DATABASES['default']['OPTIONS'] = {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = 'de-at'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/
STATIC_ROOT = env('DJANGO_STATIC_ROOT')
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    str(APPS_DIR) + '/node_modules/',
    str(APPS_DIR) + '/static/',
)

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT')
