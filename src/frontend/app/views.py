"""Views de acesso do Grupo 2 — tela inicial, login e cadastro."""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from frontend.app.models.usuarios import Usuario


def tela_inicial(request):
    """Porta de entrada: Aluno, Professor ou Admin."""
    return render(request, "tela_inicial.html")


def login_aluno(request):
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if usuario is None:
            messages.error(request, "Usuário ou senha inválidos.")
        elif not usuario.eh_aluno:
            messages.error(request, "Esta conta não é de aluno.")
        else:
            login(request, usuario)
            return redirect("dashboard_aluno")
    return render(request, "aluno/login.html")


def cadastro_aluno(request):
    """Cadastro público. O papel é sempre 'aluno'."""
    if request.method != "POST":
        return render(request, "aluno/cadastro.html")

    username = request.POST.get("username", "").strip()
    senha = request.POST.get("password", "")
    senha2 = request.POST.get("password2", "")

    if not username or not senha:
        messages.error(request, "Preencha usuário e senha.")
    elif senha != senha2:
        messages.error(request, "As senhas não conferem.")
    elif Usuario.objects.filter(username=username).exists():
        messages.error(request, "Este nome de usuário já existe.")
    else:
        usuario = Usuario(
            username=username,
            email=request.POST.get("email", "").strip(),
            first_name=request.POST.get("first_name", "").strip(),
            papel="aluno",
            primeiro_acesso=False,
            identificador_aluno=username,
        )
        usuario.set_password(senha)
        usuario.save()
        login(request, usuario)
        return redirect("dashboard_aluno")

    return render(request, "aluno/cadastro.html")


def login_professor(request):
    """Login do professor. Sem cadastro público."""
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if usuario is None:
            messages.error(request, "Usuário ou senha inválidos.")
        elif not usuario.eh_professor:
            messages.error(request, "Esta conta não é de professor.")
        else:
            login(request, usuario)
            return redirect("primeiro_acesso_professor")
    return render(request, "professor/login.html")


@login_required
def primeiro_acesso_professor(request):
    """Obriga a troca da senha temporária no primeiro acesso."""
    if request.user.primeiro_acesso:
        messages.info(request, "Defina uma nova senha para continuar.")
        return redirect("password_change")
    return redirect("dashboard_professor")


@login_required
def senha_alterada(request):
    """Chamada após a troca de senha: encerra o primeiro acesso."""
    if request.user.primeiro_acesso:
        request.user.primeiro_acesso = False
        request.user.save(update_fields=["primeiro_acesso"])
    return redirect("dashboard_professor")


def sair(request):
    logout(request)
    return redirect("tela_inicial")


# --- Placeholders: substituir pelas telas reais do Leonardo ---

@login_required
def dashboard_aluno(request):
    return render(request, "aluno/dashboard.html")


@login_required
def dashboard_professor(request):
    return render(request, "professor/dashboard.html")
