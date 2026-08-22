"""
Endpoint de exercicios.
Retorna exercicios por topico e nivel para a interface do aluno,
junto com o gabarito apos o aluno responder.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from sti.modulo_dominio.exercicios.exercicio import Exercicio
from sti.modulo_dominio.exercicios.gabarito import Gabarito
from sti.infraestrutura.logging_sti import registrar_erro


@require_GET
def exercicios_por_topico(request, topico_id):
    """Retorna exercicios de um topico especifico.

    Endpoint: GET /api/exercicios/<topico_id>/

    Query params opcionais:
        nivel: iniciante | intermediario | avancado

    Returns:
        JSON com lista de exercicios do topico.
    """
    try:
        nivel = request.GET.get("nivel", None)

        exercicios = Exercicio.objects.filter(
            topico_id=topico_id,
            ativo=True,
        )

        if nivel:
            exercicios = exercicios.filter(nivel=nivel)

        lista = [
            {
                "id": ex.id,
                "enunciado": ex.enunciado,
                "nivel": ex.nivel,
            }
            for ex in exercicios
        ]

        return JsonResponse({
            "topico_id": topico_id,
            "total": len(lista),
            "exercicios": lista,
        })

    except Exception as e:
        registrar_erro("Erro no endpoint de exercicios", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )


@require_GET
def gabarito_exercicio(request, exercicio_id):
    """Retorna o gabarito de um exercicio especifico.

    Endpoint: GET /api/exercicios/gabarito/<exercicio_id>/

    Returns:
        JSON com resposta correta e explicacao.
    """
    try:
        gabarito = Gabarito.objects.get(
            exercicio_id=exercicio_id
        )

        return JsonResponse({
            "exercicio_id": exercicio_id,
            "resposta_correta": gabarito.resposta_correta,
            "explicacao": gabarito.explicacao,
        })

    except Gabarito.DoesNotExist:
        return JsonResponse(
            {"erro": "Gabarito nao encontrado."},
            status=404,
        )
    except Exception as e:
        registrar_erro("Erro no endpoint de gabarito", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
