"""Motor de Decisão: recebe a intenção (LLM), aciona RAG + regras + perfil do
aluno e monta a resposta final. responder() é a única fronteira que a Interface
deve chamar — mantenha a assinatura estável."""

def responder(pergunta_aluno: str, aluno_id: str) -> dict:
    """Retorna a resposta final do tutor para a Interface (Grupo 2).

    Returns:
        dict: {"resposta": str, "fontes": list, "aluno_id": str}
    """
    raise NotImplementedError("TODO: implementar orquestracao do Grupo 1")
