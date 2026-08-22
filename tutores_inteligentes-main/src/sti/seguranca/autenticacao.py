"""
Funções auxiliares de autenticação do STI.
Usa o sistema de autenticação nativo do Django —
sem reinventar o que já existe.

Responsabilidade: verificar se o aluno está autenticado
antes de acessar o tutor.
"""

from django.contrib.auth import authenticate, login, logout


def autenticar_aluno(request, username, password):
    """Autentica o aluno e inicia a sessão.

    Args:
        request: requisição HTTP do Django.
        username: nome de usuário.
        password: senha.

    Returns:
        bool: True se autenticado, False se falhou.
    """
    usuario = authenticate(
        request, username=username, password=password
    )
    if usuario is not None:
        login(request, usuario)
        return True
    return False


def encerrar_sessao(request):
    """Encerra a sessão do aluno autenticado.

    Args:
        request: requisição HTTP do Django.
    """
    logout(request)


def esta_autenticado(request):
    """Verifica se há um aluno autenticado na sessão.

    Args:
        request: requisição HTTP do Django.

    Returns:
        bool: True se autenticado, False caso contrário.
    """
    return request.user.is_authenticated
