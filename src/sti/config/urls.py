"""Rotas do STI."""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

def home(request):
    """Rota de teste: confirma que o sistema esta no ar."""
    return JsonResponse({"sistema": "STI", "status": "ok", "grupo": 1})

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
]
