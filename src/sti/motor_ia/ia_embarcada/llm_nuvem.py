"""
Cliente do Groq com dois modos de resposta:

  - modo="material": responde APENAS com base no material do RAG
    (comportamento original, fiel ao conteudo do professor).

  - modo="conhecimento_geral": quando o RAG nao encontrou material
    relevante, o tutor responde com seu conhecimento geral de
    Algoritmos e Programacao, avisando ao aluno que a resposta NAO
    veio do material da disciplina (Opcao 2 — nao deixar o aluno
    sem resposta).
"""

import os
from groq import Groq

MODELO_GROQ = "openai/gpt-oss-20b"


def _cliente_groq():
    """Cria o cliente da Groq usando a chave do .env."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def montar_prompt(pergunta, contexto_rag, nivel, estilo, modo="material"):
    """Monta o prompt conforme o modo de resposta."""

    if modo == "material" and contexto_rag.strip():
        instrucao = (
            f"Voce e um tutor de Algoritmos e Programacao. "
            f"O aluno esta no nivel {nivel} e aprende melhor "
            f"de forma {estilo}. "
            f"Responda a pergunta do aluno usando APENAS as "
            f"informacoes do material abaixo. "
            f"Nao use conhecimento proprio — se a resposta nao "
            f"estiver no material, diga: 'Nao encontrei essa "
            f"informacao no material disponivel.' "
            f"Seja claro, didatico e use exemplos do proprio "
            f"material quando existirem.\n\n"
            f"MATERIAL DO PROFESSOR:\n{contexto_rag}"
        )
    else:
        # modo == "conhecimento_geral" (Opcao 2)
        # O RAG nao encontrou material relevante. O tutor responde
        # com conhecimento geral, avisando a origem ao aluno.
        instrucao = (
            f"Voce e um tutor de Algoritmos e Programacao. "
            f"O aluno esta no nivel {nivel} e aprende melhor "
            f"de forma {estilo}. "
            f"O material da disciplina nao cobre este assunto "
            f"especifico. Responda a pergunta do aluno com seu "
            f"conhecimento geral de Algoritmos e Programacao, de "
            f"forma clara e didatica, adequada ao nivel do aluno. "
            f"IMPORTANTE: comece a resposta avisando o aluno de "
            f"que esta informacao NAO foi encontrada no material "
            f"da disciplina e que se trata de uma explicacao geral. "
            f"Sugira que ele confirme o conteudo com o professor."
        )

    return [
        {"role": "system", "content": instrucao},
        {"role": "user", "content": pergunta},
    ]


def gerar_resposta(pergunta, contexto_rag, nivel, estilo, modo="material"):
    """Chama o Groq e devolve a resposta.

    Args:
        pergunta: texto digitado pelo aluno.
        contexto_rag: trechos encontrados pelo RAG (vazio no modo
            conhecimento_geral).
        nivel: nivel de proficiencia do aluno.
        estilo: estilo de aprendizado do aluno.
        modo: "material" (responde pelo RAG) ou "conhecimento_geral"
            (responde com conhecimento proprio, com aviso).

    Returns:
        str: resposta gerada pela LLM.
    """
    cliente = _cliente_groq()
    mensagens = montar_prompt(
        pergunta, contexto_rag, nivel, estilo, modo
    )

    resposta = cliente.chat.completions.create(
        model=MODELO_GROQ,
        messages=mensagens,
        temperature=0.2,
        max_tokens=800,
    )

    return resposta.choices[0].message.content.strip()
