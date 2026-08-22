"""
Endpoints de notificacoes e conquistas.
Usados pela interface do aluno para exibir
alertas e badges desbloqueados.

Estes endpoints consultam o banco do Grupo 1
e retornam dados que o Grupo 2 usa para
atualizar o painel do aluno em tempo real.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.infraestrutura.logging_sti import registrar_erro
import json


@require_GET
def resumo_aluno(request, aluno_id):
    """Retorna um resumo rapido do aluno para o dashboard.

    Endpoint: GET /api/resumo/<aluno_id>/

    Usado pelo dashboard lateral do aluno — mostra
    nivel, total de interacoes e estado emocional atual.

    Returns:
        JSON com dados resumidos do aluno.
    """
    try:
        perfil = PerfilAluno.objects.get(
            identificador=aluno_id
        )

        total = HistoricoInteracoes.objects.filter(
            aluno=perfil
        ).count()

        # Topicos mais discutidos
        topicos = {}
        interacoes = HistoricoInteracoes.objects.filter(
            aluno=perfil
        ).exclude(topico="")
        for i in interacoes:
            topicos[i.topico] = topicos.get(i.topico, 0) + 1

        # Top 3 topicos
        top_topicos = sorted(
            topicos.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:3]

        return JsonResponse({
            "identificador": perfil.identificador,
            "nome": perfil.nome,
            "nivel": perfil.nivel_proficiencia,
            "estilo": perfil.estilo_aprendizado,
            "estado_emocional": perfil.estado_emocional,
            "total_interacoes": total,
            "top_topicos": [
                {"topico": t, "total": n}
                for t, n in top_topicos
            ],
        })

    except PerfilAluno.DoesNotExist:
        return JsonResponse(
            {"erro": "Aluno nao encontrado."},
            status=404,
        )
    except Exception as e:
        registrar_erro("Erro no endpoint de resumo", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )


@csrf_exempt
@require_POST
def registrar_topico(request, aluno_id):
    """Atualiza o topico da ultima interacao do aluno.

    Endpoint: POST /api/topico/<aluno_id>/

    Chamado pelo Grupo 2 quando identifica o topico
    da conversa para enriquecer o historico.

    Body JSON:
        topico (str): nome do topico identificado.
    """
    try:
        perfil = PerfilAluno.objects.get(
            identificador=aluno_id
        )
        dados = json.loads(request.body)
        topico = dados.get("topico", "").strip()

        if not topico:
            return JsonResponse(
                {"erro": "topico e obrigatorio."},
                status=400,
            )

        # Atualiza a ultima interacao sem topico
        ultima = HistoricoInteracoes.objects.filter(
            aluno=perfil, topico=""
        ).order_by("-data_hora").first()

        if ultima:
            ultima.topico = topico
            ultima.save()

        return JsonResponse({"status": "ok", "topico": topico})

    except PerfilAluno.DoesNotExist:
        return JsonResponse(
            {"erro": "Aluno nao encontrado."},
            status=404,
        )
    except Exception as e:
        registrar_erro("Erro ao registrar topico", e)
        return JsonResponse(
            {"erro": "Erro interno do servidor."},
            status=500,
        )
