"""Tenta responder a pergunta do aluno via repositório Q&A e regras por palavra-chave,
antes de acionar a LLM (Groq) — cada resposta aqui é custo zero de API."""

from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA


def buscar_no_repositorio(pergunta):
    """Busca no Q&A uma resposta já validada pelo professor.

    Compara a pergunta com as palavras-chave cadastradas.
    Retorna a primeira resposta encontrada, ou None.

    Args:
        pergunta: texto digitado pelo aluno.

    Returns:
        str: resposta do repositório, ou None se não achou.
    """
    pergunta_lower = pergunta.lower()

    # Busca nos registros ativos do repositório.
    registros = RepositorioQA.objects.filter(ativo=True)

    for registro in registros:
        palavras = registro.palavras_chave.lower().split(",")
        # Se qualquer palavra-chave estiver na pergunta,
        # considera uma correspondência.
        if any(p.strip() in pergunta_lower for p in palavras):
            return registro.resposta

    return None


def aplicar_regras(pergunta, nivel_aluno):
    """Aplica regras simples baseadas no nível do aluno.

    Regras básicas de fallback para casos comuns.
    Retorna uma resposta ou None se nenhuma regra se aplicar.

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
    if pergunta_lower in ["ajuda", "help", "socorro"]:
        return (
            "Pode me contar com mais detalhes o que você "
            "está estudando? Assim consigo te ajudar melhor."
        )

    return None


def processar_com_regras(pergunta, nivel_aluno):
    """Tenta responder usando regras e Q&A.

    É o ponto de entrada da IA Estruturada. O orquestrador
    chama esta função ANTES de acionar o Groq.

    Args:
        pergunta: texto digitado pelo aluno.
        nivel_aluno: nível atual do aluno no perfil.

    Returns:
        str: resposta encontrada, ou None se precisar da LLM.
    """
    # 1) Tenta o repositório Q&A primeiro.
    resposta = buscar_no_repositorio(pergunta)
    if resposta:
        return resposta

    # 2) Tenta as regras simples.
    resposta = aplicar_regras(pergunta, nivel_aluno)
    if resposta:
        return resposta

    # 3) Não encontrou nada — sinaliza para usar a LLM.
    return None
