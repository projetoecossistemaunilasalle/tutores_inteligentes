"""
Modelo de Videoaulas.
Armazena links de videoaulas cadastrados pelo professor,
associados a um tópico da base de conhecimento.
"""

from django.db import models

from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import \
    ConteudoAlgoritmos


class Videoaula(models.Model):
    """Link de videoaula cadastrado pelo professor."""

    # ------------------------------------------------------------------ #
    # 1) IDENTIFICAÇÃO                                                     #
    # ------------------------------------------------------------------ #
    titulo = models.CharField("Título", max_length=200)
    url_youtube = models.URLField("Link do YouTube", max_length=500)
    descricao = models.TextField("Descrição", blank=True)

    # ------------------------------------------------------------------ #
    # 2) TÓPICO RELACIONADO                                               #
    # ------------------------------------------------------------------ #
    topico = models.ForeignKey(
        ConteudoAlgoritmos,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="videoaulas",
        verbose_name="Tópico relacionado",
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                         #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        app_label = "banco_dados"
        verbose_name = "Videoaula"
        verbose_name_plural = "Videoaulas"
        ordering = ["topico", "titulo"]

    def __str__(self):
        return self.titulo
