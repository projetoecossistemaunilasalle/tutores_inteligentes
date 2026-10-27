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

import unicodedata
import json
import os
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


# ══════════════════════════════════════════════════════════════════════
# EXERCICIOS DE FIXACAO — busca no banco de questoes (colecao "exercicios")
# Nao altera nada da busca do conteudo acima.
# ══════════════════════════════════════════════════════════════════════

COLECAO_EXERCICIOS = "exercicios"
ARQUIVO_CONFIG_EXERCICIOS = os.path.join("data", "exercicios", "config.json")
QTD_PADRAO, QTD_MIN, QTD_MAX = 2, 1, 5
_modelo_exercicios = None


def ler_quantidade_exercicios():
    """Quantas questoes oferecer por duvida (definido pelo professor).
    Sem configuracao salva, usa o padrao (2). Sempre entre 1 e 5."""
    try:
        with open(ARQUIVO_CONFIG_EXERCICIOS, encoding="utf-8") as f:
            n = int(json.load(f).get("quantidade", QTD_PADRAO))
    except Exception:
        n = QTD_PADRAO
    return max(QTD_MIN, min(QTD_MAX, n))


def salvar_quantidade_exercicios(n):
    """Salva a quantidade escolhida pelo professor (limitada a 1..5)."""
    try:
        n = int(n)
    except (TypeError, ValueError):
        n = QTD_PADRAO
    n = max(QTD_MIN, min(QTD_MAX, n))
    os.makedirs(os.path.dirname(ARQUIVO_CONFIG_EXERCICIOS), exist_ok=True)
    with open(ARQUIVO_CONFIG_EXERCICIOS, "w", encoding="utf-8") as f:
        json.dump({"quantidade": n}, f)
    return n


def _carregar_modelo_exercicios():
    """Carrega o modelo de embeddings uma unica vez."""
    global _modelo_exercicios
    if _modelo_exercicios is None:
        _modelo_exercicios = SentenceTransformer(MODELO_EMBEDDINGS)
    return _modelo_exercicios


# Inicios de pergunta que indicam duvida introdutoria (sem acento, minusculas)
PADRAO_INTRODUTORIA = re.compile(
    r"^\s*(o que (e|sao|significa)|para que serve|defina|definicao|conceito|"
    r"qual (e )?o (significado|conceito)|explique o que)\b"
)


def _sem_acento(texto):
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _duvida_introdutoria(pergunta):
    """True se a pergunta e conceitual/introdutoria (ex.: 'o que e variavel?')."""
    return bool(PADRAO_INTRODUTORIA.search(_sem_acento(pergunta)))


def _numero_prova(arquivo):
    """Nivel da prova pelo nome do arquivo (G1 -> 1, G2 -> 2...).
    'Recuperacao de G1' conta como nivel 1. Sem numero, vai para o fim (99)."""
    nome = _sem_acento(arquivo)
    m = re.search(r"recuperacao de g\s*_?(\d)",
                  nome) or re.search(r"g\s*_?(\d)", nome)
    return int(m.group(1)) if m else 99


def _relevante_exercicio(pergunta, texto):
    """A questao trata do assunto da pergunta? Compara pela raiz da palavra,
    sem acentos (ex.: 'variavel' encontra 'variaveis')."""
    corpo = _sem_acento(texto)
    termos = [p for p in _sem_acento(
        extrair_palavras_chave(pergunta)).split() if len(p) > 2]
    traducao = _traduzir_dominio(pergunta.lower())
    termos += [p for p in _sem_acento(traducao).split() if len(p) > 2]
    for t in termos:
        raiz = t[:max(4, len(t) - 2)] if len(t) > 5 else t
        if raiz in corpo:
            return True
    return False


def buscar_exercicios(pergunta, quantidade=None):
    """Busca no banco de questoes as questoes ligadas a duvida do aluno.

    quantidade: maximo de questoes. Se nao for informada, usa a
    quantidade configurada pelo professor (ler_quantidade_exercicios).

    O GABARITO NAO e devolvido aqui (fica no servidor, para a correcao).

    Returns:
        list[dict]: [{"id", "numero", "texto", "arquivo"}]. Vazia se nao
        houver questao sobre o assunto ou se nenhuma prova foi enviada.
    """
    if quantidade is None:
        quantidade = ler_quantidade_exercicios()

    try:
        cliente = chromadb.PersistentClient(path=PASTA_VETORES)
        colecao = cliente.get_collection(COLECAO_EXERCICIOS)
    except Exception:
        return []

    total = colecao.count()
    if total == 0:
        return []

    pergunta_lower = pergunta.lower()
    consultas = [f"query: {pergunta}"]
    chaves = extrair_palavras_chave(pergunta)
    if chaves.lower() != pergunta_lower:
        consultas.append(f"query: {chaves}")
    traducao = _traduzir_dominio(pergunta_lower)
    if traducao:
        consultas.append(f"query: {traducao}")

    vetores = _carregar_modelo_exercicios().encode(consultas).tolist()
    resultado = colecao.query(
        query_embeddings=vetores,
        n_results=min(max(10, quantidade * 4), total),
        include=["documents", "metadatas", "distances"],
    )

    candidatos = {}
    for ids, docs, metas, dists in zip(
        resultado["ids"], resultado["documents"],
        resultado["metadatas"], resultado["distances"],
    ):
        for id_, doc, meta, dist in zip(ids, docs, metas, dists):
            if id_ not in candidatos or dist < candidatos[id_]["dist"]:
                meta = meta or {}
                candidatos[id_] = {
                    "id": id_,
                    "numero": meta.get("numero", 0),
                    "texto": doc,
                    "arquivo": meta.get("arquivo", ""),
                    "dist": dist,
                }

    ordenados = sorted(candidatos.values(), key=lambda c: c["dist"])
    relevantes = [c for c in ordenados if _relevante_exercicio(
        pergunta, c["texto"])]

    # Duvida introdutoria: entre as 8 mais parecidas, preferir as provas
    # de nivel inicial (G1 e sua recuperacao antes da G2).
    if _duvida_introdutoria(pergunta):
        topo = sorted(relevantes[:8], key=lambda c: (
            _numero_prova(c["arquivo"]), c["dist"]))
        relevantes = topo + relevantes[8:]

    return [
        {"id": c["id"], "numero": c["numero"],
         "texto": c["texto"], "arquivo": c["arquivo"]}
        for c in relevantes[:quantidade]
    ]
