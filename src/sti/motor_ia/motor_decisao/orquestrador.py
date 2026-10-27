"""
Ponto central do Motor de IA. Recebe a pergunta do aluno,
aciona as camadas na ordem certa e devolve a resposta final.

Ordem de decisao (mais barato -> mais caro):
  1. IA Estruturada (regras + Q&A) — sem custo
  2. RAG (busca no material do professor) — sem custo de LLM na busca
  3a. LLM Groq COM material (quando o RAG encontrou trecho relevante)
  3b. LLM Groq SEM material / conhecimento proprio, com aviso
      (Opcao 2: quando o RAG nao encontrou nada relevante,
       para nao deixar o aluno sem resposta)

responder() e a unica funcao que a Interface (Grupo 2) chama.
"""

from sti.modulo_dominio.rag.buscador import (
    buscar_com_relevancia,
    montar_contexto,
    buscar_exercicios,
)
from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.modulo_dominio.rag.buscador import (
    buscar_com_relevancia,
    montar_contexto,
)
from sti.motor_ia.ia_estruturada.motor_regras import (
    processar_com_regras,
)
from sti.motor_ia.ia_embarcada.llm_nuvem import gerar_resposta

import re
import difflib
import unicodedata

# Temas das perguntas e as palavras-chave de cada um (sem acento, minusculas).
# Para ajustar os temas, basta editar esta lista.
TEMAS_PALAVRAS = [
    ("Algoritmos", ["algoritmo", "algoritmos",
     "fluxograma", "pseudocodigo", "portugol"]),
    ("Variáveis e tipos", ["variavel", "variaveis", "constante", "constantes", "tipo de dado",
                           "tipos de dados", "inteiro", "float", "string", "char", "booleano", "atribuicao"]),
    ("Entrada e saída", ["leia", "escreva", "input", "print", "entrada", "saida", "output",
                         "exibir", "imprimir", "mostrar"]),
    ("Operadores", ["operador", "operadores", "aritmetico", "aritmeticos", "logico", "logicos",
                    "relacional", "relacionais", "expressao", "expressoes"]),
    ("Condicionais", ["condicional", "condicionais", "if", "else", "elif", "senao", "se entao",
                      "switch", "escolha caso", "estrutura de decisao"]),
    ("Repetição", ["laco", "lacos", "loop", "loops", "enquanto", "repita", "for", "while",
                   "repeticao", "faca enquanto"]),
    ("Vetores e matrizes", ["vetor", "vetores", "array",
     "arrays", "lista", "listas", "matriz", "matrizes"]),
    ("Funções", ["funcao", "funcoes", "procedimento", "procedimentos", "parametro", "parametros",
                 "retorno", "def", "modular", "modulo", "modulos", "modularizacao"]),
    ("Ponteiros e memória", ["ponteiro", "ponteiros",
     "malloc", "free", "memoria", "alocacao"]),
    ("Registros", ["registro", "registros", "struct", "structs"]),
    ("Sintaxe", ["indentacao", "sintaxe", "comentario", "comentarios"]),
    ("Requisitos", ["requisito", "requisitos"]),
]


def _normalizar(texto):
    """Minusculas e sem acentos, para comparar palavras."""
    t = unicodedata.normalize("NFKD", (texto or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def _contem(palavra_chave, texto, palavras_texto):
    """Palavra-chave presente no texto. Palavras com 6+ letras aceitam
    pequenos erros de digitacao (ex.: 'vraiavel' -> 'variavel')."""
    if re.search(r"\b" + re.escape(palavra_chave) + r"\b", texto):
        return True
    if " " not in palavra_chave and len(palavra_chave) >= 6:
        return bool(difflib.get_close_matches(palavra_chave, palavras_texto, n=1, cutoff=0.87))
    return False


def classificar_tema(pergunta):
    """Tema da pergunta pelo maior numero de palavras-chave encontradas.
    Sem nenhuma palavra-chave, retorna 'Geral'."""
    texto = _normalizar(pergunta)
    palavras_texto = re.findall(r"[a-z]+", texto)
    melhor, pontos_melhor = "Geral", 0
    for tema, palavras in TEMAS_PALAVRAS:
        pontos = sum(1 for p in palavras if _contem(p, texto, palavras_texto))
        if pontos > pontos_melhor:
            melhor, pontos_melhor = tema, pontos
    return melhor


def responder(pergunta_aluno: str, aluno_id: str) -> dict:
    """Ponto de entrada para a Interface (Grupo 2).

    Returns:
        dict com: resposta, fontes, usou_rag, origem, aluno_id.
    """
    # 1) Perfil do aluno.
    perfil = PerfilAluno.objects.get(identificador=aluno_id)
    nivel = perfil.nivel_proficiencia
    estilo = perfil.estilo_aprendizado

    # 2) Camada 1 — regras e Q&A (sem custo).
    resposta = processar_com_regras(pergunta_aluno, nivel)
    fontes = []
    origem = "regras"
    usou_rag = False

    if not resposta:
        # 3) Camada 2 — RAG: busca e informa se ha material relevante.
        trechos, tem_relevante = buscar_com_relevancia(pergunta_aluno)

        if tem_relevante:
            # 3a) Ha material relevante: Groq responde COM base nele.
            contexto = montar_contexto(trechos)
            resposta = gerar_resposta(
                pergunta_aluno, contexto, nivel, estilo,
                modo="material",
            )
            fontes = trechos
            origem = "rag"
            usou_rag = True
        else:
            # 3b) Opcao 2 — sem material relevante:
            # Groq responde do proprio conhecimento, com aviso.
            resposta = gerar_resposta(
                pergunta_aluno, "", nivel, estilo,
                modo="conhecimento_geral",
            )
            fontes = []
            origem = "iagen"
            usou_rag = False

    # 4) Registra a interacao no historico.
    HistoricoInteracoes.objects.create(
        aluno=perfil,
        pergunta=pergunta_aluno,
        resposta=resposta,
        topico=classificar_tema(pergunta_aluno),
        origem=origem,
        usou_rag=usou_rag,
        fontes_rag="\n---\n".join(fontes) if fontes else "",
    )

    # 5) Exercicios de fixacao: questoes do banco ligadas a duvida.
    #    Qualquer falha aqui NAO afeta a resposta ao aluno.
    try:
        exercicios = buscar_exercicios(pergunta_aluno)
    except Exception:
        exercicios = []

    return {
        "resposta": resposta,
        "fontes": fontes,
        "usou_rag": usou_rag,
        "origem": origem,
        "aluno_id": aluno_id,
        "exercicios": exercicios,
    }
