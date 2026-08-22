"""Guarda a resposta correta e a explicação de cada exercício.
Comparado com a resposta do aluno para alimentar a análise de desempenho."""

from django.db import models

# Liga o gabarito ao exercício correspondente.
from sti.modulo_dominio.exercicios.exercicio import Exercicio


class Gabarito(models.Model):
    """A resposta correta de um exercício."""

    # ------------------------------------------------------------------ #
    # 1) A QUE EXERCÍCIO ESTE GABARITO PERTENCE                          #
    # ------------------------------------------------------------------ #
    # OneToOneField = relação "um para um": cada exercício tem exatamente
    # um gabarito, e cada gabarito pertence a um único exercício.
    exercicio = models.OneToOneField(
        Exercicio,
        on_delete=models.CASCADE,   # se o exercício for apagado, o gabarito vai junto
        related_name="gabarito",
        verbose_name="Exercício",
    )

    # ------------------------------------------------------------------ #
    # 2) A RESPOSTA                                                       #
    # ------------------------------------------------------------------ #
    resposta_correta = models.TextField("Resposta correta")
    explicacao = models.TextField(
        "Explicação",
        blank=True,  # opcional: por que a resposta está correta
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                         #
    # ------------------------------------------------------------------ #
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        app_label = "banco_dados"
        verbose_name = "Gabarito"
        verbose_name_plural = "Gabaritos"

    def __str__(self):
        return f"Gabarito:{self.exercicio.enunciado[:50]}"