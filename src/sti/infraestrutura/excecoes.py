"""
Exceções personalizadas do STI.
Permite identificar erros específicos do sistema
com mensagens claras, separando erros do STI dos
erros genéricos do Python/Django.
"""


class AlunoNaoEncontrado(Exception):
    """Aluno não existe no banco de dados."""
    pass


class RespostaNaoGerada(Exception):
    """O orquestrador não conseguiu gerar uma resposta."""
    pass


class RAGSemConteudo(Exception):
    """O RAG não encontrou conteúdo relevante."""
    pass


class LLMIndisponivel(Exception):
    """A API do Groq não está acessível."""
    pass
