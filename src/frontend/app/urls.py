"""
Rotas das janelas do Grupo 2 (Frontend) — conforme o Mapa de Telas.
Este modulo e incluido pelo urls.py do servidor unificado (sti.config.urls),
que ja expoe /admin/ e a API do Grupo 1 (/api/perguntar/, etc.).
"""

from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from frontend.app import views

urlpatterns = [
    # PARTE 1 — Tela inicial
    path("", views.tela_inicial, name="tela_inicial"),

    # PARTE 2 — Aluno
    path("aluno/login/", views.login_aluno, name="login_aluno"),
    path("aluno/cadastro/", views.cadastro_aluno, name="cadastro_aluno"),
    path("aluno/dashboard/", views.dashboard_aluno, name="dashboard_aluno"),
    path("aluno/chat/", views.chat_aluno, name="chat_aluno"),
    path("aluno/chat/perguntar/", views.chat_perguntar_aluno, name="chat_perguntar_aluno"),
    path("aluno/exercicios/", views.exercicios_aluno, name="exercicios_aluno"),
    path("aluno/historico/", views.historico_aluno, name="historico_aluno"),
    path("aluno/quiz/", views.quiz_aluno, name="quiz_aluno"),
    path("aluno/conquistas/", views.conquistas_aluno, name="conquistas_aluno"),
    path("aluno/videoaulas/", views.videoaulas_aluno, name="videoaulas_aluno"),
    path("aluno/configuracoes/", views.configuracoes_aluno, name="configuracoes_aluno"),

    # PARTE 3 — Professor
    path("professor/login/", views.login_professor, name="login_professor"),
    path("professor/primeiro-acesso/", views.primeiro_acesso_professor, name="primeiro_acesso_professor"),
    path("professor/dashboard/", views.dashboard_professor, name="dashboard_professor"),
    path("professor/aluno/<int:aluno_id>/", views.detalhe_aluno, name="detalhe_aluno"),
    path("professor/qa/", views.gestao_qa, name="gestao_qa"),
    path("professor/exercicios/", views.gestao_exercicios, name="gestao_exercicios"),
    path("professor/videoaulas/", views.gestao_videoaulas, name="gestao_videoaulas"),
    path("professor/conteudo/", views.gestao_conteudo, name="gestao_conteudo"),
    path("professor/disciplinas/", views.gestao_disciplinas, name="gestao_disciplinas"),
    path("professor/configuracoes/", views.configuracoes_professor, name="configuracoes_professor"),

    # Troca de senha (primeiro acesso do professor) — views nativas do Django
    path(
        "accounts/password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url=reverse_lazy("password_change_done"),
        ),
        name="password_change",
    ),
    path("accounts/password_change/done/", views.senha_alterada, name="password_change_done"),

    # Sessao
    path("sair/", views.sair, name="sair"),
]
