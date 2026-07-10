"""
Ponto central do Motor de IA. Recebe a pergunta do aluno,
aciona as camadas na ordem certa e devolve a resposta final.

Ordem de decisão (mais barato -> mais caro):
  1. IA Estruturada (regras + Q&A) — sem custo
  2. RAG (busca no material do professor) — sem custo
  3. LLM Groq (só se as anteriores não resolverem) — com custo

responder() é a única função que a Interface (Grupo 2) chama.
"""

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.modulo_dominio.rag.buscador import buscar, montar_contexto
from sti.motor_ia.ia_estruturada.motor_regras import (
    processar_com_regras,
)
from sti.motor_ia.ia_embarcada.llm_nuvem import gerar_resposta


def responder(pergunta_aluno: str, aluno_id: str) -> dict:
    """Ponto de entrada para a Interface (Grupo 2).

    Args:
        pergunta_aluno: texto digitado pelo aluno.
        aluno_id: identificador do aluno no banco.

    Returns:
        dict com as chaves:
            resposta (str): texto da resposta do tutor.
            fontes (list): trechos do RAG usados.
            aluno_id (str): identificador do aluno.
    """
    # 1) Busca o perfil do aluno no banco.
    perfil = PerfilAluno.objects.get(identificador=aluno_id)
    nivel = perfil.nivel_proficiencia
    estilo = perfil.estilo_aprendizado

    # 2) Tenta responder com regras e Q&A (sem custo).
    resposta = processar_com_regras(pergunta_aluno, nivel)
    fontes = []
    origem = "regras"

    # 3) Se as regras não resolveram, aciona o RAG + Groq.
    if not resposta:
        trechos = buscar(pergunta_aluno)
        contexto = montar_contexto(trechos)
        resposta = gerar_resposta(
            pergunta_aluno, contexto, nivel, estilo
        )
        fontes = trechos
        origem = "llm"

    # 4) Registra a interação no histórico.
    HistoricoInteracoes.objects.create(
        aluno=perfil,
        pergunta=pergunta_aluno,
        resposta=resposta,
        origem=origem,
    )

    return {
        "resposta": resposta,
        "fontes": fontes,
        "aluno_id": aluno_id,
    }
