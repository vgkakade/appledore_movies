import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appledore_movies.settings")

app = Celery("appledore_movies")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
