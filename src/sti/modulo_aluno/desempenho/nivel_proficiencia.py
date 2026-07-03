"""Converte a taxa de desempenho (0-100) no nível de proficiência do aluno e grava no perfil.
Recebe a taxa já calculada por analise_desempenho.py; usado no diagnóstico inicial
e no acompanhamento contínuo."""

from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno


# Faixas que definem o nível. São valores de REFERÊNCIA e podem ser ajustados
# conforme a metodologia da pesquisa.
LIMITE_INICIANTE = 40       # abaixo de 40% de acerto  -> iniciante
LIMITE_INTERMEDIARIO = 75   # de 40% até 75%           -> intermediário
#                             acima de 75%             -> avançado


def determinar_nivel(taxa_acerto: float) -> str:
    """Converte uma taxa de acerto (0 a 100) no nível correspondente.

    Args:
        taxa_acerto: percentual de acertos do aluno, de 0 a 100.

    Returns:
        str: "iniciante", "intermediario" ou "avancado"
             (os mesmos códigos usados em PerfilAluno.NIVEL_CHOICES).
    """
    if taxa_acerto < LIMITE_INICIANTE:
        return "iniciante"
    elif taxa_acerto <= LIMITE_INTERMEDIARIO:
        return "intermediario"
    else:
        return "avancado"


def atualizar_nivel_aluno(perfil: PerfilAluno, taxa_acerto: float) -> str:
    """Calcula o nível a partir da taxa e GRAVA no perfil do aluno.

    Args:
        perfil: o objeto PerfilAluno a ser atualizado.
        taxa_acerto: percentual de acertos do aluno (0 a 100).

    Returns:
        str: o novo nível que foi gravado no perfil.
    """
    novo_nivel = determinar_nivel(taxa_acerto)

    # Grava o resultado no perfil e persiste no banco de dados.
    perfil.nivel_proficiencia = novo_nivel
    perfil.save()  # atualiza a linha do aluno na tabela

    return novo_nivel
