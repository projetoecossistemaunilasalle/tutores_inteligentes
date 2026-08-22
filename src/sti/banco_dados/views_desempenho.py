"""
Endpoint de desempenho do aluno.
Retorna os dados necessarios para o dashboard:
nivel atual, taxa de acerto e historico de interacoes.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.infraestrutura.excecoes import AlunoNaoEncontrado
from sti.infraestrutura.logging_sti import registrar_erro


@require_GET
def desempenho(request, aluno_id):
    """Retorna o desempenho atual do aluno para o dashboard.

    Endpoint: GET /api/desempenho/<aluno_id>/

    Returns:
        JSON com nivel, estado emocional, total de interacoes,
        acertos e erros por origem (regras ou LLM).
    """
    try:
        perfil = PerfilAluno.objects.get(identificador=aluno_id)

        # Total de interacoes do aluno
        interacoes = HistoricoInteracoes.objects.filter(aluno=perfil)
        total = interacoes.count()
        por_regras = interacoes.filter(origem="regras").count()
        por_llm = interacoes.filter(origem="llm").count()

        return JsonResponse({
            "aluno_id": aluno_id,
            "nome": perfil.nome,
            "nivel": perfil.nivel_proficiencia,
            "estilo": perfil.estilo_aprendizado,
            "estado_emocional": perfil.estado_emocional,
            "total_interacoes": total,
            "respondido_por_regras": por_regras,
            "respondido_por_llm": por_llm,
        })

    except PerfilAluno.DoesNotExist:
        return JsonResponse(
            {"erro": "Aluno nao encontrado."},
            status=404,
        )
    except Exception as e:
        registrar_erro("Erro no endpoint de desempenho", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
