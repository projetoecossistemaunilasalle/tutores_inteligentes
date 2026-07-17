"""
IA Estruturada: responde com regras e Q&A, sem custo de API.
Usa busca por similaridade (difflib) para reconhecer variações
de palavras-chave sem precisar de correspondência exata.

Ordem de tentativa:
  1. Repositório Q&A (palavras-chave + similaridade)
  2. Regras fixas (saudações, pedidos genéricos)
  3. None -> passa para o RAG + Groq
"""

from difflib import SequenceMatcher
from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA

# Limiar de similaridade: 0.0 a 1.0
# 0.6 = 60% de similaridade — equilibra precisão e flexibilidade
LIMIAR_SIMILARIDADE = 0.6


def _similaridade(texto1, texto2):
    """Calcula a similaridade entre dois textos (0.0 a 1.0)."""
    return SequenceMatcher(
        None,
        texto1.lower(),
        texto2.lower(),
    ).ratio()


def _palavra_encontrada(palavra, pergunta):
    """Verifica se uma palavra está na pergunta por correspondência
    exata ou por similaridade acima do limiar definido."""
    pergunta_lower = pergunta.lower()
    palavra_lower = palavra.lower().strip()

    # 1) Correspondência exata
    if palavra_lower in pergunta_lower:
        return True

    # 2) Similaridade por token (palavra por palavra da pergunta)
    for token in pergunta_lower.split():
        if _similaridade(palavra_lower, token) >= LIMIAR_SIMILARIDADE:
            return True

    return False


def buscar_no_repositorio(pergunta):
    """Busca no Q&A uma resposta validada pelo professor.

    Usa correspondência exata e similaridade para reconhecer
    variações das palavras-chave cadastradas.

    Args:
        pergunta: texto digitado pelo aluno.

    Returns:
        str: resposta encontrada, ou None.
    """
    registros = RepositorioQA.objects.filter(ativo=True)

    for registro in registros:
        palavras = registro.palavras_chave.lower().split(",")
        if any(_palavra_encontrada(p, pergunta) for p in palavras):
            return registro.resposta

    return None


def aplicar_regras(pergunta, nivel_aluno):
    """Aplica regras fixas para casos comuns.

    Args:
        pergunta: texto digitado pelo aluno.
        nivel_aluno: nível atual do aluno no perfil.

    Returns:
        str: resposta da regra, ou None.
    """
    pergunta_lower = pergunta.lower()

    # Regra: saudação
    saudacoes = ["oi", "olá", "ola", "bom dia",
                 "boa tarde", "boa noite"]
    if any(s in pergunta_lower for s in saudacoes):
        return (
            f"Olá! Sou seu tutor de Algoritmos. "
            f"Você está no nível {nivel_aluno}. "
            f"Como posso te ajudar hoje?"
        )

    # Regra: pedido de ajuda genérico
    if pergunta_lower.strip() in ["ajuda", "help", "socorro"]:
        return (
            "Pode me contar com mais detalhes o que você "
            "está estudando? Assim consigo te ajudar melhor."
        )

    return None


def processar_com_regras(pergunta, nivel_aluno):
    """Ponto de entrada da IA Estruturada.

    Tenta responder usando Q&A e regras antes de acionar o Groq.

    Args:
        pergunta: texto digitado pelo aluno.
        nivel_aluno: nível atual do aluno no perfil.

    Returns:
        str: resposta encontrada, ou None se precisar da LLM.
    """
    # 1) Repositório Q&A com similaridade
    resposta = buscar_no_repositorio(pergunta)
    if resposta:
        return resposta

    # 2) Regras fixas
    resposta = aplicar_regras(pergunta, nivel_aluno)
    if resposta:
        return resposta

    # 3) Não encontrou — passa para RAG + Groq
    return None
