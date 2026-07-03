"""Prepara o material do professor para busca: lê PDFs, quebra em chunks, gera
embeddings e grava no banco de vetores (ChromaDB), para o buscador.py usar."""

import os

import pdfplumber
from sentence_transformers import SentenceTransformer
import chromadb

# Modelo que transforma texto em vetores. Pequeno e gratuito.
MODELO_EMBEDDINGS = "all-MiniLM-L6-v2"

# Pasta com os PDFs originais do professor.
PASTA_PDFS = "data/raw"

# Pasta onde o banco de vetores será gravado.
PASTA_VETORES = "data/processed/vetores"


def ler_pdf(caminho):
    """Lê um PDF e devolve todo o texto dele."""
    texto = ""
    with pdfplumber.open(caminho) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
    return texto


def dividir_em_pedacos(texto, tamanho=500, sobreposicao=50):
    """Quebra um texto longo em pedaços menores.

    'sobreposicao' repete um trecho entre os pedaços para
    não perder o contexto na fronteira.
    """
    pedacos = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + tamanho
        pedacos.append(texto[inicio:fim])
        inicio = fim - sobreposicao
    return pedacos


def indexar_pdfs(pasta=PASTA_PDFS):
    """Lê os PDFs da pasta e grava os vetores no ChromaDB.

    Retorna a quantidade de pedaços indexados.
    """
    modelo = SentenceTransformer(MODELO_EMBEDDINGS)
    cliente = chromadb.PersistentClient(path=PASTA_VETORES)
    colecao = cliente.get_or_create_collection("conteudo")

    total = 0
    for arquivo in os.listdir(pasta):
        # Ignora o que não for PDF.
        if not arquivo.lower().endswith(".pdf"):
            continue

        caminho = os.path.join(pasta, arquivo)
        texto = ler_pdf(caminho)
        pedacos = dividir_em_pedacos(texto)

        # Gera os vetores e guarda cada pedaço no banco.
        vetores = modelo.encode(pedacos).tolist()
        ids = [f"{arquivo}-{i}" for i in range(len(pedacos))]
        colecao.add(
            documents=pedacos,
            embeddings=vetores,
            ids=ids,
        )
        total += len(pedacos)

    return total