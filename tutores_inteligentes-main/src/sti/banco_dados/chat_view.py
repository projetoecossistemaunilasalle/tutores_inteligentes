"""
View do chat de teste do STI.
Serve a página HTML do chat e remove o decorator
@apenas_aluno para facilitar os testes iniciais.
"""

import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from sti.motor_ia.motor_decisao.orquestrador import responder
from sti.infraestrutura.logging_sti import registrar_erro
from sti.infraestrutura.excecoes import (
    AlunoNaoEncontrado,
    RespostaNaoGerada,
)


@ensure_csrf_cookie
def chat(request):
    """Serve a página HTML do chat."""
    with open("src/sti/banco_dados/templates/chat.html",
              encoding="utf-8") as f:
        return HttpResponse(f.read())


@require_POST
def perguntar(request):
    """Recebe a pergunta e devolve a resposta do tutor."""
    try:
        dados = json.loads(request.body)
        pergunta = dados.get("pergunta", "").strip()
        aluno_id = dados.get("aluno_id", "").strip()

        if not pergunta or not aluno_id:
            return JsonResponse(
                {"erro": "pergunta e aluno_id sao obrigatorios."},
                status=400,
            )

        resultado = responder(pergunta, aluno_id)
        return JsonResponse(resultado, status=200)

    except AlunoNaoEncontrado:
        return JsonResponse(
            {"erro": "Aluno nao encontrado."},
            status=404,
        )
    except RespostaNaoGerada as e:
        registrar_erro("Falha ao gerar resposta", e)
        return JsonResponse(
            {"erro": "Nao foi possivel gerar uma resposta."},
            status=500,
        )
    except Exception as e:
        registrar_erro("Erro inesperado", e)
        return JsonResponse(
            {"erro": f"Erro interno: {str(e)}"},
            status=500,
        )
