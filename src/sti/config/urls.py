"""
Rotas do STI — inclui o chat de teste.
Substitui o conteúdo de src/sti/config/urls.py
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from sti.banco_dados import views as api_views
from sti.banco_dados.chat_view import chat, perguntar


def home(request):
    return JsonResponse({
        "sistema": "STI",
        "status": "ok",
        "grupo": 1,
        "chat": "/chat/",
        "api": "/api/perguntar/",
    })


urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("chat/", chat, name="chat"),
    path("api/perguntar/", perguntar, name="perguntar"),
]
