"""
Controle de permissões do STI.
Define quem pode acessar o quê — aluno, professor e admin
têm níveis de acesso diferentes.

No deploy (Render), estas permissões se integram ao sistema
de autenticação do Django sem alteração.
"""

from functools import wraps
from django.http import JsonResponse


def apenas_aluno(view):
    """Decorator: permite acesso apenas a alunos autenticados.

    Uso:
        @apenas_aluno
        def minha_view(request): ...
    """
    @wraps(view)
    def verificar(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"erro": "Acesso restrito. Faça login."},
                status=401,
            )
        return view(request, *args, **kwargs)
    return verificar


def apenas_professor(view):
    """Decorator: permite acesso apenas a professores (staff).

    Uso:
        @apenas_professor
        def minha_view(request): ...
    """
    @wraps(view)
    def verificar(request, *args, **kwargs):
        if not request.user.is_staff:
            return JsonResponse(
                {"erro": "Acesso restrito a professores."},
                status=403,
            )
        return view(request, *args, **kwargs)
    return verificar
