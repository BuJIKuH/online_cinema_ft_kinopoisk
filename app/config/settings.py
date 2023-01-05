"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 4.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
from pathlib import Path
from dotenv import load_dotenv

from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get('DEBUG'))

# Quick-start development settings - unsuitable for production

include(
    'components/database.py',
    'components/installed_apps.py',
    'components/middleware.py',
    'components/auth_password_validators.py',
    'components/rest_framework.py',
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

ROOT_URLCONF = 'config.urls'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', "127.0.0.1").split(' ')
# CSRF_TRUSTED_ORIGINS = [os.environ.get('CSRF_TRUSTED_ORIGINS').split(' ')]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Internationalization

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'

# Default primary key field type

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# управление переводами
LOCALE_PATHS = ['movies/locale']

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'movies')

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = ["http://127.0.0.1:8080",
                        "http://localhost:8080",
                        ]

# if using Docker the following will set your INTERNAL_IPS
if DEBUG:
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [
        ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]