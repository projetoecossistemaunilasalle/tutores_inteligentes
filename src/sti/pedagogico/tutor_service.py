"""Ponto de entrada do módulo pedagógico: orquestra diagnóstico e planejamento.
Quem chama (o Motor de IA) não precisa conhecer os detalhes internos."""

from sti.pedagogico.diagnostico.avaliacao_inicial import (
    avaliar_aluno_inicial,
)
from sti.pedagogico.diagnostico.nivelamento import nivelar_aluno
from sti.pedagogico.diagnostico.perfil_aprendizado import (
    registrar_estilo_aprendizado,
)
from sti.pedagogico.planejamento.plano_aprendizagem import (
    montar_plano,
)


def iniciar_sessao(perfil, resultados_iniciais, respostas_estilo):
    """Fluxo completo da PRIMEIRA sessão do aluno.

    Avalia o nível, registra o estilo de aprendizado e
    devolve o plano inicial.

    Args:
        perfil: o PerfilAluno recém-criado.
        resultados_iniciais: lista de booleanos (True =
            acertou) da atividade de entrada.
        respostas_estilo: lista de estilos escolhidos pelo
            aluno no questionário inicial.
            Ex.: ["visual", "visual", "pratico"]

    Returns:
        dict com as chaves:
            nivel (str)
            estilo (str)
            plano (dict)
    """
    # 1) Define o nível e grava no perfil.
    nivel = avaliar_aluno_inicial(perfil, resultados_iniciais)

    # 2) Identifica o estilo de aprendizado e grava no perfil.
    estilo = registrar_estilo_aprendizado(perfil, respostas_estilo)

    # 3) Monta o plano inicial com base no nível e no estilo.
    # Nota: conteudos é buscado pelo Motor de IA antes de
    # chamar este serviço.
    return {"nivel": nivel, "estilo": estilo}


def atualizar_sessao(perfil, resultados_por_topico):
    """Fluxo de ATUALIZAÇÃO contínua após cada rodada.

    Nivela o aluno com base no desempenho mais recente e
    registra no histórico.

    Args:
        perfil: o PerfilAluno a ser atualizado.
        resultados_por_topico: lista de tuplas
            (topico, acertou).

    Returns:
        dict: resultado do nivelamento (nivel + analise).
    """
    return nivelar_aluno(perfil, resultados_por_topico)


def obter_plano(perfil, conteudos):
    """Devolve o plano de aprendizagem ATUAL do aluno.

    Usa o nível e o estilo já gravados no perfil para montar
    objetivos + trilha + estratégia.

    Args:
        perfil: o PerfilAluno com nível e estilo já definidos.
        conteudos: lista de ConteudoAlgoritmos do domínio.

    Returns:
        dict com as chaves:
            objetivos (list)
            trilha (list)
            estrategia (str)
    """
    return montar_plano(perfil, conteudos)
