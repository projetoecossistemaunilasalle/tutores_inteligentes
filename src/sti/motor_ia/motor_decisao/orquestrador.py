"""
Ponto central do Motor de IA. Recebe a pergunta do aluno,
aciona as camadas na ordem certa e devolve a resposta final.

Ordem de decisao (mais barato -> mais caro):
  1. IA Estruturada (regras + Q&A) — sem custo
  2. RAG (busca no material do professor) — sem custo de LLM na busca
  3a. LLM Groq COM material (quando o RAG encontrou trecho relevante)
  3b. LLM Groq SEM material / conhecimento proprio, com aviso
      (Opcao 2: quando o RAG nao encontrou nada relevante,
       para nao deixar o aluno sem resposta)

responder() e a unica funcao que a Interface (Grupo 2) chama.
"""

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.modulo_dominio.rag.buscador import (
    buscar_com_relevancia,
    montar_contexto,
)
from sti.motor_ia.ia_estruturada.motor_regras import (
    processar_com_regras,
)
from sti.motor_ia.ia_embarcada.llm_nuvem import gerar_resposta


def responder(pergunta_aluno: str, aluno_id: str) -> dict:
    """Ponto de entrada para a Interface (Grupo 2).

    Returns:
        dict com: resposta, fontes, usou_rag, origem, aluno_id.
    """
    # 1) Perfil do aluno.
    perfil = PerfilAluno.objects.get(identificador=aluno_id)
    nivel = perfil.nivel_proficiencia
    estilo = perfil.estilo_aprendizado

    # 2) Camada 1 — regras e Q&A (sem custo).
    resposta = processar_com_regras(pergunta_aluno, nivel)
    fontes = []
    origem = "regras"
    usou_rag = False

    if not resposta:
        # 3) Camada 2 — RAG: busca e informa se ha material relevante.
        trechos, tem_relevante = buscar_com_relevancia(pergunta_aluno)

        if tem_relevante:
            # 3a) Ha material relevante: Groq responde COM base nele.
            contexto = montar_contexto(trechos)
            resposta = gerar_resposta(
                pergunta_aluno, contexto, nivel, estilo,
                modo="material",
            )
            fontes = trechos
            origem = "rag"
            usou_rag = True
        else:
            # 3b) Opcao 2 — sem material relevante:
            # Groq responde do proprio conhecimento, com aviso.
            resposta = gerar_resposta(
                pergunta_aluno, "", nivel, estilo,
                modo="conhecimento_geral",
            )
            fontes = []
            origem = "iagen"
            usou_rag = False

    # 4) Registra a interacao no historico.
    HistoricoInteracoes.objects.create(
        aluno=perfil,
        pergunta=pergunta_aluno,
        resposta=resposta,
        origem=origem,
        usou_rag=usou_rag,
        fontes_rag="\n---\n".join(fontes) if fontes else "",
    )

    return {
        "resposta": resposta,
        "fontes": fontes,
        "usou_rag": usou_rag,
        "origem": origem,
        "aluno_id": aluno_id,
    }
