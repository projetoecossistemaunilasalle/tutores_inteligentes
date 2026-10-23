"""
Modelo de Usuarios do frontend.
Estende o usuario padrao do Django adicionando
o papel (aluno ou professor) e dados de perfil visual.

"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Usuário unificado do sistema.

    Herda de AbstractUser para aproveitar toda a autenticação nativa
    do Django: login, logout, hash de senha, troca de senha, sessões
    e integração com o painel /admin/.

    Campos herdados do AbstractUser (não precisam ser redeclarados):
        username, first_name, last_name, email, password,
        is_staff, is_active, is_superuser, last_login, date_joined
    """

    class Papel(models.TextChoices):
        ALUNO = "aluno", "Aluno"
        PROFESSOR = "professor", "Professor"

    papel = models.CharField(
        max_length=20,
        choices=Papel.choices,
        default=Papel.ALUNO,
        verbose_name="Papel",
        help_text="Define o tipo de acesso do usuário no sistema.",
    )

    primeiro_acesso = models.BooleanField(
        default=True,
        verbose_name="Primeiro acesso",
        help_text=(
            "Quando verdadeiro, o usuário é obrigado a trocar a senha "
            "no próximo login. Usado principalmente para professores "
            "cadastrados pelo administrador com senha temporária."
        ),
    )

    identificador_aluno = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Identificador do aluno (Grupo 1)",
        help_text=(
            "Vínculo com o registro do aluno no backend do Grupo 1. "
            "Usado nas chamadas à API, por exemplo /api/desempenho/<id>/. "
            "Deixar em branco para professores."
        ),
    )

    class Tema(models.TextChoices):
        CLARO = "claro", "Claro"
        ESCURO = "escuro", "Escuro"

    tema = models.CharField(
        max_length=10,
        choices=Tema.choices,
        default=Tema.CLARO,
        verbose_name="Tema do site",
        help_text="Aparência escolhida pelo usuário (claro ou escuro).",
    )

    notificacoes_email = models.BooleanField(
        default=True,
        verbose_name="Notificações por e-mail",
        help_text="Receber avisos de novas conquistas, quizzes e atividades por e-mail.",
    )

    class Avatar(models.TextChoices):
        AZUL = "azul", "Azul"
        VERDE = "verde", "Verde"
        ROXO = "roxo", "Roxo"
        LARANJA = "laranja", "Laranja"
        ROSA = "rosa", "Rosa"

    avatar_cor = models.CharField(
        max_length=10,
        choices=Avatar.choices,
        default=Avatar.AZUL,
        verbose_name="Cor do avatar",
        help_text="Cor do círculo com as iniciais exibido na barra lateral.",
    )

    reduzir_animacoes = models.BooleanField(
        default=False,
        verbose_name="Reduzir animações",
        help_text="Desativa transições e animações da interface (acessibilidade).",
    )

    turma_nome = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Turma (professor)",
        help_text="Nome da turma exibido no painel do professor.",
    )

    class Turno(models.TextChoices):
        MANHA = "manha", "Manhã"
        TARDE = "tarde", "Tarde"
        NOITE = "noite", "Noite"
        INTEGRAL = "integral", "Integral"

    turma_turno = models.CharField(
        max_length=10,
        choices=Turno.choices,
        blank=True,
        default="",
        verbose_name="Turno da turma (professor)",
    )

    turma_codigo = models.CharField(
        max_length=30,
        blank=True,
        default="",
        verbose_name="Código da turma (professor)",
        help_text="Código ou identificador interno da turma, se houver.",
    )

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def __str__(self):
        return f"{self.username} ({self.get_papel_display()})"

    @property
    def eh_aluno(self) -> bool:
        """Retorna True se o usuário for aluno."""
        return self.papel == self.Papel.ALUNO

    @property
    def eh_professor(self) -> bool:
        """Retorna True se o usuário for professor."""
        return self.papel == self.Papel.PROFESSOR

    def concluir_primeiro_acesso(self):
        """Marca que o usuário já trocou a senha inicial."""
        self.primeiro_acesso = False
        self.save(update_fields=["primeiro_acesso"])
