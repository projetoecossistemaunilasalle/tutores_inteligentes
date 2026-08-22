"""Monta a trilha de estudos: a sequência ordenada de tópicos que o aluno vai
percorrer, seguindo a ordem e os pré-requisitos da base de conhecimento."""


def montar_trilha(conteudos, nivel=None):
    """Monta a trilha de estudos ordenada.

    Args:
        conteudos: lista de tópicos do domínio
            (ConteudoAlgoritmos), cada um com .titulo, .nivel,
            .ordem e .ativo.
        nivel: se informado, traz só os tópicos desse nível;
            se None, traz todos.

    Returns:
        list: títulos dos tópicos, na ordem de estudo.
    """
    # Seleciona os tópicos ativos (e do nível pedido, se houver).
    selecionados = [
        c for c in conteudos
        if c.ativo and (nivel is None or c.nivel == nivel)
    ]

    # Ordena pela sequência definida na base de conhecimento.
    ordenados = sorted(selecionados, key=lambda c: c.ordem)

    return [c.titulo for c in ordenados]
