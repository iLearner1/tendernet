"""
Django settings for tn_first project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
from celery.schedules import crontab

import os
from decouple import config
from django.conf.locale.en import formats as en_formats
from django.conf.locale.ru import formats as ru_formats

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "9=&2%kp!g-o#ns78dsswqj44kmivxuh7pk63%czd4hyl57nh_e"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=False, cast=bool)
# ALLOWED_HOSTS = ['78.40.109.22', 'http://www.tendernet.kz', 'http://tendernet.kz', 'https://www.tendernet.kz', 'https://tendernet.kz']
# ALLOWED_HOSTS = ['tendernet.kz','http://www.tendernet.kz','78.40.109.22', 'http://tendernet.kz','http://localhost','127.0.0.1']
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")], default="tendernet.kz,http://www.tendernet.kz,78.40.109.22,http://tendernet.kz,http://localhost,127.0.0.1"
)


# Application definition

INSTALLED_APPS = [
    "django_crontab",
    "users.apps.UsersConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "home.apps.HomeConfig",
    "lots.apps.LotsConfig",
    "zakaz.apps.ZakazConfig",
    "django_filters",
    "widget_tweaks",
    "django.contrib.admin",
    "phonenumber_field",
    # bootstrap modal forms
    "bootstrap_modal_forms",
    'django_celery_beat',
]

# CRONJOBS = [
#     ('*/5 * * * *', 'lots.tasks.fetch_lots_from_goszakup')
# ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'tn_first.middleware.SaveCurrentDomain'
]

ROOT_URLCONF = "tn_first.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATES_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "tn_first.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

#DATABASES = {
#    "default": {
#        "ENGINE": "django.db.backends.sqlite3",
#        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
#    }
#}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME', default='db1', cast=str),
        'USER': config('DB_USER', default='root', cast=str),
        'PASSWORD': config('DB_PASSWORD', default='nurzhol@123', cast=str),
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator", },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator", },
]


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
)


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Asia/Almaty"

USE_I18N = True

USE_L10N = True

USE_TZ = True


en_formats.DATETIME_FORMAT = "Y-m-d H:i:s"
ru_formats.DATETIME_FORMAT = "Y-m-d H:i:s"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = "/webapps/django_shop/tendernet/static-files/"

if DEBUG:
#    STATIC_ROOT = None
    STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"  # Сервер для отправки сообщений
EMAIL_HOST_USER = "tendernet.kz@gmail.com"  # имя пользователя
EMAIL_USE_TLS = True  # использование протокола шифрования
EMAIL_HOST_PASSWORD = "tendernetkz2020"  # пароль от ящика
EMAIL_PORT = 587  # порт для подключения
# email, с которого будет отправлено письмо



# EMAIL_HOST = "smtp.mail.ru"  # Сервер для отправки сообщений
# EMAIL_HOST_USER = "tendernetkz@mail.ru"  # имя пользователя
# EMAIL_USE_TLS = True  # использование протокола шифрования
# EMAIL_HOST_PASSWORD = "asdfasdgasdfhgasdfg"  # пароль от ящика
# EMAIL_PORT = 465  # порт для подключения
# # # # email, с которого будет отправлено письмо


EMAIL_MANAGER = "tendernet.kz@gmail.com"
DEFAULT_FROM_EMAIL = "email@tendernet.kz"

# revice mail after contact form submit
CONTACT_MAIL_RECEIVER = 'tendernetkz@mail.ru'
CONTACT_MAIL_SENDER = 'tendernet.kz@gmail.com'

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "/accounts/login/"


# it will need for show warning message if user seaech with empty value
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# CELERY_RESULT_BACKEND = 'django-db'
# CELERY_CACHE_BACKEND = 'django-cache'
redis_port = config('custom_redis_port', cast=int, default=6379)

CELERY_BROKER_URL = f"redis://localhost:{redis_port}"
CELERY_RESULT_BACKEND = f"redis://localhost:{redis_port}"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 *24 * 365

# cache backend
#CACHES = {
#    'default': {
#        'BACKEND': 'django_redis.cache.RedisCache',
#        'LOCATION': f'redis://127.0.0.1:{redis_port}/',
#        'OPTIONS': {
#            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#        }
#    }
#}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}


if not DEBUG:
   # uncomment for server/ comment for local server
   # now user don't have to commnent uncomment above line everytime just have to change
   # .env file values acroding to user need production or development
    try:
        from .settings_prod1 import *
    except:
        pass
