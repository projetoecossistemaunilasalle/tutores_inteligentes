"""Registra cada interação do aluno com o STI (pergunta, resposta, tópico e origem
da resposta). Lido pelo módulo de Desempenho para analisar a evolução do aluno."""

from django.db import models

# Importamos PerfilAluno para ligar cada interação ao aluno que a gerou.
from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno


class HistoricoInteracoes(models.Model):
    """Uma única interação (pergunta + resposta) entre um aluno e o tutor."""

    # ------------------------------------------------------------------ #
    # 1) A QUEM PERTENCE ESTA INTERAÇÃO                                   #
    # ------------------------------------------------------------------ #
    # ForeignKey = ligação com outra tabela. Cada interação pertence a um
    # PerfilAluno. 'related_name' permite acessar todas as interações de um
    # aluno escrevendo:  aluno.interacoes.all()
    aluno = models.ForeignKey(
        PerfilAluno,
        on_delete=models.CASCADE,   # se o aluno for apagado, apaga as interações
        related_name="interacoes",
        verbose_name="Aluno",
    )

    # ------------------------------------------------------------------ #
    # 2) O CONTEÚDO DA INTERAÇÃO                                          #
    # ------------------------------------------------------------------ #
    pergunta = models.TextField("Pergunta do aluno")
    resposta = models.TextField("Resposta dada pelo tutor")
    topico = models.CharField(
        "Tópico / assunto",
        max_length=120,
        blank=True,  # opcional: pode não estar identificado
    )

    # ------------------------------------------------------------------ #
    # 3) QUAL IA RESPONDEU (controle de custo da hibridização)           #
    # ------------------------------------------------------------------ #
    ORIGEM_CHOICES = [
        ("regras", "IA Estruturada (regras) — sem custo"),
        ("llm", "LLM em nuvem (Groq) — com custo"),
    ]
    origem = models.CharField(
        "Origem da resposta",
        max_length=10,
        choices=ORIGEM_CHOICES,
        default="regras",
    )

    # ------------------------------------------------------------------ #
    # 4) QUANDO ACONTECEU (preenchido automaticamente)                   #
    # ------------------------------------------------------------------ #
    data_hora = models.DateTimeField(
        "Data e hora",
        auto_now_add=True,  # gravado uma vez, no momento da criação
    )

    class Meta:
        # Mesmo app de persistência do perfil (já registrado no settings.py).
        app_label = "banco_dados"
        verbose_name = "Histórico de Interação"
        verbose_name_plural = "Histórico de Interações"
        ordering = ["-data_hora"]  # mais recentes primeiro

    def __str__(self):
        return f"{self.aluno.nome} — {self.topico or 'sem tópico'} ({self.data_hora:%d/%m/%Y %H:%M})"
