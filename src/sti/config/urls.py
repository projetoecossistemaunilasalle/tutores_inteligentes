"""
Rotas completas do STI — Grupo 1.
Inclui todos os endpoints para o Grupo 2 consumir.
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
from sti.banco_dados.views_turma import turma
from sti.banco_dados.views_aluno_detalhes import aluno_detalhes
from sti.banco_dados.views_notificacoes import (
    resumo_aluno,
    registrar_topico,
)


def home(request):
    """Rota raiz — lista todas as rotas disponiveis."""
    return JsonResponse({
        "sistema": "STI",
        "status": "ok",
        "grupo": 1,
        "rotas": {
            # Interface de teste
            "chat": "/chat/",

            # API — Aluno
            "perguntar":     "POST /api/perguntar/",
            "desempenho":    "GET  /api/desempenho/<aluno_id>/",
            "resumo":        "GET  /api/resumo/<aluno_id>/",
            "topico":        "POST /api/topico/<aluno_id>/",

            # API — Conteudo
            "exercicios":    "GET  /api/exercicios/<topico_id>/",
            "gabarito":      "GET  /api/exercicios/gabarito/<id>/",

            # API — Professor
            "turma":         "GET  /api/turma/",
            "aluno_detalhes": "GET  /api/aluno/<aluno_id>/detalhes/",
        },
    })


urlpatterns = [
    # Raiz e admin
    path("", home),
    path("admin/", admin.site.urls),

    # Interface de teste
    path("chat/", chat, name="chat"),

    # API — Chat e desempenho do aluno
    path("api/perguntar/", perguntar, name="perguntar"),
    path(
        "api/desempenho/<str:aluno_id>/",
        desempenho,
        name="desempenho",
    ),
    path(
        "api/resumo/<str:aluno_id>/",
        resumo_aluno,
        name="resumo",
    ),
    path(
        "api/topico/<str:aluno_id>/",
        registrar_topico,
        name="topico",
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

    # API — Professor
    path("api/turma/", turma, name="turma"),
    path(
        "api/aluno/<str:aluno_id>/detalhes/",
        aluno_detalhes,
        name="aluno_detalhes",
    ),
]
