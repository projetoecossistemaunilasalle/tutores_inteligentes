"""
Modelos de Progresso do frontend.
Registra a evolucao do aluno: progresso nas licoes,
nivel de XP, conquistas e notificacoes.
"""

from django.db import models
from django.conf import settings


class ProgressoLicao(models.Model):
    """Progresso do aluno em uma licao especifica."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="progressos",
        verbose_name="Usuario",
    )
    licao = models.ForeignKey(
        "app.Licao",
        on_delete=models.CASCADE,
        related_name="progressos",
        verbose_name="Licao",
    )

    # ------------------------------------------------------------------ #
    # 2) PROGRESSO                                                         #
    # ------------------------------------------------------------------ #
    etapa_atual = models.PositiveSmallIntegerField(
        "Etapa atual",
        default=0,
    )
    concluida = models.BooleanField("Concluida", default=False)
    xp_ganho = models.SmallIntegerField("XP ganho", default=0)

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    iniciado_em = models.DateTimeField(
        "Iniciado em",
        auto_now_add=True,
    )
    concluido_em = models.DateTimeField(
        "Concluido em",
        null=True,
        blank=True,
    )
    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Progresso de Licao"
        verbose_name_plural = "Progressos de Licoes"
        unique_together = ["usuario", "licao"]
        ordering = ["-atualizado_em"]

    def __str__(self):
        status = "concluida" if self.concluida else "em andamento"
        return f"{self.usuario} — {self.licao} ({status})"


class NivelUsuario(models.Model):
    """Nivel e XP acumulado do aluno."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO (1:1 com Usuario)                                  #
    # ------------------------------------------------------------------ #
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nivel",
        verbose_name="Usuario",
    )

    # ------------------------------------------------------------------ #
    # 2) NIVEL E XP                                                        #
    # ------------------------------------------------------------------ #
    xp_total = models.IntegerField("XP total", default=0)
    nivel = models.SmallIntegerField("Nivel", default=1)
    xp_proximo_nivel = models.IntegerField(
        "XP para o proximo nivel",
        default=100,
    )
    streak_dias = models.SmallIntegerField(
        "Sequencia de dias",
        default=0,
    )
    ultima_atividade = models.DateField(
        "Ultima atividade",
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Nivel do Usuario"
        verbose_name_plural = "Niveis dos Usuarios"

    def __str__(self):
        return f"{self.usuario} — Nivel {self.nivel} ({self.xp_total} XP)"


class Conquista(models.Model):
    """Conquista (badge) disponivel no sistema."""

    # ------------------------------------------------------------------ #
    # 1) IDENTIFICACAO                                                     #
    # ------------------------------------------------------------------ #
    codigo = models.CharField(
        "Codigo",
        max_length=60,
        unique=True,
    )
    nome = models.CharField("Nome", max_length=100)
    descricao = models.TextField("Descricao", blank=True)
    icone = models.CharField("Icone", max_length=10, blank=True)
    xp_bonus = models.SmallIntegerField("XP bonus", default=0)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Conquista"
        verbose_name_plural = "Conquistas"

    def __str__(self):
        return self.nome


class ConquistaUsuario(models.Model):
    """Conquista desbloqueada por um usuario."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conquistas",
        verbose_name="Usuario",
    )
    conquista = models.ForeignKey(
        Conquista,
        on_delete=models.CASCADE,
        related_name="usuarios",
        verbose_name="Conquista",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ganho_em = models.DateTimeField(
        "Ganho em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Conquista do Usuario"
        verbose_name_plural = "Conquistas dos Usuarios"
        unique_together = ["usuario", "conquista"]

    def __str__(self):
        return f"{self.usuario} — {self.conquista}"


class Notificacao(models.Model):
    """Notificacao enviada ao usuario."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name="Usuario",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO                                                          #
    # ------------------------------------------------------------------ #
    tipo = models.CharField("Tipo", max_length=40)
    titulo = models.CharField("Titulo", max_length=120)
    corpo = models.TextField("Corpo", blank=True)
    link = models.URLField("Link", max_length=300, blank=True)

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    lida = models.BooleanField("Lida", default=False)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    lida_em = models.DateTimeField(
        "Lida em",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Notificacao"
        verbose_name_plural = "Notificacoes"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.usuario} — {self.titulo}"
