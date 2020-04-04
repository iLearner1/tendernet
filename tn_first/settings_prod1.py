#DEBUG = False
ALLOWED_HOSTS = ['*']

#settings for db on server
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'db2',
        'USER': 'django_shop',
        'PASSWORD': 'ObeFH2FRUSxP7U2WC',
        'HOST': 'localhost',
        'PORT': '',                      # Set to empty string for default.
    }
}