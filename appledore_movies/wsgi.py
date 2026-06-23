"""
WSGI config for appledore_movies project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.conf import settings
import django

from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
if not settings.DEBUG:
    import newrelic.agent  # noqa: E402

    os.environ["NEW_RELIC_LICENSE_KEY"] = os.getenv("NEW_RELIC_LICENSE_KEY", "")
    os.environ["NEW_RELIC_APP_NAME"] = "Movies Service"
    newrelic.agent.initialize("newrelic.ini")

django.setup()

if not settings.DEBUG:
    application = newrelic.agent.WSGIApplicationWrapper(get_wsgi_application())
else:
    application = get_wsgi_application()
