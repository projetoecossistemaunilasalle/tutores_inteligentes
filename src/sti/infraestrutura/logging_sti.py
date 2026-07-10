"""
Configuração de logging (registro de eventos) do STI.
Registra erros e eventos importantes para facilitar
a identificação de problemas em desenvolvimento e produção.

No Render, os logs aparecem automaticamente no painel
sem necessidade de alteração.
"""

import logging

# Cria um logger com o nome do sistema.
logger = logging.getLogger("sti")


def registrar_erro(mensagem, excecao=None):
    """Registra um erro no log do sistema.

    Args:
        mensagem: descrição do erro.
        excecao: exceção capturada (opcional).
    """
    if excecao:
        logger.error("%s | %s", mensagem, str(excecao))
    else:
        logger.error(mensagem)


def registrar_evento(mensagem):
    """Registra um evento informativo no log.

    Args:
        mensagem: descrição do evento.
    """
    logger.info(mensagem)
