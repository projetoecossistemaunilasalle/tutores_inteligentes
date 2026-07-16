"""
Modelos de Disciplinas e Licoes do frontend.
O professor cadastra as disciplinas e suas licoes.
O aluno acessa o conteudo e acompanha o progresso.
"""

from django.db import models


class Disciplina(models.Model):
    """Disciplina disponivel no sistema."""

    # ------------------------------------------------------------------ #
    # 1) IDENTIFICACAO                                                     #
    # ------------------------------------------------------------------ #
    nome = models.CharField("Nome", max_length=80, unique=True)
    descricao = models.TextField("Descricao", blank=True)
    icone = models.CharField("Icone", max_length=10, blank=True)
    cor_primaria = models.CharField(
        "Cor primaria",
        max_length=40,
        default="#1a73e8",
    )

    # ------------------------------------------------------------------ #
    # 2) CONFIGURACAO PEDAGOGICA                                           #
    # ------------------------------------------------------------------ #
    # Prompt que orienta o tutor ao responder sobre esta disciplina
    prompt_sistema = models.TextField(
        "Prompt do sistema",
        blank=True,
    )
    ordem = models.SmallIntegerField("Ordem", default=0)

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ativa = models.BooleanField("Ativa", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Disciplina"
        verbose_name_plural = "Disciplinas"
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome


class Licao(models.Model):
    """Licao dentro de uma disciplina."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    disciplina = models.ForeignKey(
        Disciplina,
        on_delete=models.CASCADE,
        related_name="licoes",
        verbose_name="Disciplina",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO                                                          #
    # ------------------------------------------------------------------ #
    titulo = models.CharField("Titulo", max_length=150)
    descricao = models.TextField("Descricao", blank=True)
    conteudo = models.TextField("Conteudo", blank=True)
    ordem = models.SmallIntegerField("Ordem", default=0)
    total_etapas = models.PositiveSmallIntegerField(
        "Total de etapas",
        default=1,
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ativa = models.BooleanField("Ativa", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Licao"
        verbose_name_plural = "Licoes"
        ordering = ["disciplina", "ordem"]

    def __str__(self):
        return f"{self.disciplina.nome} — {self.titulo}"
