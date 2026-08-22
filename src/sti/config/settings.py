"""Configurações centrais do Django: apps instalados, banco de dados, idioma/fuso.
As chaves das IAs são lidas do .env, que não vai para o GitHub."""

import os
from pathlib import Path

from dotenv import load_dotenv  # pip install python-dotenv

# Raiz do projeto: .../01.1 - SISTEMA TUTORES INTELIGENTES
# (settings.py está em src/sti/config/, então subimos 3 níveis.)
BASE_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = BASE_DIR / "data"

# Carrega as variáveis do arquivo .env (que fica na raiz do projeto).
# É isto que faz o os.getenv() conseguir ler a GROQ_API_KEY, EXA_API_KEY, etc.
load_dotenv(BASE_DIR / ".env")

# --- Segurança / modo de desenvolvimento ---
SECRET_KEY = os.getenv("SECRET_KEY", "dev-inseguro-trocar-em-producao")
DEBUG = True
ALLOWED_HOSTS = []

# --- Apps ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",          # Django REST Framework
    "sti.banco_dados",         # app transversal (modelos do STI)
    "frontend.app",              # app do frontend (views, templates, etc.)
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

ROOT_URLCONF = "sti.config.urls"
WSGI_APPLICATION = "sti.config.wsgi.application"

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

# --- Banco de dados: SQLite (zero configuração, ideal para os testes) ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- Idioma e fuso ---
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ------------------------------------------------------------------ #
# CHAVES DAS IAs (lidas do .env)                                      #
# ------------------------------------------------------------------ #
# LLM (resposta + análise emocional)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
EXA_API_KEY = os.getenv("EXA_API_KEY", "")     # busca semântica (RAG)
OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST", "http://localhost:11434")  # IA local (offline)

# ------------------------------------------------------------------ #
# AUTENTICACAO E INTERFACE (Grupo 2)                                   #
# Usuario customizado, arquivos estaticos e rotas de login/logout.     #
# ------------------------------------------------------------------ #
AUTH_USER_MODEL = "app.Usuario"
STATICFILES_DIRS = [BASE_DIR / "src" / "frontend" / "static"]
LOGIN_URL = "/aluno/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
