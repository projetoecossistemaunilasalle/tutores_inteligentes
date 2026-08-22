"""
Modelos de Quizzes do frontend.
Gerencia os questionarios, questoes, alternativas
e as tentativas dos alunos.
"""

from django.db import models
from django.conf import settings


class Quiz(models.Model):
    """Questionario de fixacao vinculado a uma licao."""

    # ------------------------------------------------------------------ #
    # 1) CONTEXTO                                                          #
    # ------------------------------------------------------------------ #
    disciplina = models.ForeignKey(
        "app.Disciplina",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quizzes",
        verbose_name="Disciplina",
    )
    licao = models.ForeignKey(
        "app.Licao",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="quizzes",
        verbose_name="Licao",
    )

    # ------------------------------------------------------------------ #
    # 2) DADOS DO QUIZ                                                     #
    # ------------------------------------------------------------------ #
    titulo = models.CharField("Titulo", max_length=200)
    descricao = models.TextField("Descricao", blank=True)
    total_questoes = models.PositiveSmallIntegerField(
        "Total de questoes",
        default=0,
    )
    gerado_por_ia = models.BooleanField(
        "Gerado por IA",
        default=False,
    )

    # ------------------------------------------------------------------ #
    # 3) CONTROLE                                                          #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.titulo


class Questao(models.Model):
    """Questao de um quiz."""

    TIPO_CHOICES = [
        ("multipla", "Multipla escolha"),
        ("verdadeiro_falso", "Verdadeiro ou Falso"),
        ("dissertativa", "Dissertativa"),
    ]

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questoes",
        verbose_name="Quiz",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO                                                          #
    # ------------------------------------------------------------------ #
    enunciado = models.TextField("Enunciado")
    tipo = models.CharField(
        "Tipo",
        max_length=20,
        choices=TIPO_CHOICES,
        default="multipla",
    )
    explicacao = models.TextField("Explicacao", blank=True)
    ordem = models.PositiveSmallIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Questao"
        verbose_name_plural = "Questoes"
        ordering = ["quiz", "ordem"]

    def __str__(self):
        return self.enunciado[:60]


class Alternativa(models.Model):
    """Alternativa de uma questao de multipla escolha."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    questao = models.ForeignKey(
        Questao,
        on_delete=models.CASCADE,
        related_name="alternativas",
        verbose_name="Questao",
    )

    # ------------------------------------------------------------------ #
    # 2) CONTEUDO                                                          #
    # ------------------------------------------------------------------ #
    texto = models.TextField("Texto")
    correta = models.BooleanField("Correta", default=False)
    ordem = models.PositiveSmallIntegerField("Ordem", default=0)

    class Meta:
        verbose_name = "Alternativa"
        verbose_name_plural = "Alternativas"
        ordering = ["questao", "ordem"]

    def __str__(self):
        return self.texto[:50]


class TentativaQuiz(models.Model):
    """Tentativa de um aluno em um quiz."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tentativas",
        verbose_name="Usuario",
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="tentativas",
        verbose_name="Quiz",
    )

    # ------------------------------------------------------------------ #
    # 2) RESULTADO                                                         #
    # ------------------------------------------------------------------ #
    acertos = models.PositiveSmallIntegerField("Acertos", default=0)
    total = models.PositiveSmallIntegerField("Total", default=0)
    pontuacao = models.DecimalField(
        "Pontuacao",
        max_digits=5,
        decimal_places=2,
        default=0,
    )
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

    class Meta:
        verbose_name = "Tentativa de Quiz"
        verbose_name_plural = "Tentativas de Quiz"
        ordering = ["-iniciado_em"]

    def __str__(self):
        return (
            f"{self.usuario} — {self.quiz} "
            f"({self.pontuacao}%)"
        )


class RespostaQuiz(models.Model):
    """Resposta do aluno a uma questao especifica."""

    # ------------------------------------------------------------------ #
    # 1) RELACIONAMENTO                                                    #
    # ------------------------------------------------------------------ #
    tentativa = models.ForeignKey(
        TentativaQuiz,
        on_delete=models.CASCADE,
        related_name="respostas",
        verbose_name="Tentativa",
    )
    questao = models.ForeignKey(
        Questao,
        on_delete=models.CASCADE,
        related_name="respostas",
        verbose_name="Questao",
    )
    alternativa = models.ForeignKey(
        Alternativa,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="respostas",
        verbose_name="Alternativa escolhida",
    )

    # ------------------------------------------------------------------ #
    # 2) RESULTADO                                                         #
    # ------------------------------------------------------------------ #
    resposta_texto = models.TextField(
        "Resposta dissertativa",
        blank=True,
    )
    correta = models.BooleanField("Correta", default=False)
    respondido_em = models.DateTimeField(
        "Respondido em",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Resposta de Quiz"
        verbose_name_plural = "Respostas de Quiz"

    def __str__(self):
        return (
            f"{self.tentativa.usuario} — "
            f"{self.questao.enunciado[:40]}"
        )
