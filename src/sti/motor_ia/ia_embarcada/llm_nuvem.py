"""
Cliente do Groq com prompt restritivo ao material do professor.
O Groq deve responder APENAS com base no contexto do RAG,
sem acrescentar conhecimento proprio.
"""

import os
from groq import Groq

MODELO_GROQ = "openai/gpt-oss-20b"


def _cliente_groq():
    """Cria o cliente da Groq usando a chave do .env."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def montar_prompt(pergunta, contexto_rag, nivel, estilo):
    """Monta o prompt restritivo ao material do professor."""

    if contexto_rag.strip():
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
        # Sem contexto do RAG — informa ao aluno
        instrucao = (
            f"Voce e um tutor de Algoritmos e Programacao. "
            f"O aluno esta no nivel {nivel}. "
            f"Nao ha material especifico disponivel sobre este "
            f"assunto ainda. Informe ao aluno que o professor "
            f"ainda nao cadastrou material sobre este topico e "
            f"sugira que ele consulte o professor diretamente."
        )

    return [
        {"role": "system", "content": instrucao},
        {"role": "user", "content": pergunta},
    ]


def gerar_resposta(pergunta, contexto_rag, nivel, estilo):
    """Chama o Groq e devolve a resposta baseada no material.

    Args:
        pergunta: texto digitado pelo aluno.
        contexto_rag: trechos encontrados pelo RAG.
        nivel: nivel de proficiencia do aluno.
        estilo: estilo de aprendizado do aluno.

    Returns:
        str: resposta gerada pela LLM.
    """
    cliente = _cliente_groq()
    mensagens = montar_prompt(
        pergunta, contexto_rag, nivel, estilo
    )

    resposta = cliente.chat.completions.create(
        model=MODELO_GROQ,
        messages=mensagens,
        temperature=0.2,  # mais baixo = mais fiel ao material
        max_tokens=800,
    )

    return resposta.choices[0].message.content.strip()
