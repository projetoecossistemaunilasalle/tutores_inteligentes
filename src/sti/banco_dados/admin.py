"""
Admin atualizado com campo usou_rag no historico.
"""

from django.contrib import admin
from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import (
    HistoricoInteracoes,
)
from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import (
    ConteudoAlgoritmos,
)
from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA
from sti.modulo_dominio.exercicios.exercicio import Exercicio
from sti.modulo_dominio.exercicios.gabarito import Gabarito
from sti.banco_dados.models.videoaulas import Videoaula


@admin.register(PerfilAluno)
class PerfilAlunoAdmin(admin.ModelAdmin):
    list_display = (
        "nome", "identificador", "nivel_proficiencia",
        "estado_emocional", "atualizado_em",
    )
    search_fields = ("nome", "identificador")


@admin.register(HistoricoInteracoes)
class HistoricoInteracoesAdmin(admin.ModelAdmin):
    list_display = (
        "aluno", "topico", "origem", "usou_rag", "data_hora",
    )
    list_filter = ("origem", "usou_rag")
    search_fields = ("pergunta", "resposta")


@admin.register(ConteudoAlgoritmos)
class ConteudoAlgoritmosAdmin(admin.ModelAdmin):
    list_display = ("titulo", "nivel", "ordem", "ativo")
    list_filter = ("nivel", "ativo")
    search_fields = ("titulo", "descricao")


@admin.register(RepositorioQA)
class RepositorioQAAdmin(admin.ModelAdmin):
    list_display = ("topico", "ativo", "atualizado_em")
    list_filter = ("ativo",)
    search_fields = ("pergunta", "resposta")


@admin.register(Exercicio)
class ExercicioAdmin(admin.ModelAdmin):
    list_display = ("topico", "nivel", "ativo")
    list_filter = ("nivel", "ativo")
    search_fields = ("enunciado",)


@admin.register(Gabarito)
class GabaritoAdmin(admin.ModelAdmin):
    list_display = ("exercicio", "atualizado_em")
    search_fields = ("resposta_correta",)


@admin.register(Videoaula)
class VideoaulaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "topico", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("titulo", "descricao")
