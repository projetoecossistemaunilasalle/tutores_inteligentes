# src/sti/pedagogico/diagnostico/__init__.py
"""Funções de diagnóstico do tutor: avaliação inicial, nivelamento contínuo
e identificação do estilo de aprendizado.
Expõe: avaliar_aluno_inicial, nivelar_aluno, identificar_estilo, registrar_estilo_aprendizado."""

from .avaliacao_inicial import avaliar_aluno_inicial
from .nivelamento import nivelar_aluno
from .perfil_aprendizado import (
    identificar_estilo,
    registrar_estilo_aprendizado,
)
