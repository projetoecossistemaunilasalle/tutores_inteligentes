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

MODELO_EMBEDDINGS = "intfloat/multilingual-e5-small"
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

        # Ignora linhas curtas, MAS preserva titulos em maiusculas
        # (ex.: "ALGORITMO NATURAL:") que sao secoes relevantes.
        eh_titulo = linha.isupper() and len(linha) >= 4
        if len(linha) < 15 and not eh_titulo:
            continue

        # Ignora cabecalhos e rodapes
        linha_lower = linha.lower()
        if any(ignorar in linha_lower for ignorar in LINHAS_IGNORAR):
            continue

        # Ignora linhas com texto duplicado (ex: PPrroocceessssoo)
        if re.search(r'(.)\1{2,}', linha):
            continue

        linhas_limpas.append(linha)

  # 3) Junta as linhas preservando quebras entre elas
    texto_limpo = '\n'.join(linhas_limpas)
    # colapsa espacos horizontais, mas mantem as quebras de linha
    texto_limpo = re.sub(r'[ \t]+', ' ', texto_limpo).strip()

    return texto_limpo


def dividir_em_pedacos(texto, tamanho=700, sobreposicao=1):
    """Divide o texto em pedacos respeitando fronteiras de sentenca.

    Em vez de cortar em um numero fixo de caracteres (o que partia
    palavras e titulos no meio), agrupa sentencas inteiras ate atingir
    ~700 caracteres. Mantem 'sobreposicao' sentencas do fim de um pedaco
    no inicio do proximo, para nao perder contexto entre eles.
    """
    # Quebra em sentencas: por pontuacao final OU por quebra de linha
    # (titulos e itens de lista costumam vir em linha propria).
    bruto = re.split(r'(?<=[.:!?])\s+|\n+', texto)
    sentencas = [s.strip() for s in bruto if s and len(s.strip()) > 1]

    pedacos = []
    atual = []
    tam_atual = 0

    for sent in sentencas:
        atual.append(sent)
        tam_atual += len(sent) + 1

        if tam_atual >= tamanho:
            pedaco = ' '.join(atual).strip()
            if len(pedaco) > 50:
                pedacos.append(pedaco)
            # mantem as ultimas 'sobreposicao' sentencas como contexto
            atual = atual[-sobreposicao:] if sobreposicao > 0 else []
            tam_atual = sum(len(s) + 1 for s in atual)

    # ultimo pedaco que sobrou
    if atual:
        pedaco = ' '.join(atual).strip()
        if len(pedaco) > 50:
            pedacos.append(pedaco)

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
    colecao = cliente.create_collection(
        "conteudo",
        metadata={"hnsw:space": "cosine"},
    )

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

        pedacos_prefixados = [f"passage: {p}" for p in pedacos]
        vetores = modelo.encode(pedacos_prefixados).tolist()
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


def reindexar_material(pasta=PASTA_PDFS):
    """Reindexa o material de forma SEGURA, para ser chamada pela interface.

    Diferente de indexar_pdfs(), esta funcao protege a colecao atual:
    indexa primeiro numa colecao temporaria e so substitui a colecao
    'conteudo' se a indexacao terminar com sucesso e gerar conteudo.
    Assim, se um PDF estiver corrompido ou vazio, o RAG atual continua
    funcionando em vez de ficar quebrado.

    Returns:
        dict com:
            ok (bool): True se reindexou com sucesso.
            total (int): quantidade de pedacos indexados.
            arquivos (int): quantos PDFs foram processados.
            mensagem (str): texto para mostrar ao professor/admin.
    """
    try:
        arquivos = [
            f for f in os.listdir(pasta)
            if f.lower().endswith(".pdf")
        ]
    except FileNotFoundError:
        return {
            "ok": False, "total": 0, "arquivos": 0,
            "mensagem": "Pasta de materiais nao encontrada.",
        }

    if not arquivos:
        return {
            "ok": False, "total": 0, "arquivos": 0,
            "mensagem": "Nenhum PDF encontrado na pasta de materiais.",
        }

    try:
        modelo = SentenceTransformer(MODELO_EMBEDDINGS)
        os.makedirs(PASTA_VETORES, exist_ok=True)
        cliente = chromadb.PersistentClient(path=PASTA_VETORES)

        # 1) Indexa numa colecao TEMPORARIA (nao mexe na atual ainda)
        nome_temp = "conteudo_temp"
        try:
            cliente.delete_collection(nome_temp)
        except Exception:
            pass
        colecao_temp = cliente.create_collection(
            nome_temp,
            metadata={"hnsw:space": "cosine"},
        )

        total = 0
        arquivos_ok = 0
        for arquivo in arquivos:
            caminho = os.path.join(pasta, arquivo)
            texto_completo = ""
            try:
                with pdfplumber.open(caminho) as pdf:
                    for pagina in pdf.pages:
                        texto_pagina = pagina.extract_text() or ""
                        texto_limpo = limpar_texto(texto_pagina)
                        if texto_limpo:
                            texto_completo += " " + texto_limpo
            except Exception:
                # PDF corrompido ou ilegivel: pula, mas registra
                continue

            if not texto_completo.strip():
                continue

            pedacos = dividir_em_pedacos(texto_completo)
            if not pedacos:
                continue

            pedacos_prefixados = [f"passage: {p}" for p in pedacos]
            vetores = modelo.encode(pedacos_prefixados).tolist()
            ids = [f"{arquivo}-{i}" for i in range(len(pedacos))]
            colecao_temp.add(
                documents=pedacos, embeddings=vetores, ids=ids,
            )
            total += len(pedacos)
            arquivos_ok += 1

        # 2) Se a indexacao nao gerou nada, ABORTA sem tocar na atual
        if total == 0:
            try:
                cliente.delete_collection(nome_temp)
            except Exception:
                pass
            return {
                "ok": False, "total": 0, "arquivos": len(arquivos),
                "mensagem": (
                    "Nenhum conteudo pode ser extraido dos PDFs. "
                    "Material nao indexado (possivel arquivo corrompido "
                    "ou sem texto). O material anterior foi mantido."
                ),
            }

        # 3) Sucesso: substitui a colecao 'conteudo' pela nova
        try:
            cliente.delete_collection("conteudo")
        except Exception:
            pass
        # renomeia a temporaria para o nome oficial
        colecao_temp.modify(name="conteudo")

        return {
            "ok": True, "total": total, "arquivos": arquivos_ok,
            "mensagem": (
                f"Reindexacao concluida: {arquivos_ok} arquivo(s), "
                f"{total} trechos indexados."
            ),
        }

    except Exception as e:
        return {
            "ok": False, "total": 0, "arquivos": 0,
            "mensagem": f"Falha na reindexacao: {e}",
        }
