"""
Modelo de Usuarios do frontend.
Estende o usuario padrao do Django adicionando
o papel (aluno ou professor) e dados de perfil visual.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """Usuario do sistema — aluno ou professor."""

    PAPEL_CHOICES = [
        ("aluno", "Aluno"),
        ("professor", "Professor"),
    ]

    # ------------------------------------------------------------------ #
    # 1) PAPEL NO SISTEMA                                                  #
    # ------------------------------------------------------------------ #
    papel = models.CharField(
        "Papel",
        max_length=20,
        choices=PAPEL_CHOICES,
        default="aluno",
    )

    # ------------------------------------------------------------------ #
    # 2) PERFIL VISUAL                                                     #
    # ------------------------------------------------------------------ #
    avatar_sigla = models.CharField(
        "Sigla do avatar",
        max_length=2,
        blank=True,
    )
    avatar_cor = models.CharField(
        "Cor do avatar",
        max_length=40,
        blank=True,
        default="#1a73e8",
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    ultimo_login_sti = models.DateTimeField(
        "Ultimo login no STI",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return f"{self.get_full_name()} ({self.papel})"

    @property
    def eh_professor(self):
        """Verifica se o usuario e professor."""
        return self.papel == "professor"

    @property
    def eh_aluno(self):
        """Verifica se o usuario e aluno."""
        return self.papel == "aluno"
