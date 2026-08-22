"""
Endpoint de metricas gerais da turma.
Usado pelo dashboard do professor para ver
o desempenho geral de todos os alunos.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.infraestrutura.logging_sti import registrar_erro


@require_GET
def turma(request):
    """Retorna metricas gerais da turma para o professor.

    Endpoint: GET /api/turma/

    Returns:
        JSON com total de alunos, distribuicao por nivel,
        total de interacoes, custo (regras x LLM) e
        alunos que precisam de atencao.
    """
    try:
        alunos = PerfilAluno.objects.all()
        total = alunos.count()

        # Distribuicao por nivel
        iniciantes = alunos.filter(
            nivel_proficiencia="iniciante"
        ).count()
        intermediarios = alunos.filter(
            nivel_proficiencia="intermediario"
        ).count()
        avancados = alunos.filter(
            nivel_proficiencia="avancado"
        ).count()

        # Total de interacoes
        interacoes = HistoricoInteracoes.objects.all()
        total_interacoes = interacoes.count()
        por_regras = interacoes.filter(origem="regras").count()
        por_llm = interacoes.filter(origem="llm").count()

        # Alunos que mais interagiram
        # (potencial indicador de dificuldade)
        alunos_ativos = []
        for aluno in alunos:
            total_aluno = HistoricoInteracoes.objects.filter(
                aluno=aluno
            ).count()
            if total_aluno > 0:
                alunos_ativos.append({
                    "identificador": aluno.identificador,
                    "nome": aluno.nome,
                    "nivel": aluno.nivel_proficiencia,
                    "total_interacoes": total_aluno,
                    "estado_emocional": aluno.estado_emocional,
                })

        # Ordena por mais interacoes (possivel dificuldade)
        alunos_ativos.sort(
            key=lambda x: x["total_interacoes"],
            reverse=True,
        )

        return JsonResponse({
            "total_alunos": total,
            "por_nivel": {
                "iniciante": iniciantes,
                "intermediario": intermediarios,
                "avancado": avancados,
            },
            "interacoes": {
                "total": total_interacoes,
                "por_regras": por_regras,
                "por_llm": por_llm,
            },
            "alunos_em_destaque": alunos_ativos[:5],
        })

    except Exception as e:
        registrar_erro("Erro no endpoint de turma", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
