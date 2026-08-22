# src/sti/pedagogico/__init__.py
"""Camada de decisão do tutor. Ponto de entrada: tutor_service.
Expõe: iniciar_sessao, atualizar_sessao, obter_plano."""

from .tutor_service import (
    iniciar_sessao,
    atualizar_sessao,
    obter_plano,
)
