"""
Registra os modelos do Grupo 2 no Admin do Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from frontend.app.models.usuarios import Usuario
from frontend.app.models.disciplina import Disciplina, Licao
from frontend.app.models.conversas import Conversa, Mensagem
from frontend.app.models.quizzes import (
    Quiz, Questao, Alternativa,
    TentativaQuiz, RespostaQuiz,
)
from frontend.app.models.progresso import (
    ProgressoLicao, NivelUsuario,
    Conquista, ConquistaUsuario, Notificacao,
)
from frontend.app.models.videoaulas import Videoaula


# --- Usuarios ---
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "papel", "ativo")
    list_filter = ("papel", "ativo")


# --- Conteudo ---
@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ordem", "ativa")
    search_fields = ("nome",)


@admin.register(Licao)
class LicaoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "disciplina", "ordem", "ativa")
    list_filter = ("disciplina",)


@admin.register(Videoaula)
class VideoaulaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "disciplina", "licao", "ativa")
    list_filter = ("disciplina",)


# --- Interacao ---
@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario", "disciplina", "total_mensagens", "iniciada_em",
    )


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ("conversa", "papel", "enviado_em")
    list_filter = ("papel",)


# --- Avaliacao ---
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("titulo", "disciplina", "total_questoes", "ativo")
    list_filter = ("ativo",)


@admin.register(Questao)
class QuestaoAdmin(admin.ModelAdmin):
    list_display = ("quiz", "tipo", "ordem")
    list_filter = ("tipo",)


@admin.register(Alternativa)
class AlternativaAdmin(admin.ModelAdmin):
    list_display = ("questao", "correta", "ordem")
    list_filter = ("correta",)


@admin.register(TentativaQuiz)
class TentativaQuizAdmin(admin.ModelAdmin):
    list_display = ("usuario", "quiz", "pontuacao", "iniciado_em")


@admin.register(RespostaQuiz)
class RespostaQuizAdmin(admin.ModelAdmin):
    list_display = ("tentativa", "questao", "correta")
    list_filter = ("correta",)


# --- Progresso ---
@admin.register(ProgressoLicao)
class ProgressoLicaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "licao", "concluida", "xp_ganho")
    list_filter = ("concluida",)


@admin.register(NivelUsuario)
class NivelUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nivel", "xp_total", "streak_dias")


@admin.register(Conquista)
class ConquistaAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "xp_bonus")
    search_fields = ("nome", "codigo")


@admin.register(ConquistaUsuario)
class ConquistaUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "conquista", "ganho_em")


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "titulo", "lida", "criado_em")
    list_filter = ("lida",)
