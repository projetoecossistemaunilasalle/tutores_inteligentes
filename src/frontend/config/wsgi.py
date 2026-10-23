"""WSGI do frontend (Grupo 2)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "frontend.config.settings"
)
application = get_wsgi_application()
