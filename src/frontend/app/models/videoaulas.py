"""
Modelo de Videoaulas do frontend.
O professor cadastra links de videoaulas do YouTube
associados a disciplinas e licoes especificas.
"""

from django.db import models
from django.conf import settings


class Videoaula(models.Model):
    """Link de videoaula cadastrado pelo professor."""

    # ------------------------------------------------------------------ #
    # 1) IDENTIFICACAO                                                     #
    # ------------------------------------------------------------------ #
    titulo = models.CharField("Titulo", max_length=200)
    descricao = models.TextField("Descricao", blank=True)
    url_youtube = models.URLField("Link do YouTube", max_length=500)
    duracao_minutos = models.PositiveSmallIntegerField(
        "Duracao (minutos)",
        default=0,
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEXTO PEDAGOGICO                                               #
    # ------------------------------------------------------------------ #
    disciplina = models.ForeignKey(
        "app.Disciplina",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videoaulas",
        verbose_name="Disciplina",
    )
    licao = models.ForeignKey(
        "app.Licao",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videoaulas",
        verbose_name="Licao",
    )
    topico = models.ForeignKey(
        "banco_dados.ConteudoAlgoritmos",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videoaulas",
        verbose_name="Topico da base de conhecimento",
    )
    ordem = models.PositiveSmallIntegerField("Ordem", default=0)

    # ------------------------------------------------------------------ #
    # 3) CADASTRO                                                          #
    # ------------------------------------------------------------------ #
    cadastrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videoaulas_cadastradas",
        verbose_name="Cadastrado por",
    )

    # ------------------------------------------------------------------ #
    # 4) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ativa = models.BooleanField("Ativa", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Videoaula"
        verbose_name_plural = "Videoaulas"
        ordering = ["disciplina", "licao", "ordem"]

    def __str__(self):
        return self.titulo

    @property
    def embed_url(self):
        """Converte o link do YouTube para formato embed (iframe)."""
        if "watch?v=" in self.url_youtube:
            video_id = self.url_youtube.split("watch?v=")[-1]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.url_youtube
