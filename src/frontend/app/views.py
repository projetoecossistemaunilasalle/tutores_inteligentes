"""
Views do Grupo 2 (Frontend) — todas as janelas do Mapa de Telas.

Padrao de cada tela: HTML + VIEW + MODEL + GET + POST.
O controle de acesso fica aqui (decorators), nao no HTML.

Banco unificado: as classes do Grupo 1 (app 'banco_dados') sao acessadas
direto pelo ORM. A API so e necessaria para o chat (/api/perguntar/),
porque ela aciona o motor de IA.
"""

from functools import wraps
import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

# --- Models do Grupo 2 (frontend.app) ---
from frontend.app.models.usuarios import Usuario
from frontend.app.models.disciplina import Disciplina, Licao
from frontend.app.models.conversas import Conversa, Mensagem
from frontend.app.models.progresso import (
    NivelUsuario, ProgressoLicao, Conquista, ConquistaUsuario, Notificacao,
)
from frontend.app.models.quizzes import (
    Quiz, Questao, Alternativa, TentativaQuiz, RespostaQuiz,
)
from frontend.app.models.videoaulas import Videoaula
from frontend.app.models.exercicios_resp import RespostaExercicio

# --- Models do Grupo 1 (sti / app 'banco_dados') — import tolerante ---
try:
    from sti.modulo_dominio.exercicios.exercicio import Exercicio
    from sti.modulo_dominio.exercicios.gabarito import Gabarito
    from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import ConteudoAlgoritmos
    from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA
    from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
    from sti.modulo_aluno.historico.historico_interacoes import HistoricoInteracoes
    STI_OK = True
except Exception:  # pragma: no cover - ambiente sem o app do Grupo 1
    Exercicio = Gabarito = ConteudoAlgoritmos = RepositorioQA = None
    PerfilAluno = HistoricoInteracoes = None
    STI_OK = False


# ══════════════════════════════════════════════════════════════════════
# Utilitarios
# ══════════════════════════════════════════════════════════════════════
def professor_required(view):
    """Garante que o usuario logado e professor."""
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.eh_professor:
            messages.error(request, "Area exclusiva de professores.")
            return redirect("dashboard_aluno")
        return view(request, *args, **kwargs)
    return wrapper


def aluno_required(view):
    @wraps(view)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.eh_aluno:
            messages.error(request, "Area exclusiva de alunos.")
            return redirect("dashboard_professor")
        return view(request, *args, **kwargs)
    return wrapper


def _iniciais(user):
    base = (user.first_name or user.username or "?").strip()
    partes = base.split()
    if len(partes) >= 2:
        return (partes[0][0] + partes[1][0]).upper()
    return base[:2].upper()


def _nivel_do(user):
    nivel, _ = NivelUsuario.objects.get_or_create(usuario=user)
    return nivel


def _aluno_id(user):
    """Identificador usado nas chamadas a API do Grupo 1."""
    return user.identificador_aluno or user.username


def _garantir_perfil_grupo1(user):
    """Garante que o aluno tem um PerfilAluno no Grupo 1 (STI).
    Sem isso, o motor de IA não encontra o aluno e falha.
    Cria o perfil automaticamente se ainda não existir."""
    if not STI_OK:
        return None
    aluno_id = _aluno_id(user)
    perfil, _ = PerfilAluno.objects.get_or_create(
        identificador=aluno_id,
        defaults=dict(
            nome=user.first_name or user.username,
            nivel_proficiencia="iniciante",
        ),
    )
    return perfil


def conceder_xp(nivel, quantidade):
    """Soma XP ao usuário e sobe de nível quando o contador zera.
    xp_proximo_nivel funciona como uma contagem regressiva até o
    próximo nível (não é um total acumulado)."""
    if quantidade <= 0:
        return False
    nivel.xp_total += quantidade
    faltante = nivel.xp_proximo_nivel - quantidade
    subiu = False
    while faltante <= 0:
        nivel.nivel += 1
        subiu = True
        custo_proximo = 100 + nivel.nivel * 20
        faltante += custo_proximo
    nivel.xp_proximo_nivel = max(faltante, 1)
    return subiu


def atualizar_streak(nivel):
    """Atualiza a sequência de dias de estudo do aluno."""
    hoje = timezone.localdate()
    if nivel.ultima_atividade == hoje:
        return
    ontem = hoje - timedelta(days=1)
    if nivel.ultima_atividade == ontem:
        nivel.streak_dias += 1
    else:
        nivel.streak_dias = 1
    nivel.ultima_atividade = hoje


def desbloquear_conquista(usuario, nivel, codigo):
    """Desbloqueia uma conquista pelo código, se ainda não desbloqueada.
    Concede o XP de bônus e cria uma notificação. Idempotente — pode
    ser chamada quantas vezes for preciso, só desbloqueia uma vez.
    Retorna a Conquista se foi desbloqueada agora, ou None."""
    ja_tem = ConquistaUsuario.objects.filter(
        usuario=usuario, conquista__codigo=codigo
    ).exists()
    if ja_tem:
        return None
    conquista = Conquista.objects.filter(codigo=codigo).first()
    if not conquista:
        return None
    ConquistaUsuario.objects.create(usuario=usuario, conquista=conquista)
    if nivel is not None and conquista.xp_bonus:
        conceder_xp(nivel, conquista.xp_bonus)
    Notificacao.objects.create(
        usuario=usuario, tipo="conquista",
        titulo="Nova conquista desbloqueada!",
        corpo=f"Você ganhou '{conquista.nome}'. +{conquista.xp_bonus} XP.",
    )
    return conquista


def verificar_conquistas(usuario, nivel):
    """Verifica todas as condições de conquista do sistema e desbloqueia
    as que o aluno já atende, concedendo XP de bônus e notificando.
    Cada condição é computada a partir de dados reais (mensagens,
    lições concluídas, tentativas de quiz, exercícios corretos, nível
    e XP acumulado) — nada aqui é decorativo."""
    ja_desbloqueadas = set(
        ConquistaUsuario.objects.filter(usuario=usuario)
        .values_list("conquista__codigo", flat=True)
    )

    total_perguntas = Mensagem.objects.filter(
        conversa__usuario=usuario, papel="aluno"
    ).count()
    total_licoes_concluidas = ProgressoLicao.objects.filter(
        usuario=usuario, concluida=True
    ).count()
    total_licoes_ativas = Licao.objects.filter(ativa=True).count()
    tentativas_quiz = TentativaQuiz.objects.filter(
        usuario=usuario, concluido_em__isnull=False
    )
    total_quizzes_100 = tentativas_quiz.filter(pontuacao=100).count()
    total_exercicios_corretos = RespostaExercicio.objects.filter(
        usuario=usuario, correta=True
    ).count()
    total_exercicios_ativos = Exercicio.objects.filter(ativo=True).count() if STI_OK else 0

    # codigo -> True/False (condição atendida agora)
    condicoes = {
        "primeira_pergunta": total_perguntas >= 1,
        "primeiro_quiz": tentativas_quiz.exists(),
        "perfil_completo": bool(usuario.first_name) and bool(usuario.email),

        "streak3": nivel.streak_dias >= 3,
        "streak5": nivel.streak_dias >= 5,
        "streak7": nivel.streak_dias >= 7,
        "streak15": nivel.streak_dias >= 15,
        "streak30": nivel.streak_dias >= 30,

        "perguntas10": total_perguntas >= 10,
        "perguntas50": total_perguntas >= 50,
        "perguntas100": total_perguntas >= 100,

        "primeira_licao": total_licoes_concluidas >= 1,
        "maratonista": total_licoes_ativas > 0 and total_licoes_concluidas >= total_licoes_ativas,

        "quiz_ace": total_quizzes_100 >= 1,
        "quiz_veterano": tentativas_quiz.count() >= 5,
        "quiz_perfeccionista": total_quizzes_100 >= 3,

        "primeiro_exercicio": RespostaExercicio.objects.filter(usuario=usuario).exists(),
        "exercicios10": total_exercicios_corretos >= 10,
        "exercicios25": total_exercicios_corretos >= 25,
        "gabarito_mestre": total_exercicios_ativos > 0 and total_exercicios_corretos >= total_exercicios_ativos,

        "nivel5": nivel.nivel >= 5,
        "nivel10": nivel.nivel >= 10,
        "xp1000": nivel.xp_total >= 1000,
        "xp5000": nivel.xp_total >= 5000,
    }

    novas = []
    for codigo, atingida in condicoes.items():
        if not atingida or codigo in ja_desbloqueadas:
            continue
        conquista = desbloquear_conquista(usuario, nivel, codigo)
        if conquista:
            novas.append(conquista)
    return novas


def _licao_atual(disciplina):
    """Primeira lição ativa da disciplina, na ordem — a mesma lição
    que a tela de chat mostra como 'aula atual'."""
    if not disciplina:
        return None
    return disciplina.licoes.filter(ativa=True).order_by("ordem").first()


def avancar_progresso_licao(usuario, licao, nivel):
    """Avança uma etapa na lição atual a cada interação com o tutor.
    Ao concluir todas as etapas, marca a lição como concluída e dá
    um bônus de XP. Retorna o ProgressoLicao atualizado (ou None)."""
    if not licao:
        return None
    progresso, _ = ProgressoLicao.objects.get_or_create(usuario=usuario, licao=licao)
    if progresso.concluida:
        return progresso
    progresso.etapa_atual = min(progresso.etapa_atual + 1, licao.total_etapas)
    if progresso.etapa_atual >= licao.total_etapas:
        progresso.concluida = True
        progresso.concluido_em = timezone.now()
        progresso.xp_ganho = 20
        conceder_xp(nivel, 20)
    progresso.save()
    return progresso


AVATAR_GRADIENTES = {
    "azul": "linear-gradient(135deg,#0066ff,#00aeff)",
    "verde": "linear-gradient(135deg,#16a34a,#4ade80)",
    "roxo": "linear-gradient(135deg,#7c3aed,#c084fc)",
    "laranja": "linear-gradient(135deg,#ea580c,#fb923c)",
    "rosa": "linear-gradient(135deg,#db2777,#f472b6)",
}


def base_ctx(request, active_nav):
    """Contexto comum ao shell (sidebar + topbar)."""
    ctx = {
        "active_nav": active_nav,
        "disciplinas": list(Disciplina.objects.filter(ativa=True)),
        "avatar_iniciais": _iniciais(request.user),
        "avatar_cor": AVATAR_GRADIENTES.get(request.user.avatar_cor, AVATAR_GRADIENTES["azul"]),
    }
    if request.user.eh_aluno:
        nivel = _nivel_do(request.user)
        total = nivel.xp_total + max(1, nivel.xp_proximo_nivel)
        ctx.update({
            "nivel": nivel,
            "xp_pct": min(100, int(nivel.xp_total * 100 / total)),
            "xp_faltante": nivel.xp_proximo_nivel,
            "proximo_nivel": nivel.nivel + 1,
        })
    else:
        ctx["turma_nome"] = request.user.turma_nome or "Turma"
    return ctx


# ══════════════════════════════════════════════════════════════════════
# PARTE 1 — TELA INICIAL
# ══════════════════════════════════════════════════════════════════════
def tela_inicial(request):
    """Porta de entrada: Aluno, Professor ou Admin.  URL: /"""
    if request.user.is_authenticated:
        return redirect("dashboard_professor" if request.user.eh_professor else "dashboard_aluno")
    return render(request, "tela_inicial.html")


# ══════════════════════════════════════════════════════════════════════
# PARTE 2 — TELAS DO ALUNO
# ══════════════════════════════════════════════════════════════════════
def login_aluno(request):
    """URL: /aluno/login/"""
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if usuario is None:
            messages.error(request, "Usuario ou senha invalidos.")
        elif not usuario.eh_aluno:
            messages.error(request, "Esta conta nao e de aluno.")
        else:
            primeiro_login = usuario.last_login is None
            login(request, usuario)
            if primeiro_login:
                nivel = _nivel_do(usuario)
                desbloquear_conquista(usuario, nivel, "primeiro_login")
                nivel.save()
            return redirect("dashboard_aluno")
    return render(request, "aluno/login.html")


def cadastro_aluno(request):
    """Cadastro publico. O papel e sempre 'aluno'.  URL: /aluno/cadastro/"""
    if request.method != "POST":
        return render(request, "aluno/cadastro.html")

    username = request.POST.get("username", "").strip()
    senha = request.POST.get("password", "")
    senha2 = request.POST.get("password2", "")

    if not username or not senha:
        messages.error(request, "Preencha usuario e senha.")
    elif senha != senha2:
        messages.error(request, "As senhas nao conferem.")
    elif Usuario.objects.filter(username=username).exists():
        messages.error(request, "Este nome de usuario ja existe.")
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
        NivelUsuario.objects.get_or_create(usuario=usuario)
        _garantir_perfil_grupo1(usuario)
        login(request, usuario)
        nivel = _nivel_do(usuario)
        desbloquear_conquista(usuario, nivel, "primeiro_login")
        nivel.save()
        messages.success(request, "Conta criada com sucesso. Bem-vindo!")
        return redirect("dashboard_aluno")

    return render(request, "aluno/cadastro.html")


@aluno_required
def dashboard_aluno(request):
    """URL: /aluno/dashboard/"""
    nivel = _nivel_do(request.user)
    progressos = list(
        ProgressoLicao.objects.filter(usuario=request.user)
        .select_related("licao", "licao__disciplina")
    )
    for p in progressos:
        total = max(1, p.licao.total_etapas)
        p.pct = min(100, int(p.etapa_atual * 100 / total))

    ctx = base_ctx(request, "dashboard")
    ctx.update({
        "progressos": progressos,
        "licoes_concluidas": sum(1 for p in progressos if p.concluida),
        "licoes_andamento": sum(1 for p in progressos if not p.concluida),
        "conquistas_total": ConquistaUsuario.objects.filter(usuario=request.user).count(),
        "desempenho_resumo": None,
    })
    return render(request, "aluno/dashboard.html", ctx)


@aluno_required
def chat_aluno(request):
    """Chat com o tutor. O envio real vai para /api/perguntar/ (Grupo 1).
    URL: /aluno/chat/"""
    disciplina = None
    did = request.GET.get("disciplina")
    if did:
        disciplina = Disciplina.objects.filter(id=did, ativa=True).first()
    if disciplina is None:
        disciplina = Disciplina.objects.filter(ativa=True).first()

    licao = None
    licao_total = 1
    licao_ordem = 1
    if disciplina:
        licoes = list(disciplina.licoes.filter(ativa=True))
        licao_total = max(1, len(licoes))
        licao = licoes[0] if licoes else None
        if licao:
            licao_ordem = licao.ordem or 1
            licao_total = max(1, licao.total_etapas)

    conversa = (
        Conversa.objects.filter(usuario=request.user, disciplina=disciplina)
        .order_by("-iniciada_em").first()
    )
    mensagens = list(conversa.mensagens.all()) if conversa else []

    ctx = base_ctx(request, "chat")
    ctx.update({
        "disciplina": disciplina,
        "disciplina_ativa_id": disciplina.id if disciplina else None,
        "licao": licao,
        "licao_ordem": licao_ordem,
        "licao_total": licao_total,
        "mensagens": mensagens,
        "aluno_id": _aluno_id(request.user),
    })
    return render(request, "aluno/chat.html", ctx)


@aluno_required
@require_POST
def chat_perguntar_aluno(request):
    """Ponte entre o chat (Grupo 2) e o motor de IA real (Grupo 1).

    Chama sti.motor_ia.motor_decisao.orquestrador.responder() — a IA
    de verdade (regras + Q&A + RAG + LLM) — grava a conversa para o
    histórico do chat e concede XP/streak/conquistas pela interação.

    URL: POST /aluno/chat/perguntar/
    """
    if not STI_OK:
        return JsonResponse(
            {"erro": "O motor de IA (Grupo 1) não está instalado neste ambiente."},
            status=503,
        )

    try:
        dados = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"erro": "Requisição inválida."}, status=400)

    pergunta = (dados.get("pergunta") or "").strip()
    if not pergunta:
        return JsonResponse({"erro": "Digite uma pergunta."}, status=400)

    disciplina_id = dados.get("disciplina_id")
    disciplina = Disciplina.objects.filter(id=disciplina_id).first() if disciplina_id else None

    # Garante que o aluno existe no Grupo 1 antes de perguntar.
    _garantir_perfil_grupo1(request.user)
    aluno_id = _aluno_id(request.user)

    try:
        from sti.motor_ia.motor_decisao.orquestrador import responder
    except Exception as e:
        return JsonResponse(
            {"erro": (
                "O motor de IA não pôde ser carregado. Verifique se as "
                f"dependências estão instaladas (pip install -r requirements.txt). Detalhe: {e}"
            )},
            status=503,
        )

    try:
        resultado = responder(pergunta, aluno_id)
    except ObjectDoesNotExist:
        return JsonResponse(
            {"erro": "Perfil do aluno não encontrado no motor de IA."}, status=404
        )
    except Exception as e:
        return JsonResponse(
            {"erro": f"O motor de IA não conseguiu responder agora ({e})."},
            status=502,
        )

    resposta_txt = resultado.get("resposta") or "Não consegui gerar uma resposta agora."

    # --- Persiste a conversa (Grupo 2), para exibir no histórico do chat ---
    conversa = (
        Conversa.objects.filter(
            usuario=request.user, disciplina=disciplina, encerrada_em__isnull=True
        )
        .order_by("-iniciada_em")
        .first()
    )
    if not conversa:
        conversa = Conversa.objects.create(
            usuario=request.user, disciplina=disciplina,
            titulo=disciplina.nome if disciplina else "Conversa com o tutor",
        )
    Mensagem.objects.create(conversa=conversa, papel="aluno", conteudo=pergunta)
    Mensagem.objects.create(conversa=conversa, papel="tutor", conteudo=resposta_txt)
    conversa.total_mensagens = conversa.mensagens.count()
    conversa.save(update_fields=["total_mensagens"])

    # --- Gamificação: XP, sequência de dias, progresso da lição e conquistas ---
    nivel = _nivel_do(request.user)
    subiu_de_nivel = conceder_xp(nivel, 5)
    atualizar_streak(nivel)

    licao = _licao_atual(disciplina)
    progresso = avancar_progresso_licao(request.user, licao, nivel)

    nivel.save()
    novas_conquistas = verificar_conquistas(request.user, nivel)
    nivel.save()

    return JsonResponse({
        "resposta": resposta_txt,
        "fontes": resultado.get("fontes", []),
        "usou_rag": resultado.get("usou_rag", False),
        "xp_ganho": 5,
        "xp_total": nivel.xp_total,
        "nivel": nivel.nivel,
        "xp_proximo_nivel": nivel.xp_proximo_nivel,
        "streak_dias": nivel.streak_dias,
        "subiu_de_nivel": subiu_de_nivel,
        "etapa_atual": progresso.etapa_atual if progresso else None,
        "licao_total": licao.total_etapas if licao else None,
        "licao_concluida": bool(progresso and progresso.concluida),
        "conquistas_novas": [
            {"nome": c.nome, "icone": c.icone, "xp_bonus": c.xp_bonus}
            for c in novas_conquistas
        ],
    })


@aluno_required
def exercicios_aluno(request):
    """Lista exercicios do topico e corrige pela resposta do gabarito.
    A resposta de cada aluno fica salva (RespostaExercicio), então o
    feedback persiste entre visitas e alimenta as conquistas de exercícios.
    URL: /aluno/exercicios/"""
    ctx = base_ctx(request, "exercicios")
    if not STI_OK:
        ctx.update({"topicos": [], "exercicios": [], "topico": None})
        return render(request, "aluno/exercicios.html", ctx)

    topicos = list(ConteudoAlgoritmos.objects.filter(ativo=True))
    tid = request.GET.get("topico")
    topico = ConteudoAlgoritmos.objects.filter(id=tid).first() if tid else None

    qs = Exercicio.objects.filter(ativo=True)
    if topico:
        qs = qs.filter(topico=topico)
    exercicios = list(qs.select_related("gabarito", "topico"))

    if request.method == "POST":
        ex_id = request.POST.get("exercicio_id")
        resposta = request.POST.get("resposta", "").strip()
        for ex in exercicios:
            if str(ex.id) != str(ex_id):
                continue
            gab = getattr(ex, "gabarito", None)
            if not gab:
                continue
            correta = resposta.lower() == gab.resposta_correta.strip().lower()

            anterior = RespostaExercicio.objects.filter(usuario=request.user, exercicio=ex).first()
            ja_estava_correta = bool(anterior and anterior.correta)

            if anterior:
                anterior.resposta = resposta
                anterior.correta = correta
                anterior.tentativas += 1
                anterior.save()
            else:
                RespostaExercicio.objects.create(
                    usuario=request.user, exercicio=ex, resposta=resposta, correta=correta,
                )

            # Só concede XP na primeira vez que o aluno acerta este exercício,
            # para não permitir reenviar a mesma resposta em loop por XP.
            if correta and not ja_estava_correta:
                nivel = _nivel_do(request.user)
                conceder_xp(nivel, 8)
                atualizar_streak(nivel)
                nivel.save()
                verificar_conquistas(request.user, nivel)
                nivel.save()

    # Hidrata cada exercício com a última resposta salva deste aluno
    # (funciona tanto após o POST acima quanto num GET normal).
    respostas = {
        r.exercicio_id: r
        for r in RespostaExercicio.objects.filter(
            usuario=request.user, exercicio__in=exercicios
        )
    }
    for ex in exercicios:
        r = respostas.get(ex.id)
        ex.gabarito = getattr(ex, "gabarito", None)
        ex.feedback = r is not None
        ex.resposta_enviada = r.resposta if r else ""
        ex.acertou = r.correta if r else False

    ctx.update({"topicos": topicos, "exercicios": exercicios, "topico": topico})
    return render(request, "aluno/exercicios.html", ctx)


@aluno_required
def historico_aluno(request):
    """Lista as interacoes do aluno (Grupo 1).  URL: /aluno/historico/"""
    ctx = base_ctx(request, "historico")
    interacoes = []
    if STI_OK:
        perfil = PerfilAluno.objects.filter(identificador=_aluno_id(request.user)).first()
        if perfil:
            interacoes = list(perfil.interacoes.all()[:50])
    ctx["interacoes"] = interacoes
    return render(request, "aluno/historico.html", ctx)


@aluno_required
def quiz_aluno(request):
    """Carrega questoes/alternativas e grava a tentativa.  URL: /aluno/quiz/"""
    ctx = base_ctx(request, "quiz")
    qid = request.GET.get("quiz")
    quiz = Quiz.objects.filter(id=qid, ativo=True).first() if qid else None

    if quiz and request.method == "POST":
        questoes = list(quiz.questoes.prefetch_related("alternativas"))
        acertos = 0
        tentativa = TentativaQuiz.objects.create(
            usuario=request.user, quiz=quiz, total=len(questoes),
        )
        for q in questoes:
            alt_id = request.POST.get(f"q_{q.id}")
            alt = Alternativa.objects.filter(id=alt_id, questao=q).first() if alt_id else None
            correta = bool(alt and alt.correta)
            acertos += 1 if correta else 0
            RespostaQuiz.objects.create(
                tentativa=tentativa, questao=q, alternativa=alt, correta=correta,
            )
        pont = round(acertos * 100 / max(1, len(questoes)), 2)
        xp = acertos * 10
        tentativa.acertos = acertos
        tentativa.pontuacao = pont
        tentativa.xp_ganho = xp
        tentativa.concluido_em = timezone.now()
        tentativa.save()

        nivel = _nivel_do(request.user)
        conceder_xp(nivel, xp)
        atualizar_streak(nivel)
        nivel.save()
        verificar_conquistas(request.user, nivel)
        nivel.save()

        ctx.update({
            "quiz": quiz,
            "questoes": [],
            "resultado": {"acertos": acertos, "total": len(questoes),
                          "pontuacao": pont, "xp_ganho": xp},
        })
        return render(request, "aluno/quiz.html", ctx)

    if quiz:
        ctx.update({"quiz": quiz, "questoes": list(quiz.questoes.prefetch_related("alternativas"))})
    else:
        ctx.update({"quiz": None, "quizzes": list(Quiz.objects.filter(ativo=True))})
    return render(request, "aluno/quiz.html", ctx)


@aluno_required
def conquistas_aluno(request):
    """Lista conquistas (agrupadas por categoria) e notificacoes.
    URL: /aluno/conquistas/"""
    if request.method == "POST":
        nid = request.POST.get("notificacao_id")
        n = Notificacao.objects.filter(id=nid, usuario=request.user).first()
        if n:
            n.lida = True
            n.lida_em = timezone.now()
            n.save(update_fields=["lida", "lida_em"])
        return redirect("conquistas_aluno")

    desbloqueadas = set(
        ConquistaUsuario.objects.filter(usuario=request.user)
        .values_list("conquista_id", flat=True)
    )
    conquistas = list(Conquista.objects.all().order_by("categoria", "xp_bonus"))
    for c in conquistas:
        c.desbloqueada = c.id in desbloqueadas

    rotulos = dict(Conquista.Categoria.choices)
    ordem_categorias = [
        "inicio", "consistencia", "conversas", "licoes",
        "quizzes", "exercicios", "progressao", "geral",
    ]
    por_categoria = {cat: [] for cat in ordem_categorias}
    for c in conquistas:
        por_categoria.setdefault(c.categoria, []).append(c)
    grupos = [
        {"label": rotulos.get(cat, cat), "itens": itens,
         "total": len(itens), "desbloqueadas": sum(1 for i in itens if i.desbloqueada)}
        for cat, itens in por_categoria.items() if itens
    ]

    ctx = base_ctx(request, "conquistas")
    ctx.update({
        "grupos_conquistas": grupos,
        "conquistas_total": len(conquistas),
        "conquistas_desbloqueadas": len(desbloqueadas),
        "notificacoes": list(Notificacao.objects.filter(usuario=request.user)[:20]),
    })
    return render(request, "aluno/conquistas.html", ctx)


@aluno_required
def videoaulas_aluno(request):
    """Lista as videoaulas ativas.  URL: /aluno/videoaulas/"""
    ctx = base_ctx(request, "videoaulas")
    ctx["videoaulas"] = list(
        Videoaula.objects.filter(ativa=True).select_related("disciplina")
    )
    return render(request, "aluno/videoaulas.html", ctx)


# ══════════════════════════════════════════════════════════════════════
# PARTE 3 — TELAS DO PROFESSOR
# ══════════════════════════════════════════════════════════════════════
def login_professor(request):
    """URL: /professor/login/"""
    if request.method == "POST":
        usuario = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if usuario is None:
            messages.error(request, "Usuario ou senha invalidos.")
        elif not usuario.eh_professor:
            messages.error(request, "Esta conta nao e de professor.")
        else:
            login(request, usuario)
            return redirect("primeiro_acesso_professor")
    return render(request, "professor/login.html")


@login_required
def primeiro_acesso_professor(request):
    """Obriga a troca da senha temporaria no primeiro acesso."""
    if request.user.primeiro_acesso:
        messages.info(request, "Defina uma nova senha para continuar.")
        return redirect("password_change")
    return redirect("dashboard_professor")


@login_required
def senha_alterada(request):
    """Chamada apos a troca de senha: encerra o primeiro acesso."""
    if getattr(request.user, "primeiro_acesso", False):
        request.user.primeiro_acesso = False
        request.user.save(update_fields=["primeiro_acesso"])
    messages.success(request, "Senha atualizada.")
    return redirect("dashboard_professor")


@professor_required
def dashboard_professor(request):
    """Metricas gerais da turma.  URL: /professor/dashboard/"""
    ctx = base_ctx(request, "dashboard")
    alunos = []
    total_interacoes = 0
    if STI_OK:
        alunos = list(PerfilAluno.objects.all())
        for a in alunos:
            a.num_interacoes = a.interacoes.count()
            total_interacoes += a.num_interacoes
    ctx.update({
        "alunos": alunos,
        "total_alunos": len(alunos),
        "total_interacoes": total_interacoes,
        "total_exercicios": Exercicio.objects.filter(ativo=True).count() if STI_OK else 0,
        "total_videoaulas": Videoaula.objects.filter(ativa=True).count(),
    })
    return render(request, "professor/dashboard.html", ctx)


@professor_required
def detalhe_aluno(request, aluno_id):
    """Perfil, nivel e historico do aluno.  URL: /professor/aluno/<id>/"""
    ctx = base_ctx(request, "dashboard")
    if not STI_OK:
        messages.error(request, "Modulo do aluno (Grupo 1) indisponivel.")
        return redirect("dashboard_professor")
    perfil = get_object_or_404(PerfilAluno, id=aluno_id)
    ctx.update({"perfil": perfil, "interacoes": list(perfil.interacoes.all()[:30])})
    return render(request, "professor/aluno_detalhe.html", ctx)


@professor_required
def gestao_qa(request):
    """Lista e cria registros de Q&A.  URL: /professor/qa/"""
    ctx = base_ctx(request, "qa")
    if not STI_OK:
        ctx.update({"registros": [], "topicos": []})
        return render(request, "professor/qa.html", ctx)

    if request.method == "POST":
        tid = request.POST.get("topico")
        RepositorioQA.objects.create(
            pergunta=request.POST.get("pergunta", "").strip(),
            resposta=request.POST.get("resposta", "").strip(),
            topico=ConteudoAlgoritmos.objects.filter(id=tid).first() if tid else None,
            palavras_chave=request.POST.get("palavras_chave", "").strip(),
        )
        messages.success(request, "Q&A cadastrado.")
        return redirect("gestao_qa")

    ctx.update({
        "registros": list(RepositorioQA.objects.filter(ativo=True).select_related("topico")),
        "topicos": list(ConteudoAlgoritmos.objects.filter(ativo=True)),
    })
    return render(request, "professor/qa.html", ctx)


@professor_required
def gestao_exercicios(request):
    """Lista/cria exercicio + gabarito.  URL: /professor/exercicios/"""
    ctx = base_ctx(request, "exercicios")
    if not STI_OK:
        ctx.update({"exercicios": [], "topicos": []})
        return render(request, "professor/exercicios.html", ctx)

    if request.method == "POST":
        tid = request.POST.get("topico")
        ex = Exercicio.objects.create(
            enunciado=request.POST.get("enunciado", "").strip(),
            topico=ConteudoAlgoritmos.objects.filter(id=tid).first() if tid else None,
            nivel=request.POST.get("nivel", "iniciante"),
        )
        Gabarito.objects.create(
            exercicio=ex,
            resposta_correta=request.POST.get("resposta_correta", "").strip(),
            explicacao=request.POST.get("explicacao", "").strip(),
        )
        messages.success(request, "Exercicio cadastrado.")
        return redirect("gestao_exercicios")

    ctx.update({
        "exercicios": list(Exercicio.objects.filter(ativo=True).select_related("gabarito", "topico")),
        "topicos": list(ConteudoAlgoritmos.objects.filter(ativo=True)),
    })
    return render(request, "professor/exercicios.html", ctx)


@professor_required
def gestao_videoaulas(request):
    """Lista/cadastra/exclui videoaulas.  URL: /professor/videoaulas/"""
    if request.method == "POST":
        if request.POST.get("acao") == "excluir":
            v = Videoaula.objects.filter(id=request.POST.get("videoaula_id")).first()
            if v:
                v.delete()
                messages.success(request, "Videoaula removida.")
            return redirect("gestao_videoaulas")

        dur = request.POST.get("duracao_minutos") or 0
        did = request.POST.get("disciplina")
        Videoaula.objects.create(
            titulo=request.POST.get("titulo", "").strip(),
            url_youtube=request.POST.get("url_youtube", "").strip(),
            descricao=request.POST.get("descricao", "").strip(),
            duracao_minutos=int(dur),
            disciplina=Disciplina.objects.filter(id=did).first() if did else None,
            cadastrado_por=request.user,
        )
        messages.success(request, "Videoaula cadastrada.")
        return redirect("gestao_videoaulas")

    ctx = base_ctx(request, "videoaulas")
    ctx.update({
        "videoaulas": list(Videoaula.objects.select_related("disciplina")),
        "disciplinas": list(Disciplina.objects.filter(ativa=True)),
    })
    return render(request, "professor/videoaulas.html", ctx)


@professor_required
def gestao_conteudo(request):
    """Lista/cria conteudo por nivel.  URL: /professor/conteudo/"""
    ctx = base_ctx(request, "conteudo")
    if not STI_OK:
        ctx["por_nivel"] = {}
        return render(request, "professor/conteudo.html", ctx)

    if request.method == "POST":
        ConteudoAlgoritmos.objects.create(
            titulo=request.POST.get("titulo", "").strip(),
            descricao=request.POST.get("descricao", "").strip(),
            conteudo=request.POST.get("conteudo", "").strip(),
            nivel=request.POST.get("nivel", "iniciante"),
        )
        messages.success(request, "Topico cadastrado.")
        return redirect("gestao_conteudo")

    por_nivel = {}
    rotulos = {"iniciante": "Iniciante", "intermediario": "Intermediario", "avancado": "Avancado"}
    for c in ConteudoAlgoritmos.objects.filter(ativo=True):
        por_nivel.setdefault(rotulos.get(c.nivel, c.nivel), []).append(c)
    ctx["por_nivel"] = por_nivel
    return render(request, "professor/conteudo.html", ctx)


@professor_required
def gestao_disciplinas(request):
    """Lista/cria/exclui disciplinas e licoes.  URL: /professor/disciplinas/"""
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        if tipo == "disciplina":
            Disciplina.objects.create(
                nome=request.POST.get("nome", "").strip(),
                descricao=request.POST.get("descricao", "").strip(),
                icone=request.POST.get("icone", "").strip(),
                cor_primaria=request.POST.get("cor_primaria", "#0066ff").strip() or "#0066ff",
            )
            messages.success(request, "Disciplina cadastrada.")
        elif tipo == "licao":
            disc = Disciplina.objects.filter(id=request.POST.get("disciplina")).first()
            if disc:
                Licao.objects.create(
                    disciplina=disc,
                    titulo=request.POST.get("titulo", "").strip(),
                    descricao=request.POST.get("descricao", "").strip(),
                    ordem=int(request.POST.get("ordem") or 0),
                    total_etapas=int(request.POST.get("total_etapas") or 1),
                )
                messages.success(request, "Licao cadastrada.")
        elif tipo == "excluir_licao":
            licao = Licao.objects.filter(id=request.POST.get("licao_id")).first()
            if licao:
                licao.delete()
                messages.success(request, "Lição removida.")
        return redirect("gestao_disciplinas")

    ctx = base_ctx(request, "disciplinas")
    ctx["disciplinas"] = list(
        Disciplina.objects.filter(ativa=True).prefetch_related("licoes")
    )
    return render(request, "professor/disciplinas.html", ctx)


@aluno_required
def configuracoes_aluno(request):
    """Configurações do site para o aluno: aparência, notificações,
    perfil e uma zona de perigo para reiniciar o progresso.
    URL: /aluno/configuracoes/"""
    u = request.user

    if request.method == "POST" and request.POST.get("acao") == "zerar_progresso":
        if request.POST.get("confirmar_reset") == "on":
            ProgressoLicao.objects.filter(usuario=u).delete()
            ConquistaUsuario.objects.filter(usuario=u).delete()
            nivel = _nivel_do(u)
            nivel.nivel = 1
            nivel.xp_total = 0
            nivel.xp_proximo_nivel = 300
            nivel.streak_dias = 0
            nivel.save()
            messages.success(request, "Seu progresso foi reiniciado.")
        else:
            messages.error(request, "Marque a caixa de confirmação para reiniciar o progresso.")
        return redirect("configuracoes_aluno")

    if request.method == "POST":
        u.first_name = request.POST.get("first_name", u.first_name).strip()
        u.email = request.POST.get("email", u.email).strip()
        u.tema = request.POST.get("tema", u.tema)
        u.avatar_cor = request.POST.get("avatar_cor", u.avatar_cor)
        u.reduzir_animacoes = request.POST.get("reduzir_animacoes") == "on"
        u.notificacoes_email = request.POST.get("notificacoes_email") == "on"
        u.save(update_fields=[
            "first_name", "email", "tema", "avatar_cor",
            "reduzir_animacoes", "notificacoes_email",
        ])
        messages.success(request, "Configurações salvas.")
        return redirect("configuracoes_aluno")

    ctx = base_ctx(request, "configuracoes")
    ctx["avatar_opcoes"] = Usuario.Avatar.choices
    return render(request, "aluno/configuracoes.html", ctx)


@professor_required
def gestao_quizzes(request):
    """Lista/cria/exclui quizzes.  URL: /professor/quizzes/
    A montagem de perguntas continua sendo feita via /admin/ ou pela IA;
    aqui o professor cadastra o quiz (título/disciplina) e pode removê-lo."""
    if request.method == "POST":
        if request.POST.get("acao") == "excluir":
            q = Quiz.objects.filter(id=request.POST.get("quiz_id")).first()
            if q:
                q.delete()
                messages.success(request, "Quiz removido.")
            return redirect("gestao_quizzes")

        did = request.POST.get("disciplina")
        Quiz.objects.create(
            titulo=request.POST.get("titulo", "").strip(),
            descricao=request.POST.get("descricao", "").strip(),
            disciplina=Disciplina.objects.filter(id=did).first() if did else None,
        )
        messages.success(request, "Quiz cadastrado. Adicione as perguntas pelo /admin/.")
        return redirect("gestao_quizzes")

    ctx = base_ctx(request, "quizzes")
    ctx.update({
        "quizzes": list(Quiz.objects.select_related("disciplina").prefetch_related("questoes")),
        "disciplinas": list(Disciplina.objects.filter(ativa=True)),
    })
    return render(request, "professor/quizzes.html", ctx)


@professor_required
def configuracoes_professor(request):
    """Configurações do site para o professor: aparência, notificações,
    identificação da turma e perfil.
    URL: /professor/configuracoes/"""
    u = request.user
    if request.method == "POST":
        u.first_name = request.POST.get("first_name", u.first_name).strip()
        u.email = request.POST.get("email", u.email).strip()
        u.tema = request.POST.get("tema", u.tema)
        u.avatar_cor = request.POST.get("avatar_cor", u.avatar_cor)
        u.reduzir_animacoes = request.POST.get("reduzir_animacoes") == "on"
        u.notificacoes_email = request.POST.get("notificacoes_email") == "on"
        u.turma_nome = request.POST.get("turma_nome", u.turma_nome).strip()
        u.turma_codigo = request.POST.get("turma_codigo", u.turma_codigo).strip()
        u.turma_turno = request.POST.get("turma_turno", u.turma_turno)
        u.save(update_fields=[
            "first_name", "email", "tema", "avatar_cor", "reduzir_animacoes",
            "notificacoes_email", "turma_nome", "turma_codigo", "turma_turno",
        ])
        messages.success(request, "Configurações salvas.")
        return redirect("configuracoes_professor")

    ctx = base_ctx(request, "configuracoes")
    ctx["avatar_opcoes"] = Usuario.Avatar.choices
    ctx["turno_opcoes"] = Usuario.Turno.choices
    return render(request, "professor/configuracoes.html", ctx)


# ══════════════════════════════════════════════════════════════════════
# SESSAO
# ══════════════════════════════════════════════════════════════════════
def sair(request):
    logout(request)
    return redirect("tela_inicial")
