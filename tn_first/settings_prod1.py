DEBUG = False
ALLOWED_HOSTS = ['*']

# to run on local server comment this whole page out. or run python manage.py runserver --settings=tn_first.settings


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
