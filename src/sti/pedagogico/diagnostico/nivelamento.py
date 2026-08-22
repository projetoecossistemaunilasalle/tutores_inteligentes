"""A cada rodada de exercícios, determina o nível do aluno e registra o nivelamento
no histórico. Diferente de avaliacao_inicial.py (uso único), roda continuamente."""

from sti.modulo_aluno.desempenho.analise_desempenho import (
    analisar_desempenho,
)
from sti.modulo_aluno.desempenho.nivel_proficiencia import (
    atualizar_nivel_aluno,
)
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)


def nivelar_aluno(perfil, resultados_por_topico):
    """Determina o nível do aluno e registra o nivelamento.

    Args:
        perfil: o PerfilAluno a ser avaliado e atualizado.
        resultados_por_topico: lista de tuplas (topico,
            acertou), onde 'acertou' é booleano.
            Ex.: [("lacos", True), ("vetores", False)]

    Returns:
        dict com as chaves:
            nivel (str): nível gravado no perfil.
            analise (dict): saída de analisar_desempenho().
    """
    # 1) Analisa o desempenho geral e por tópico.
    analise = analisar_desempenho(resultados_por_topico)

    # 2) Converte a taxa geral em nível e grava no perfil.
    nivel = atualizar_nivel_aluno(perfil, analise["taxa_geral"])

    # 3) Monta um resumo por tópico para o registro.
    resumo_topicos = "; ".join(
        f"{topico}: {taxa:.0f}%"
        for topico, taxa in analise["por_topico"].items()
    )

    # 4) Registra o nivelamento no histórico (evolução
    #    rastreável). origem='regras' = cálculo, sem custo.
    HistoricoInteracoes.objects.create(
        aluno=perfil,
        pergunta="[nivelamento automático]",
        resposta=(
            f"Nível definido: {nivel} | "
            f"Taxa geral: {analise['taxa_geral']:.0f}% | "
            f"Por tópico: {resumo_topicos}"
        ),
        topico="nivelamento",
        origem="regras",
    )

    return {"nivel": nivel, "analise": analise}
