"""
Configuracao do app Django do frontend (Grupo 2).
"""

from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "frontend.app"
    verbose_name = "Frontend STI"
