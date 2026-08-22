"""Define a estratégia de ensino (como apresentar o conteúdo) com base no estilo
de aprendizado do aluno, identificado no diagnóstico."""


# Para cada estilo, a abordagem de ensino recomendada.
# Pode ser ajustada conforme a metodologia da pesquisa.
ESTRATEGIAS = {
    "visual": "Priorizar exemplos, diagramas e código comentado.",
    "textual": "Priorizar explicações escritas e detalhadas.",
    "pratico": "Priorizar exercícios e o aprender fazendo.",
}


def definir_estrategia(estilo_aprendizado):
    """Define a estratégia de ensino conforme o estilo.

    Args:
        estilo_aprendizado: o estilo do aluno (visual,
            textual ou pratico).

    Returns:
        str: a abordagem de ensino recomendada. Se o estilo
            não for conhecido, devolve uma abordagem
            equilibrada.
    """
    return ESTRATEGIAS.get(
        estilo_aprendizado,
        "Abordagem equilibrada (texto, exemplos e prática).",
    )
