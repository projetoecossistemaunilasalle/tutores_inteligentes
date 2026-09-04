"""
Logica de busca semantica do RAG, com expansao de consulta.

Modelo: intfloat/multilingual-e5-small (o MESMO do indexador).

Melhorias:
  1. Expansao por palavras-chave (atende material em topicos/slides).
  2. Dicionario de sinonimos do dominio: termos ambiguos como "para"
     e "se" sao traduzidos para os termos tecnicos da apostila.
  3. Verificacao de relevancia por CONTEUDO: apos buscar, confere se
     os trechos realmente tratam do assunto perguntado (pela palavra-
     chave da pergunta OU por um sinonimo de dominio). Isso informa ao
     orquestrador se ha material relevante ou se deve acionar o
     conhecimento geral do modelo (Opcao 2).
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
    "e", "o", "que", "eh",
}

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
    "output": "saida exibir resultado tela console",
    "input": "entrada leitura digitado teclado",
}


def _traduzir_dominio(pergunta_lower):
    """Se a pergunta menciona um termo ambiguo do dominio, devolve
    a expansao tecnica correspondente. Senao, devolve vazio."""
    for termo in sorted(SINONIMOS_DOMINIO, key=len, reverse=True):
        if re.search(rf"\b{re.escape(termo)}\b", pergunta_lower):
            return SINONIMOS_DOMINIO[termo]
    return ""


def extrair_palavras_chave(pergunta):
    """Extrai palavras significativas, sem as vazias."""
    palavras = re.findall(r"\w+", pergunta.lower())
    chaves = [p for p in palavras if p not in STOPWORDS and len(p) > 2]
    return " ".join(chaves) if chaves else pergunta


def _tem_conteudo_relevante(pergunta, trechos):
    """Verifica se os trechos realmente tratam do assunto perguntado.

    Combinada: um trecho e relevante se contem alguma palavra-chave
    da pergunta OU algum termo da expansao de dominio correspondente.
    """
    if not trechos:
        return False

    pergunta_lower = pergunta.lower()

    # termos a procurar: palavras-chave da pergunta + expansao de dominio
    termos_busca = set()
    for palavra in extrair_palavras_chave(pergunta).split():
        if len(palavra) > 2:
            termos_busca.add(palavra)

    traducao = _traduzir_dominio(pergunta_lower)
    if traducao:
        for palavra in traducao.split():
            if len(palavra) > 2:
                termos_busca.add(palavra)

    if not termos_busca:
        return False

    # relevante se ALGUM trecho contem ALGUM dos termos
    corpo = " ".join(trechos).lower()
    for termo in termos_busca:
        if termo in corpo:
            return True
    return False


def buscar(pergunta, quantidade=3):
    """Busca trechos relevantes. Retorna apenas a lista (compat.)."""
    trechos, _ = buscar_com_relevancia(pergunta, quantidade)
    return trechos


def buscar_com_relevancia(pergunta, quantidade=3):
    """Busca trechos e informa se ha material realmente relevante.

    Returns:
        (trechos, tem_relevante):
            trechos (list[str]): os trechos encontrados.
            tem_relevante (bool): True se os trechos tratam do assunto.
    """
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
    resultado = colecao.query(
        query_embeddings=vetores,
        n_results=quantidade,
    )

    vistos = set()
    combinados = []
    for lista in resultado.get("documents", []):
        for doc in lista:
            if doc not in vistos:
                vistos.add(doc)
                combinados.append(doc)

    trechos = combinados[: quantidade * 2]
    tem_relevante = _tem_conteudo_relevante(pergunta, trechos)

    return trechos, tem_relevante


def montar_contexto(trechos):
    """Reune os trechos num unico texto para o Groq usar."""
    return "\n\n".join(trechos)
