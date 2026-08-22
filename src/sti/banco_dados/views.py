"""
Views da API do STI.
Recebe as requisicoes HTTP, chama o orquestrador e
devolve a resposta em JSON para a Interface (Grupo 2).
"""

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from sti.motor_ia.motor_decisao.orquestrador import responder
from sti.seguranca.permissoes import apenas_aluno
from sti.infraestrutura.logging_sti import registrar_erro
from sti.infraestrutura.excecoes import (
    AlunoNaoEncontrado,
    RespostaNaoGerada,
)


@csrf_exempt
@require_POST
@apenas_aluno
def perguntar(request):
    """Recebe a pergunta do aluno e devolve a resposta do tutor.

    Endpoint: POST /api/perguntar/

    Body JSON:
        pergunta (str): texto digitado pelo aluno.
        aluno_id (str): identificador do aluno.

    Returns:
        JSON com resposta, fontes e aluno_id.
    """
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
        registrar_erro("Erro inesperado na view perguntar", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
