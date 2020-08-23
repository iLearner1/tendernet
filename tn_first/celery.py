from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from datetime import timedelta


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tn_first.settings")

app = Celery("tn_first", broker=settings.CELERY_BROKER_URL)

app.config_from_object("django.conf:settings")

app.autodiscover_tasks()

app.conf.CELERYBEAT_SCHEDULE = {
    'fetch-lots-from-goszakup-every-20-minutes': {
            'task': 'lots.tasks.fetch_lots_from_goszakup',
            'schedule': 1200, #20minutes

        },
    'update_existing_region_location': {
        'task': 'lots.tasks.update_existing_lots_region_location',
        'schedule': 60,
    }
    }
if __name__ == "__main__":
    app.start()

