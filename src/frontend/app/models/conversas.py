"""
Modelos de Conversas e Mensagens do frontend.
Registra as sessoes de chat do aluno com o tutor,
incluindo cada mensagem trocada e o consumo de tokens.
"""

from django.db import models
from django.conf import settings


class Conversa(models.Model):
    """Sessao de chat entre o aluno e o tutor."""

    # ------------------------------------------------------------------ #
    # 1) PARTICIPANTES E CONTEXTO                                          #
    # ------------------------------------------------------------------ #
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversas",
        verbose_name="Usuario",
    )
    disciplina = models.ForeignKey(
        "app.Disciplina",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversas",
        verbose_name="Disciplina",
    )
    licao = models.ForeignKey(
        "app.Licao",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="conversas",
        verbose_name="Licao",
    )

    # ------------------------------------------------------------------ #
    # 2) DADOS DA CONVERSA                                                 #
    # ------------------------------------------------------------------ #
    titulo = models.CharField(
        "Titulo",
        max_length=200,
        blank=True,
    )
    total_mensagens = models.SmallIntegerField(
        "Total de mensagens",
        default=0,
    )
    tokens_usados = models.IntegerField(
        "Tokens usados",
        default=0,
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    iniciada_em = models.DateTimeField(
        "Iniciada em",
        auto_now_add=True,
    )
    encerrada_em = models.DateTimeField(
        "Encerrada em",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"
        ordering = ["-iniciada_em"]

    def __str__(self):
        return (
            f"{self.usuario} — "
            f"{self.titulo or 'sem titulo'} "
            f"({self.iniciada_em:%d/%m/%Y})"
        )


class Mensagem(models.Model):
    """Mensagem individual dentro de uma conversa."""

    PAPEL_CHOICES = [
        ("aluno", "Aluno"),
        ("tutor", "Tutor"),
    ]

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    conversa = models.ForeignKey(
        Conversa,
        on_delete=models.CASCADE,
        related_name="mensagens",
        verbose_name="Conversa",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO                                                          #
    # ------------------------------------------------------------------ #
    papel = models.CharField(
        "Papel",
        max_length=10,
        choices=PAPEL_CHOICES,
    )
    conteudo = models.TextField("Conteudo")
    tokens = models.SmallIntegerField("Tokens", default=0)

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    enviado_em = models.DateTimeField(
        "Enviado em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ["enviado_em"]

    def __str__(self):
        return (
            f"{self.papel}: "
            f"{self.conteudo[:50]}"
        )
