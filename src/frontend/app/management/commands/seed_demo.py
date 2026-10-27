"""
Popula o banco com dados de demonstracao para todas as janelas.

Uso:
    python manage.py seed_demo

Cria: usuarios (aluno/professor), disciplinas, licoes, niveis, conquistas,
notificacoes, quizzes, videoaulas e, se o app do Grupo 1 estiver instalado,
topicos, exercicios, gabaritos, Q&A, perfis e historico.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from frontend.app.models.usuarios import Usuario
from frontend.app.models.disciplina import Disciplina, Licao
from frontend.app.models.progresso import (
    NivelUsuario, ProgressoLicao, Conquista, ConquistaUsuario, Notificacao,
)
from frontend.app.models.quizzes import Quiz, Questao, Alternativa
from frontend.app.models.videoaulas import Videoaula


class Command(BaseCommand):
    help = "Cria dados de demonstracao para todas as telas."

    def handle(self, *args, **opts):
        w = self.stdout.write

        # ---------------- Usuarios ----------------
        prof, _ = Usuario.objects.get_or_create(
            username="prof.costa",
            defaults=dict(first_name="Joao Costa", email="costa@escola.edu.br",
                          papel="professor", primeiro_acesso=False, is_staff=True),
        )
        prof.set_password("123456"); prof.primeiro_acesso = False; prof.save()

        aluno, _ = Usuario.objects.get_or_create(
            username="2024001234",
            defaults=dict(first_name="Aluno Demo", email="aluno@escola.edu.br",
                          papel="aluno", primeiro_acesso=False,
                          identificador_aluno="2024001234"),
        )
        aluno.set_password("123456"); aluno.save()

        maria, _ = Usuario.objects.get_or_create(
            username="2024005678",
            defaults=dict(first_name="Maria Silva", email="maria@escola.edu.br",
                          papel="aluno", primeiro_acesso=False,
                          identificador_aluno="2024005678"),
        )
        maria.set_password("123456"); maria.save()

        admin, created = Usuario.objects.get_or_create(
            username="admin",
            defaults=dict(first_name="Admin", papel="professor",
                          primeiro_acesso=False, is_staff=True, is_superuser=True),
        )
        if created:
            admin.set_password("admin"); admin.save()
        w("Usuarios: prof.costa / 2024001234 / 2024005678 (senha 123456), admin/admin")

        # ---------------- Disciplina única + Lições ----------------
        NOME_DISCIPLINA = "Algoritmos e Programação"
        disc, _ = Disciplina.objects.get_or_create(
            nome=NOME_DISCIPLINA,
            defaults=dict(
                icone="💻", cor_primaria="#0066ff", ordem=0,
                prompt_sistema=(
                    "Você é o Prof.ia, tutor de Algoritmos e Programação. "
                    "Explique com exemplos de código claros e proponha exercícios progressivos."
                ),
            ),
        )
        for j, tit in enumerate(["Variáveis e tipos", "Estruturas condicionais", "Laços de repetição"]):
            Licao.objects.get_or_create(
                disciplina=disc, titulo=tit,
                defaults=dict(ordem=j, total_etapas=8,
                              descricao=f"Licao introdutoria de {tit.lower()}."),
            )
        disciplinas = [disc]

        # Remove matérias antigas de execuções anteriores do seed (mantém o banco limpo)
        removidas = Disciplina.objects.exclude(nome=NOME_DISCIPLINA)
        if removidas.exists():
            w(f"Removendo {removidas.count()} disciplina(s) antiga(s)...")
            removidas.delete()
        # Quizzes/videoaulas orfãos (de disciplinas removidas) também saem
        Quiz.objects.filter(disciplina__isnull=True).delete()
        Videoaula.objects.filter(disciplina__isnull=True).delete()

        w(f"Disciplinas: {len(disciplinas)} (com licoes)")

        # ---------------- Nivel + Progresso ----------------
        for u, xp, nv, streak in [(aluno, 2340, 7, 5), (maria, 3120, 9, 12)]:
            nivel, _ = NivelUsuario.objects.get_or_create(usuario=u)
            nivel.xp_total = xp; nivel.nivel = nv; nivel.xp_proximo_nivel = 300
            nivel.streak_dias = streak; nivel.ultima_atividade = timezone.now().date()
            nivel.save()

        licoes = list(Licao.objects.all()[:4])
        for k, lic in enumerate(licoes):
            ProgressoLicao.objects.get_or_create(
                usuario=aluno, licao=lic,
                defaults=dict(etapa_atual=min(lic.total_etapas, 3 + k),
                              concluida=(k == 0), xp_ganho=40),
            )
        w("Niveis e progresso do aluno criados")

        # ---------------- Conquistas + Notificacoes ----------------
        # (codigo, nome, descricao, icone, xp_bonus, categoria)
        conqs = [
            # Primeiros passos
            ("primeiro_login", "Primeiros passos", "Fez o primeiro acesso à plataforma.", "🎯", 20, "inicio"),
            ("primeira_pergunta", "Quebra-gelo", "Fez a primeira pergunta ao tutor.", "💬", 15, "inicio"),
            ("primeiro_exercicio", "Mão na massa", "Respondeu ao primeiro exercício.", "✍️", 15, "inicio"),
            ("primeiro_quiz", "Testando os limites", "Completou o primeiro quiz.", "🧩", 15, "inicio"),
            ("perfil_completo", "Tudo em ordem", "Preencheu nome e e-mail no perfil.", "🪪", 10, "inicio"),
            # Consistência
            ("streak3", "Aquecendo", "3 dias seguidos estudando.", "🔥", 20, "consistencia"),
            ("streak5", "Ritmo constante", "5 dias seguidos de estudo.", "🔥", 50, "consistencia"),
            ("streak7", "Uma semana inteira", "7 dias seguidos estudando.", "📅", 80, "consistencia"),
            ("streak15", "Disciplina de ferro", "15 dias seguidos estudando.", "🗓️", 150, "consistencia"),
            ("streak30", "Um mês de dedicação", "30 dias seguidos estudando.", "🏅", 300, "consistencia"),
            # Conversas com o tutor
            ("perguntas10", "Curioso", "Fez 10 perguntas ao tutor.", "🙋", 30, "conversas"),
            ("perguntas50", "Investigador", "Fez 50 perguntas ao tutor.", "🔍", 80, "conversas"),
            ("perguntas100", "Sedento por conhecimento", "Fez 100 perguntas ao tutor.", "📖", 150, "conversas"),
            # Lições
            ("primeira_licao", "Primeira vitória", "Concluiu a primeira lição.", "✅", 25, "licoes"),
            ("maratonista", "Maratonista", "Concluiu todas as lições da matéria.", "🏃", 120, "licoes"),
            # Quizzes
            ("quiz_ace", "Mestre do quiz", "Gabaritou um quiz (100%).", "🧠", 80, "quizzes"),
            ("quiz_veterano", "Veterano dos quizzes", "Completou 5 quizzes.", "🎓", 60, "quizzes"),
            ("quiz_perfeccionista", "Perfeccionista", "Gabaritou 3 quizzes.", "💯", 150, "quizzes"),
            # Exercícios
            ("exercicios10", "Praticante", "Acertou 10 exercícios.", "🏋️", 40, "exercicios"),
            ("exercicios25", "Treinado", "Acertou 25 exercícios.", "💪", 90, "exercicios"),
            ("gabarito_mestre", "Gabarito mestre", "Acertou todos os exercícios disponíveis.", "📜", 150, "exercicios"),
            # Nível & XP
            ("nivel5", "Ganhando experiência", "Alcançou o nível 5.", "⭐", 40, "progressao"),
            ("nivel10", "Veterano", "Alcançou o nível 10.", "🌟", 80, "progressao"),
            ("xp1000", "Colecionador de XP", "Acumulou 1.000 XP.", "🪙", 30, "progressao"),
            ("xp5000", "Lenda do XP", "Acumulou 5.000 XP.", "🏆", 100, "progressao"),
        ]
        objs = []
        for cod, nome, desc, ico, xp, cat in conqs:
            c, _ = Conquista.objects.update_or_create(
                codigo=cod,
                defaults=dict(nome=nome, descricao=desc, icone=ico, xp_bonus=xp, categoria=cat),
            )
            objs.append(c)

        # Roda a verificação REAL de conquistas contra os dados já semeados
        # (nível, streak, lição concluída etc.) — nada é forçado; só
        # desbloqueia o que o aluno já "conquistou" de fato com este estado.
        from frontend.app.views import _nivel_do, verificar_conquistas
        nivel_aluno = _nivel_do(aluno)
        verificar_conquistas(aluno, nivel_aluno)
        nivel_aluno.save()

        # As notificações de conquista já foram criadas de verdade pelo
        # verificar_conquistas() acima — uma para cada conquista genuína.
        Notificacao.objects.get_or_create(
            usuario=aluno, titulo="Novo quiz disponivel",
            defaults=dict(tipo="quiz", corpo="Um quiz de Logica Matematica foi liberado."))
        w("Conquistas e notificacoes criadas")

        # ---------------- Quiz ----------------
        quiz, novo = Quiz.objects.get_or_create(
            titulo="Quiz — Variáveis e laços",
            defaults=dict(disciplina=disciplinas[0], descricao="3 questoes de algoritmos.",
                          total_questoes=3, ativo=True))
        if novo:
            perguntas = [
                ("Qual tipo de dado guarda 'verdadeiro' ou 'falso'?",
                 [("Booleano", True), ("String", False)]),
                ("Quantas vezes 'for i in range(3)' executa?",
                 [("2", False), ("3", True)]),
                ("O que uma estrutura condicional (if/else) faz?",
                 [("Repete um bloco de código", False), ("Decide entre caminhos diferentes", True)]),
            ]
            for i, (enun, alts) in enumerate(perguntas):
                q = Questao.objects.create(quiz=quiz, enunciado=enun,
                                           tipo="multipla", ordem=i)
                for j, (txt, ok) in enumerate(alts):
                    Alternativa.objects.create(questao=q, texto=txt, correta=ok, ordem=j)
        w("Quiz de demonstracao criado")

        # ---------------- Videoaulas ----------------
        vids = [
            ("Introdução à programação", "https://www.youtube.com/watch?v=zOjov-2OZ0E", 14, disciplinas[0]),
            ("Variáveis e tipos de dados", "https://www.youtube.com/watch?v=Z1Yd7upQsXY", 11, disciplinas[0]),
            ("Laços de repetição na prática", "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ", 16, disciplinas[0]),
        ]
        for tit, url, dur, disc in vids:
            Videoaula.objects.get_or_create(
                titulo=tit, defaults=dict(url_youtube=url, duracao_minutos=dur,
                                          disciplina=disc, cadastrado_por=prof))
        w("Videoaulas criadas")

        # ---------------- Grupo 1 (opcional) ----------------
        try:
            from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import ConteudoAlgoritmos
            from sti.modulo_dominio.exercicios.exercicio import Exercicio
            from sti.modulo_dominio.exercicios.gabarito import Gabarito
            from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA
            from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
            from sti.modulo_aluno.historico.historico_interacoes import HistoricoInteracoes
        except Exception as e:  # pragma: no cover
            w(f"Grupo 1 nao instalado ({e}); pulando dados do STI.")
            w(self.style.SUCCESS("Seed concluido (somente Grupo 2)."))
            return

        topicos = []
        for i, (tit, desc) in enumerate([
            ("Tabela verdade", "Operadores logicos e valores V/F."),
            ("Laços de repeticao", "for, while e iteracao."),
            ("Ordenacao", "Bubble sort e selection sort."),
        ]):
            t, _ = ConteudoAlgoritmos.objects.get_or_create(
                titulo=tit, defaults=dict(descricao=desc, nivel="iniciante", ordem=i,
                                          conteudo=f"Material sobre {tit.lower()}."))
            topicos.append(t)

        pares = [
            ("Qual o resultado de V E F?", "iniciante", "falso", "V E F e sempre falso."),
            ("Quantas vezes 'for i in range(3)' executa?", "iniciante", "3", "range(3) gera 0,1,2."),
            ("O bubble sort compara pares?", "intermediario", "sim", "Compara e troca elementos adjacentes."),
        ]
        for i, (enun, nv, resp, expl) in enumerate(pares):
            ex, novo = Exercicio.objects.get_or_create(
                enunciado=enun, defaults=dict(topico=topicos[i % len(topicos)], nivel=nv))
            if novo:
                Gabarito.objects.create(exercicio=ex, resposta_correta=resp, explicacao=expl)

        RepositorioQA.objects.get_or_create(
            pergunta="O que e uma tabela verdade?",
            defaults=dict(resposta="E uma tabela que lista todos os valores possiveis de uma expressao logica.",
                          topico=topicos[0], palavras_chave="logica, tabela, verdade"))

        perfil, _ = PerfilAluno.objects.get_or_create(
            identificador="2024001234",
            defaults=dict(nome="Aluno Demo", nivel_proficiencia="intermediario",
                          estilo_aprendizado="visual", estado_emocional="motivado"))
        PerfilAluno.objects.get_or_create(
            identificador="2024005678",
            defaults=dict(nome="Maria Silva", nivel_proficiencia="avancado",
                          estilo_aprendizado="pratico", estado_emocional="confiante"))

        HistoricoInteracoes.objects.get_or_create(
            aluno=perfil, pergunta="Como funciona a tabela verdade?",
            defaults=dict(resposta="A tabela verdade mostra o resultado de expressoes para cada combinacao de V/F.",
                          topico="Tabela verdade", origem="regras"))
        HistoricoInteracoes.objects.get_or_create(
            aluno=perfil, pergunta="Me da um exemplo de laco for.",
            defaults=dict(resposta="for i in range(3): print(i)  # imprime 0,1,2",
                          topico="Laços", origem="llm"))

        w(self.style.SUCCESS("Seed concluido (Grupo 2 + Grupo 1)."))
