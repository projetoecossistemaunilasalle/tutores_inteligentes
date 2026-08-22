# src/sti/seguranca/__init__.py
"""Segurança: autenticação e controle de acesso do STI."""

from .autenticacao import autenticar_aluno, encerrar_sessao, esta_autenticado
from .permissoes import apenas_aluno, apenas_professor
