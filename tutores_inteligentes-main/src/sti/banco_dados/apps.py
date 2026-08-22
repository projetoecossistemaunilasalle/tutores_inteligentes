"""App Django da camada transversal de dados."""
from django.apps import AppConfig

class BancoDadosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sti.banco_dados"
