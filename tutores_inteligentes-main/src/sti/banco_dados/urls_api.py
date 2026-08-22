"""
Rotas da API do STI.
Adicione este arquivo em config/urls.py usando include().
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from sti.banco_dados import views as api_views


def home(request):
    """Rota raiz — confirma que o sistema esta no ar."""
    return JsonResponse({
        "sistema": "STI",
        "status": "ok",
        "grupo": 1,
        "api": "/api/perguntar/",
    })


# Rotas da API — prefixo /api/
api_urlpatterns = [
    path("perguntar/", api_views.perguntar, name="perguntar"),
]

# Rotas principais
urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/", include(api_urlpatterns)),
]
