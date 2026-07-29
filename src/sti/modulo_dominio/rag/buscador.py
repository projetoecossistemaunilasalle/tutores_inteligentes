"""
Logica de busca semantica do RAG.
Busca os trechos mais relevantes para a pergunta
do aluno nos vetores indexados pelo indexador_pdf.

Modelo: paraphrase-MiniLM-L3-v2
  Deve ser o MESMO modelo usado no indexador_pdf.py!
"""

import chromadb
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDINGS = "paraphrase-multilingual-MiniLM-L12-v2"
PASTA_VETORES = "data/processed/vetores"


def buscar(pergunta, quantidade=3):
    """Busca os trechos mais relevantes para a pergunta.

    Args:
        pergunta: texto digitado pelo aluno.
        quantidade: quantos trechos retornar (padrao 3).

    Returns:
        list: trechos mais relevantes encontrados.
    """
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    cliente = chromadb.PersistentClient(path=PASTA_VETORES)
    colecao = cliente.get_or_create_collection("conteudo")

    vetor_pergunta = modelo.encode([pergunta]).tolist()

    resultado = colecao.query(
        query_embeddings=vetor_pergunta,
        n_results=quantidade,
    )

    return resultado.get("documents", [[]])[0]


def montar_contexto(trechos):
    """Reune os trechos num unico texto para o Groq usar.

    Args:
        trechos: lista de trechos retornados pelo buscar().

    Returns:
        str: contexto consolidado.
    """
    return "\n\n".join(trechos)
