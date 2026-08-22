"""
Modelo de historico de interacoes do aluno com o tutor.
Registra cada conversa, incluindo agora se o RAG foi usado
e quais fontes foram consultadas.
"""

from django.db import models
from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno


class HistoricoInteracoes(models.Model):
    """Uma unica interacao (pergunta + resposta) com o tutor."""

    # ------------------------------------------------------------------ #
    # 1) A QUEM PERTENCE                                                   #
    # ------------------------------------------------------------------ #
    aluno = models.ForeignKey(
        PerfilAluno,
        on_delete=models.CASCADE,
        related_name="interacoes",
        verbose_name="Aluno",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO DA INTERACAO                                             #
    # ------------------------------------------------------------------ #
    pergunta = models.TextField("Pergunta do aluno")
    resposta = models.TextField("Resposta do tutor")
    topico = models.CharField(
        "Topico / assunto",
        max_length=120,
        blank=True,
    )

    # ------------------------------------------------------------------ #
    # 3) ORIGEM DA RESPOSTA                                                #
    # ------------------------------------------------------------------ #
    ORIGEM_CHOICES = [
        ("regras", "IA Estruturada (regras) — sem custo"),
        ("llm",    "LLM em nuvem (Groq) — com custo"),
    ]
    origem = models.CharField(
        "Origem da resposta",
        max_length=10,
        choices=ORIGEM_CHOICES,
        default="regras",
    )

    # NOVO: indica se o RAG foi usado para fundamentar a resposta
    usou_rag = models.BooleanField(
        "Usou RAG (material do professor)",
        default=False,
    )

    # NOVO: fontes consultadas pelo RAG (nomes dos PDFs)
    fontes_rag = models.TextField(
        "Fontes consultadas pelo RAG",
        blank=True,
        help_text="Trechos do material do professor usados na resposta.",
    )

    # ------------------------------------------------------------------ #
    # 4) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    data_hora = models.DateTimeField(
        "Data e hora",
        auto_now_add=True,
    )

    class Meta:
        app_label = "banco_dados"
        verbose_name = "Historico de Interacao"
        verbose_name_plural = "Historico de Interacoes"
        ordering = ["-data_hora"]

    def __str__(self):
        rag = " [RAG]" if self.usou_rag else ""
        return (
            f"{self.aluno.nome} — "
            f"{self.topico or 'sem topico'}{rag} "
            f"({self.data_hora:%d/%m/%Y %H:%M})"
        )
