"""
Registro da resposta de cada aluno a cada exercício (Grupo 1).

Sem este modelo, a correção do exercício era apenas um estado temporário
da requisição — ao recarregar a página, o aluno perdia o feedback, e não
era possível saber quantos exercícios cada aluno já acertou (necessário
para as conquistas de exercícios).
"""

from django.db import models
from django.conf import settings


class RespostaExercicio(models.Model):
    """Última resposta enviada por um aluno a um exercício específico."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="respostas_exercicios",
        verbose_name="Usuário",
    )
    exercicio = models.ForeignKey(
        "banco_dados.Exercicio",
        on_delete=models.CASCADE,
        related_name="respostas_alunos",
        verbose_name="Exercício",
    )
    resposta = models.TextField("Resposta enviada", blank=True)
    correta = models.BooleanField("Resposta correta", default=False)
    tentativas = models.PositiveSmallIntegerField("Tentativas", default=1)
    respondido_em = models.DateTimeField("Respondido em", auto_now=True)

    class Meta:
        verbose_name = "Resposta de exercício"
        verbose_name_plural = "Respostas de exercícios"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "exercicio"], name="unico_resposta_por_aluno_exercicio"
            )
        ]

    def __str__(self):
        return f"{self.usuario} — exercício #{self.exercicio_id}"
