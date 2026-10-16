from .settings import *  # noqa

# Override settings for testing
ELASTICSEARCH_DSL_AUTOSYNC = False
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
CELERY_TASK_ALWAYS_EAGER = True
