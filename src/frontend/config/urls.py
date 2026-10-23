"""Rotas do frontend (Grupo 2)."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


def home(request):
    return JsonResponse({
        "sistema": "STI",
        "grupo": 2,
        "status": "ok",
        "api_backend": "/api/perguntar/ (Grupo 1 - porta 8000)",
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
]
