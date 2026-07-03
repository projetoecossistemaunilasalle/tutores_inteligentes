"""Faz a primeira avaliação do aluno: calcula a taxa de acerto e define o nível,
gravando no perfil. Usa calcular_taxa_acerto e atualizar_nivel_aluno."""

from sti.modulo_aluno.desempenho.analise_desempenho import (
    calcular_taxa_acerto,
)
from sti.modulo_aluno.desempenho.nivel_proficiencia import (
    atualizar_nivel_aluno,
)


def avaliar_aluno_inicial(perfil, resultados):
    """Faz a avaliação inicial do aluno.

    Args:
        perfil: o PerfilAluno a ser avaliado.
        resultados: lista de booleanos (True = acertou) da
            atividade inicial.

    Returns:
        str: o nível definido para o aluno.
    """
    # 1) calcula quanto o aluno acertou na atividade inicial
    taxa = calcular_taxa_acerto(resultados)

    # 2) converte a taxa em nível e grava no perfil do aluno
    nivel = atualizar_nivel_aluno(perfil, taxa)

    return nivel