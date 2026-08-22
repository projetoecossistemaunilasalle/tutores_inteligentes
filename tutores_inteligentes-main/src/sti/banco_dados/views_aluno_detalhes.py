"""
Endpoint de detalhes individuais do aluno.
Usado pelo professor para ver o perfil completo
de um aluno especifico — historico, evolucao e emocoes.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.infraestrutura.logging_sti import registrar_erro


@require_GET
def aluno_detalhes(request, aluno_id):
    """Retorna o perfil completo de um aluno para o professor.

    Endpoint: GET /api/aluno/<aluno_id>/detalhes/

    Returns:
        JSON com perfil, ultimas interacoes,
        distribuicao emocional e evolucao de nivel.
    """
    try:
        perfil = PerfilAluno.objects.get(
            identificador=aluno_id
        )

        # Ultimas 10 interacoes
        interacoes = HistoricoInteracoes.objects.filter(
            aluno=perfil
        ).order_by("-data_hora")[:10]

        historico = [
            {
                "pergunta": i.pergunta,
                "resposta": i.resposta,
                "topico": i.topico,
                "origem": i.origem,
                "data_hora": i.data_hora.strftime(
                    "%d/%m/%Y %H:%M"
                ),
            }
            for i in interacoes
        ]

        # Distribuicao de origens
        total = HistoricoInteracoes.objects.filter(
            aluno=perfil
        ).count()
        por_regras = HistoricoInteracoes.objects.filter(
            aluno=perfil, origem="regras"
        ).count()
        por_llm = HistoricoInteracoes.objects.filter(
            aluno=perfil, origem="llm"
        ).count()

        return JsonResponse({
            "aluno": {
                "identificador": perfil.identificador,
                "nome": perfil.nome,
                "nivel": perfil.nivel_proficiencia,
                "estilo": perfil.estilo_aprendizado,
                "estado_emocional": perfil.estado_emocional,
                "criado_em": perfil.criado_em.strftime(
                    "%d/%m/%Y"
                ),
                "atualizado_em": perfil.atualizado_em.strftime(
                    "%d/%m/%Y %H:%M"
                ),
            },
            "interacoes": {
                "total": total,
                "por_regras": por_regras,
                "por_llm": por_llm,
                "historico": historico,
            },
        })

    except PerfilAluno.DoesNotExist:
        return JsonResponse(
            {"erro": "Aluno nao encontrado."},
            status=404,
        )
    except Exception as e:
        registrar_erro("Erro no endpoint de detalhes", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
