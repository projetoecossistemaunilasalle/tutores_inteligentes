"""
Logica de indexacao do RAG com limpeza de texto.
Le os PDFs, limpa o texto extraido e indexa no ChromaDB.

Melhorias desta versao:
  - Remove caracteres (cid:xxx) gerados por PDFs com fontes especiais
  - Remove linhas de cabecalho/rodape repetitivas
  - Remove linhas muito curtas (menos de 30 caracteres)
  - Remove espacos e quebras de linha excessivas
"""

import os
import re
import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb

MODELO_EMBEDDINGS = "paraphrase-MiniLM-L3-v2"
PASTA_PDFS = "data/raw"
PASTA_VETORES = "data/processed/vetores"

# Linhas de cabecalho/rodape para ignorar
LINHAS_IGNORAR = [
    "ufu", "universidade federal", "faculdade de computacao",
    "prof.", "pag.:", "prof. luiz", "introducao a algoritmos",
]


def limpar_texto(texto):
    """Limpa o texto extraido do PDF.

    Remove:
    - Caracteres (cid:xxx) de fontes especiais
    - Linhas de cabecalho e rodape
    - Linhas muito curtas
    - Espacos e quebras excessivas
    """
    if not texto:
        return ""

    # 1) Remove (cid:xxx)
    texto = re.sub(r'\(cid:\d+\)', '', texto)

    # 2) Processa linha por linha
    linhas_limpas = []
    for linha in texto.split('\n'):
        linha = linha.strip()

        # Ignora linhas muito curtas
        if len(linha) < 15:
            continue

        # Ignora cabecalhos e rodapes
        linha_lower = linha.lower()
        if any(ignorar in linha_lower for ignorar in LINHAS_IGNORAR):
            continue

        # Ignora linhas com texto duplicado (ex: PPrroocceessssoo)
        if re.search(r'(.)\1{2,}', linha):
            continue

        linhas_limpas.append(linha)

    # 3) Junta as linhas e remove espacos excessivos
    texto_limpo = ' '.join(linhas_limpas)
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()

    return texto_limpo


def dividir_em_pedacos(texto, tamanho=600, sobreposicao=80):
    """Divide o texto em pedacos menores com sobreposicao.

    Tamanho menor (600) para pedacos mais precisos.
    Sobreposicao maior (80) para nao perder contexto.
    """
    pedacos = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        pedaco = texto[inicio:fim].strip()
        if len(pedaco) > 50:  # ignora pedacos muito pequenos
            pedacos.append(pedaco)
        inicio = fim - sobreposicao
    return pedacos


def indexar_pdfs(pasta=PASTA_PDFS):
    """Le, limpa e indexa os PDFs no ChromaDB."""
    print(f"Carregando modelo {MODELO_EMBEDDINGS}...")
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    print("Modelo carregado!")

    os.makedirs(PASTA_VETORES, exist_ok=True)

    # Recria a colecao para reindexar do zero
    cliente = chromadb.PersistentClient(path=PASTA_VETORES)
    try:
        cliente.delete_collection("conteudo")
        print("Colecao anterior removida.")
    except Exception:
        pass
    colecao = cliente.create_collection("conteudo")

    total = 0
    arquivos = [
        f for f in os.listdir(pasta)
        if f.lower().endswith(".pdf")
    ]

    if not arquivos:
        print("Nenhum PDF encontrado em", pasta)
        return 0

    for arquivo in arquivos:
        print(f"\nIndexando: {arquivo}...")
        caminho = os.path.join(pasta, arquivo)

        texto_completo = ""
        with pdfplumber.open(caminho) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_pagina = pagina.extract_text() or ""
                texto_limpo = limpar_texto(texto_pagina)
                if texto_limpo:
                    texto_completo += " " + texto_limpo

        if not texto_completo.strip():
            print(f"  Aviso: {arquivo} sem texto extraivel")
            continue

        pedacos = dividir_em_pedacos(texto_completo)
        print(f"  {len(pedacos)} pedacos gerados apos limpeza")

        vetores = modelo.encode(pedacos).tolist()
        ids = [f"{arquivo}-{i}" for i in range(len(pedacos))]

        colecao.add(
            documents=pedacos,
            embeddings=vetores,
            ids=ids,
        )
        total += len(pedacos)
        print(f"  {arquivo} indexado com sucesso!")

    print(f"\nTotal indexado: {total} pedacos")
    return total
