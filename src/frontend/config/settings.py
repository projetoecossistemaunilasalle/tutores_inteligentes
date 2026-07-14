"""
Configurações do Django para o Grupo 2 (Frontend).
Grupo 2: interface, ambiente de aprendizagem e integração visual.

Rodar o servidor do frontend:
    python manage_frontend.py runserver 8001
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Raiz do projeto
BASE_DIR = Path(__file__).resolve().parents[3]

load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv(
    "SECRET_KEY_FRONTEND", "dev-frontend-trocar-em-producao"
)
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Apps do Grupo 2 (adicionar conforme for implementando)
    # "frontend.usuarios",
    # "frontend.conversas",
    # "frontend.disciplinas",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "frontend.config.urls"
WSGI_APPLICATION = "frontend.config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "src" / "frontend" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

# Banco de dados do Grupo 2 (SQLite separado do Grupo 1)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db_frontend.sqlite3",
    }
}

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "src" / "frontend" / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# URL da API do Grupo 1 (backend)
# Em desenvolvimento: http://127.0.0.1:8000
# Em produção: URL do Render
API_BACKEND_URL = os.getenv(
    "API_BACKEND_URL", "http://127.0.0.1:8000"
)
