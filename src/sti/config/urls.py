"""
Rotas do STI — todas as rotas do sistema.
"""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from sti.banco_dados.chat_view import chat, perguntar
from sti.banco_dados.views_desempenho import desempenho
from sti.banco_dados.views_exercicios import (
    exercicios_por_topico,
    gabarito_exercicio,
)


def home(request):
    """Rota raiz — confirma que o sistema esta no ar."""
    return JsonResponse({
        "sistema": "STI",
        "status": "ok",
        "grupo": 1,
        "rotas": {
            "chat": "/chat/",
            "api_perguntar": "/api/perguntar/",
            "api_desempenho": "/api/desempenho/<aluno_id>/",
            "api_exercicios": "/api/exercicios/<topico_id>/",
            "api_gabarito": "/api/exercicios/gabarito/<exercicio_id>/",
        },
    })


urlpatterns = [
    # Raiz e admin
    path("", home),
    path("admin/", admin.site.urls),

    # Interface de teste
    path("chat/", chat, name="chat"),

    # API — Chat
    path("api/perguntar/", perguntar, name="perguntar"),

    # API — Desempenho
    path(
        "api/desempenho/<str:aluno_id>/",
        desempenho,
        name="desempenho",
    ),

    # API — Exercicios
    path(
        "api/exercicios/<int:topico_id>/",
        exercicios_por_topico,
        name="exercicios",
    ),
    path(
        "api/exercicios/gabarito/<int:exercicio_id>/",
        gabarito_exercicio,
        name="gabarito",
    ),
]
