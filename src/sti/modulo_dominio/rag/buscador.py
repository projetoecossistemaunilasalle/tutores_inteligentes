"""Busca no banco de vetores os trechos mais relevantes para a pergunta do aluno
(o "R" do RAG). Usa o mesmo modelo e pasta de vetores do indexador_pdf.py."""

import chromadb
from sentence_transformers import SentenceTransformer

# Precisam bater com o indexador_pdf.py.
MODELO_EMBEDDINGS = "all-MiniLM-L6-v2"
PASTA_VETORES = "data/processed/vetores"


def buscar(pergunta, quantidade=3):
    """Busca os trechos mais relevantes para a pergunta.

    Retorna uma lista com os pedaços de texto encontrados.
    'quantidade' = quantos trechos trazer (padrão 3).
    """
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    cliente = chromadb.PersistentClient(path=PASTA_VETORES)
    colecao = cliente.get_or_create_collection("conteudo")

    # Transforma a pergunta em vetor (mesma técnica do índice).
    vetor_pergunta = modelo.encode([pergunta]).tolist()

    # Procura os trechos mais parecidos com a pergunta.
    resultado = colecao.query(
        query_embeddings=vetor_pergunta,
        n_results=quantidade,
    )

    # 'documents' vem como lista de listas; pegamos a primeira.
    return resultado.get("documents", [[]])[0]


def montar_contexto(trechos):
    """Junta os trechos num único texto.

    Esse texto será entregue ao Motor de IA como o "contexto"
    em que ele deve se basear para responder.
    """
    return "\n\n".join(trechos)