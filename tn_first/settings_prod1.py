ALLOWED_HOSTS += ['tendernet.kz', '78.40.109.22', 'www.tendernet.kz']

# settings for db on server
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql_psycopg2",
#         "NAME": "db2",
#         "USER": "django_shop",
#         "PASSWORD": "ObeFH2FRUSxP7U2WC",
#         "HOST": "localhost",
#         "PORT": "",  # Set to empty string for default.
#     }
# }
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
