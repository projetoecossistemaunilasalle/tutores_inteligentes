"""Define cada tópico de conteúdo da disciplina (ex.: "Vetores", "Laços de repetição").
Usado pelo Pedagógico para montar a trilha e pelo Motor de IA para gerar explicações."""

from django.db import models


class ConteudoAlgoritmos(models.Model):
    """Uma unidade de conteúdo (tópico) da disciplina."""

    # As mesmas faixas de nível usadas no perfil do aluno, para que tópico e
    # aluno fiquem na mesma "linguagem" de nível.
    NIVEL_CHOICES = [
        ("iniciante", "Iniciante"),
        ("intermediario", "Intermediário"),
        ("avancado", "Avançado"),
    ]

    # ------------------------------------------------------------------ #
    # 1) IDENTIFICAÇÃO DO TÓPICO                                          #
    # ------------------------------------------------------------------ #
    titulo = models.CharField("Título do tópico", max_length=150)
    descricao = models.CharField("Descrição breve", max_length=300, blank=True)
    conteudo = models.TextField("Conteúdo / material explicativo", blank=True)

    # ------------------------------------------------------------------ #
    # 2) CLASSIFICAÇÃO E SEQUÊNCIA                                        #
    # ------------------------------------------------------------------ #
    nivel = models.CharField(
        "Nível",
        max_length=20,
        choices=NIVEL_CHOICES,
        default="iniciante",
    )
    ordem = models.PositiveIntegerField(
        "Ordem na trilha",
        default=0,  # define a sequência em que os tópicos aparecem
    )

    # Pré-requisito: aponta para OUTRO tópico que deve vir antes deste.
    # "self" = uma ligação com o próprio modelo (um tópico aponta para outro).
    # Opcional (null/blank): nem todo tópico tem pré-requisito.
    pre_requisito = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,   # se o pré-requisito for apagado, só limpa o vínculo
        related_name="desbloqueia",
        verbose_name="Pré-requisito",
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                         #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        """Metadados e configurações para o modelo Conteúdos."""
        app_label = "banco_dados"
        verbose_name = "Conteúdo (Algoritmos)"
        verbose_name_plural = "Conteúdos (Algoritmos)"
        ordering = ["ordem", "titulo"]  # ordena pela sequência da trilha

    def __str__(self):
        return f"{self.ordem}. {self.titulo} ({self.nivel})"
