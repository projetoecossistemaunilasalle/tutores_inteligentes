"""
Logica de busca semantica do RAG, com expansao de consulta.

Modelo: intfloat/multilingual-e5-small (o MESMO do indexador).

Duas melhorias sobre a busca simples:
  1. Expansao por palavras-chave (atende material em topicos/slides).
  2. Dicionario de sinonimos do dominio: termos ambiguos como "para"
     e "se" (que sao comando E palavra comum) sao traduzidos para os
     termos tecnicos inequivocos usados na apostila.
"""

import re
import chromadb
from sentence_transformers import SentenceTransformer

MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
PASTA_VETORES = "data/processed/vetores"

STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "de", "do", "da", "dos", "das",
    "que", "para", "por", "com", "em", "no", "na", "nos", "nas",
    "qual", "quais", "como", "quando", "onde", "porque", "sao",
    "serve", "significa", "funciona", "explique", "defina",
    "me", "diga", "fale", "sobre", "isso", "isto", "seu", "sua",
}

# Traducao de termos ambiguos ou coloquiais para os termos tecnicos
# inequivocos que aparecem na apostila. A chave dispara a expansao.
SINONIMOS_DOMINIO = {
    "para": "estrutura de repeticao for laco controlado por contagem",
    "comando para": "estrutura de repeticao for laco controlado por contagem",
    "laco para": "estrutura de repeticao for contagem",
    "enquanto": "estrutura de repeticao while condicao",
    "comando enquanto": "estrutura de repeticao while condicao",
    "se": "estrutura condicional selecao if",
    "comando se": "estrutura condicional selecao if",
    "senao": "estrutura condicional else",
    "repita": "estrutura de repeticao laco",
}


def _traduzir_dominio(pergunta_lower):
    """Se a pergunta menciona um termo ambiguo do dominio, devolve
    a expansao tecnica correspondente. Senao, devolve vazio."""
    # tenta primeiro as chaves compostas (mais especificas)
    for termo in sorted(SINONIMOS_DOMINIO, key=len, reverse=True):
        if re.search(rf"\b{re.escape(termo)}\b", pergunta_lower):
            return SINONIMOS_DOMINIO[termo]
    return ""


def extrair_palavras_chave(pergunta):
    """Extrai palavras significativas, sem as vazias."""
    palavras = re.findall(r"\w+", pergunta.lower())
    chaves = [p for p in palavras if p not in STOPWORDS and len(p) > 2]
    return " ".join(chaves) if chaves else pergunta


def buscar(pergunta, quantidade=3):
    """Busca trechos relevantes combinando ate tres consultas:
    a pergunta original, as palavras-chave, e a expansao do dominio."""
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    cliente = chromadb.PersistentClient(path=PASTA_VETORES)
    colecao = cliente.get_or_create_collection("conteudo")

    pergunta_lower = pergunta.lower()
    consultas = [f"query: {pergunta}"]

    chaves = extrair_palavras_chave(pergunta)
    if chaves.lower() != pergunta_lower:
        consultas.append(f"query: {chaves}")

    traducao = _traduzir_dominio(pergunta_lower)
    if traducao:
        consultas.append(f"query: {traducao}")

    vetores = modelo.encode(consultas).tolist()
    resultado = colecao.query(query_embeddings=vetores, n_results=quantidade)

    vistos = set()
    combinados = []
    for lista in resultado.get("documents", []):
        for doc in lista:
            if doc not in vistos:
                vistos.add(doc)
                combinados.append(doc)

    return combinados[: quantidade * 2]


def montar_contexto(trechos):
    """Reune os trechos num unico texto para o Groq usar."""
    return "\n\n".join(trechos)
