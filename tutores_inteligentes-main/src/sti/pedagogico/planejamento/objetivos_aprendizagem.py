"""Define quais tópicos o aluno deve alcançar nesta etapa, com base no nível
atual e no conteúdo disponível no domínio."""


def definir_objetivos(nivel_aluno, conteudos):
    """Define os objetivos de aprendizagem do aluno.

    Seleciona os tópicos adequados ao nível atual do aluno —
    o que ele deve dominar nesta etapa.

    Args:
        nivel_aluno: nível do aluno (iniciante, intermediario
            ou avancado).
        conteudos: lista de tópicos do domínio
            (ConteudoAlgoritmos), cada um com .titulo, .nivel
            e .ativo.

    Returns:
        list: títulos dos tópicos que são objetivos.
    """
    objetivos = [
        c.titulo
        for c in conteudos
        if c.ativo and c.nivel == nivel_aluno
    ]
    return objetivos
