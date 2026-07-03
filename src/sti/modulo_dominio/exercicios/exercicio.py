"""Define a estrutura de cada exercício de prática: enunciado, tópico e nível
de dificuldade. O desempenho do aluno nos exercícios alimenta a análise de desempenho."""

from django.db import models

# Liga cada exercício a um tópico do conteúdo.
from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import ConteudoAlgoritmos


class Exercicio(models.Model):
    """Um exercício de prática da disciplina."""

    NIVEL_CHOICES = [
        ("iniciante", "Iniciante"),
        ("intermediario", "Intermediário"),
        ("avancado", "Avançado"),
    ]

    # ------------------------------------------------------------------ #
    # 1) O EXERCÍCIO                                                      #
    # ------------------------------------------------------------------ #
    enunciado = models.TextField("Enunciado do exercício")

    # ------------------------------------------------------------------ #
    # 2) A QUE TÓPICO PERTENCE E QUAL O NÍVEL                             #
    # ------------------------------------------------------------------ #
    topico = models.ForeignKey(
        ConteudoAlgoritmos,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="exercicios",
        verbose_name="Tópico",
    )
    nivel = models.CharField(
        "Nível de dificuldade",
        max_length=20,
        choices=NIVEL_CHOICES,
        default="iniciante",
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                         #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        app_label = "banco_dados"
        verbose_name = "Exercício"
        verbose_name_plural = "Exercícios"
        ordering = ["topico", "nivel"]

    def __str__(self):
        return self.enunciado[:60]