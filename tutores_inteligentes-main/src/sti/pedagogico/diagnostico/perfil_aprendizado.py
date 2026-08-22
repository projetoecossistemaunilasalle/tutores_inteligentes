"""Identifica o estilo de aprendizado predominante do aluno e grava no perfil.
Orienta como o tutor apresenta o conteúdo (mais exemplos, texto ou prática)."""


# Estilos de referência. Podem ser ajustados conforme a
# metodologia da pesquisa.
ESTILOS = ["visual", "textual", "pratico"]


def identificar_estilo(respostas):
    """Descobre o estilo predominante a partir das respostas.

    Args:
        respostas: lista com os estilos escolhidos pelo aluno
            (por exemplo, num questionário rápido).
            Ex.: ["visual", "pratico", "visual"] -> "visual"

    Returns:
        str: o estilo mais frequente; "" se a lista vier vazia.
    """
    if not respostas:
        return ""

    # Conta quantas vezes cada estilo aparece.
    contagem = {}
    for estilo in respostas:
        contagem[estilo] = contagem.get(estilo, 0) + 1

    # Devolve o estilo com a maior contagem.
    return max(contagem, key=contagem.get)


def registrar_estilo_aprendizado(perfil, respostas):
    """Identifica o estilo e GRAVA no perfil do aluno.

    Args:
        perfil: o PerfilAluno a ser atualizado.
        respostas: lista de estilos escolhidos pelo aluno.

    Returns:
        str: o estilo gravado no perfil.
    """
    estilo = identificar_estilo(respostas)

    perfil.estilo_aprendizado = estilo
    perfil.save()  # atualiza a linha do aluno no banco

    return estilo
