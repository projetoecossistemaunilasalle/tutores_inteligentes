"""Detecta o estado emocional do aluno a partir do texto, via LLM (Groq), e grava
no perfil. É um sinal aproximado para o tutor ajustar o tom — não um diagnóstico."""

import os

# Biblioteca da Groq. Precisa ser instalada antes de usar:  pip install groq
# (enquanto não instalar, o editor vai sublinhar este import — é normal.)
from groq import Groq


# As sete categorias possíveis. São as mesmas que combinamos: um conjunto
# pequeno, mas que permite ao tutor reagir de formas diferentes.
ESTADOS_EMOCIONAIS = [
    "satisfeito",    # engajado/motivado  -> manter ritmo, propor mais desafio
    "confiante",     # domina o ponto      -> pode avançar
    "neutro",        # sem carga clara     -> segue normal
    "confuso",       # não entendeu        -> re-explicar de outro jeito
    "frustrado",     # travou/irritou      -> simplificar, encorajar
    "ansioso",       # medo de errar       -> tranquilizar, reforçar acertos
    "desmotivado",   # desinteresse        -> mudar a abordagem
]

# Modelo da Groq a ser usado. É só um EXEMPLO — confira na documentação da
# Groq qual modelo está disponível no momento e ajuste aqui se precisar.
MODELO_GROQ = "llama-3.1-8b-instant"


def _cliente_groq() -> Groq:
    """Cria o cliente da Groq usando a chave guardada no ambiente (.env).

    A variável GROQ_API_KEY precisa estar carregada (ver nota no final).
    """
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def detectar_estado_emocional(texto_aluno: str) -> str:
    """Classifica a mensagem do aluno em UMA das categorias emocionais.

    Args:
        texto_aluno: a mensagem escrita pelo aluno.

    Returns:
        str: uma das categorias de ESTADOS_EMOCIONAIS.
             Se a LLM responder algo fora da lista, retorna "neutro".
    """
    cliente = _cliente_groq()

    # Instrução para a LLM: responder com APENAS uma das categorias válidas.
    instrucao = (
        "Você classifica o estado emocional de um aluno a partir da mensagem "
        "dele em um tutor de estudos. Responda com APENAS UMA palavra, "
        "exatamente uma destas opções: " + ", ".join(ESTADOS_EMOCIONAIS) + "."
    )

    resposta = cliente.chat.completions.create(
        model=MODELO_GROQ,
        messages=[
            {"role": "system", "content": instrucao},
            {"role": "user", "content": texto_aluno},
        ],
        temperature=0,   # 0 = respostas mais estáveis/consistentes
        max_tokens=5,    # só precisamos de uma palavra
    )

    # Pega o texto retornado, limpa espaços e deixa em minúsculas.
    estado = resposta.choices[0].message.content.strip().lower()

    # Segurança: só aceita se for uma categoria válida; senão, "neutro".
    return estado if estado in ESTADOS_EMOCIONAIS else "neutro"


def registrar_estado_emocional(perfil, texto_aluno: str) -> str:
    """Detecta o estado emocional e GRAVA no perfil do aluno.

    Args:
        perfil: objeto PerfilAluno a ser atualizado.
        texto_aluno: a mensagem escrita pelo aluno.

    Returns:
        str: o estado emocional gravado no perfil.
    """
    estado = detectar_estado_emocional(texto_aluno)

    perfil.estado_emocional = estado
    perfil.save()  # atualiza a linha do aluno no banco

    return estado
