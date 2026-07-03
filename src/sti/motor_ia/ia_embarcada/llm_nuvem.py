"""Conecta com a API do Groq para gerar a resposta do tutor quando a IA Estruturada
não consegue responder. Recebe pergunta + contexto do RAG + perfil e monta o prompt."""

import os
from groq import Groq

# Modelo recomendado para geração de respostas do tutor.
# Verifique o painel da Groq para confirmar disponibilidade.
MODELO_GROQ = "llama-3.1-8b-instant"


def _cliente_groq():
    """Cria o cliente da Groq usando a chave do .env."""
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def montar_prompt(pergunta, contexto_rag, nivel, estilo):
    """Monta o prompt completo para a LLM.

    Instrui a LLM a se comportar como tutor, considerando
    o nível e o estilo do aluno e o contexto do RAG.

    Args:
        pergunta: texto digitado pelo aluno.
        contexto_rag: trechos do material do professor
            recuperados pelo buscador.py.
        nivel: nível de proficiência do aluno.
        estilo: estilo de aprendizado do aluno.

    Returns:
        list: mensagens no formato esperado pela API Groq.
    """
    instrucao = (
        f"Você é um tutor de Algoritmos e Programação. "
        f"O aluno está no nível {nivel} e aprende melhor "
        f"de forma {estilo}. Responda de forma didática, "
        f"clara e encorajadora. Baseie sua resposta no "
        f"material abaixo e não invente informações.\n\n"
        f"Material de referência:\n{contexto_rag}"
    )

    return [
        {"role": "system", "content": instrucao},
        {"role": "user", "content": pergunta},
    ]


def gerar_resposta(pergunta, contexto_rag, nivel, estilo):
    """Chama o Groq e devolve a resposta do tutor.

    Args:
        pergunta: texto digitado pelo aluno.
        contexto_rag: contexto recuperado pelo RAG.
        nivel: nível de proficiência do aluno.
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
        temperature=0.3,  # baixo = mais consistente
        max_tokens=1000,
    )

    return resposta.choices[0].message.content.strip()
