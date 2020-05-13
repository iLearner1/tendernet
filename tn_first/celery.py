from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta
# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tn_first.settings")

app = Celery("tn_first", broker=settings.CELERY_BROKER_URL)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'home.tasks.test',
        'schedule': timedelta(minutes=1)
    },
}

app.conf.timezone = 'UTC'

# if __name__ == "__main__":
#     app.start()
