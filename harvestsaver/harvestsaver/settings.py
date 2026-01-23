import os
import logging
from logging.handlers import RotatingFileHandler

from pathlib import Path

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-dgu5*^9cexga$udi7@__0lwjbhm3lrkm7@c$320l!!)drw*onu'

ALLOWED_HOSTS = ["127.0.0.1", "54.237.207.136",
                 "www.pysoftware.tech", "pysoftware.tech"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "accounts",
    "farm",
    "transit",
    "api",
    "payment",
    "rest_framework",
    "crispy_forms",
    "crispy_bootstrap4",
    "django.contrib.humanize",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'harvestsaver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
        # BASE_DIR / "templates" for tempates at project level
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                "harvestsaver.context_processors.common_variables",
            ],
            "builtins":[
                "crispy_forms.templatetags.crispy_forms_tags",
            ],
        },
    },
]

WSGI_APPLICATION = 'harvestsaver.wsgi.application'

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True

AUTH_USER_MODEL = "accounts.User"

CRISPY_TEMPLATE_PACK = 'bootstrap4'

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR / "static")]

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get("PGDATABASE"),
            'USER': os.environ.get("PGUSER"),
            'PASSWORD': os.environ.get("PASSWORD"),
            'HOST': os.environ.get("HOST"),
            'PORT': os.environ.get("PORT"),
            }
        }

#setting for sendimg email
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
EMAIL_PORT = os.environ.get("EMAIL_PORT")
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS")
EMAIL_BACKEND = os.environ.get("EMAIL_BACKEND")

# strip setup
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# weather
WEATHER_API_KEY = os.environ.get("WEATHER_API_KEY")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",  # db 1 for cache
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
#            "class": "logging.FileHandler",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "harvestsaver.log",
            "formatter": "verbose",
            "maxBytes": 10485760,
            "backupCount": 5,     # Number of backup log files to retain
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "propagate": True,
            "level": "ERROR",  # from debug
        },
        "MYAPP": {
            "handlers": ["file"],
            "level": "ERROR",  # from debug
        },
    },
}

