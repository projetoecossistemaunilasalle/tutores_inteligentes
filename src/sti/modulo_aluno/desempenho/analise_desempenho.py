"""Calcula o desempenho do aluno: taxa de acerto geral e por tópico.
Recebe resultados prontos (topico, acertou); a taxa geral alimenta o
nivel_proficiencia.py."""


def calcular_taxa_acerto(resultados) -> float:
    """Calcula a taxa de acerto geral (0 a 100).

    Args:
        resultados: iterável de valores booleanos (True = acertou).

    Returns:
        float: percentual de acertos, arredondado a 1 casa. 0.0 se vazio.
    """
    resultados = list(resultados)
    if not resultados:
        return 0.0
    acertos = sum(1 for acertou in resultados if acertou)
    return round((acertos / len(resultados)) * 100, 1)


def analisar_desempenho(resultados_por_topico) -> dict:
    """Analisa o desempenho geral e por tópico.

    Args:
        resultados_por_topico: iterável de tuplas (topico, acertou),
            onde 'acertou' é booleano.

    Returns:
        dict: {
            "taxa_geral": float,          # % de acerto somando tudo
            "por_topico": {str: float},   # % de acerto em cada tópico
            "total": int,                 # quantidade de questões consideradas
        }
    """
    resultados_por_topico = list(resultados_por_topico)

    # 1) Separa os acertos/erros de cada tópico num dicionário.
    #    Ex.: {"lacos": [True, False], "vetores": [True]}
    agrupado = {}
    for topico, acertou in resultados_por_topico:
        agrupado.setdefault(topico, []).append(acertou)

    # 2) Calcula a taxa de acerto de cada tópico reaproveitando a função acima.
    por_topico = {
        topico: calcular_taxa_acerto(acertos)
        for topico, acertos in agrupado.items()
    }

    # 3) Calcula a taxa geral somando todos os resultados.
    todos = [acertou for _, acertou in resultados_por_topico]

    return {
        "taxa_geral": calcular_taxa_acerto(todos),
        "por_topico": por_topico,
        "total": len(todos),
    }
