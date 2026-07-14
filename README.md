# STI — Sistema de Tutores Inteligentes

Tutor inteligente híbrido para a disciplina de Algoritmos e Programação.
Arquitetura: IA Estruturada + RAG local + IA Generativa (Groq/LLaMA).

---

## Divisão de Grupos

### Grupo 1 — Backend (Marcos)
Responsável pela lógica pedagógica, inteligência artificial e API.
Localização: `src/sti/`

Módulos:
- `modulo_aluno/` — perfil, histórico, desempenho e análise emocional
- `modulo_dominio/` — base de conhecimento, Q&A, exercícios e RAG
- `pedagogico/` — diagnóstico, planejamento e tutor service
- `motor_ia/` — IA estruturada, IA embarcada e orquestrador
- `banco_dados/` — modelos, migrações e admin
- `seguranca/` — autenticação e permissões
- `infraestrutura/` — logging e exceções

Rodar o servidor do Grupo 1:
```bash
python manage.py runserver 8000
```

---

### Grupo 2 — Frontend (Leonardo)
Responsável pela interface, ambiente de aprendizagem e integração visual.
Localização: `src/frontend/`

Módulos a implementar:
- `usuarios/` — cadastro, login e perfil visual
- `conversas/` — interface do chat e histórico visual
- `disciplinas/` — listagem de conteúdos e lições
- `conquistas/` — gamificação e progresso
- `quizzes/` — atividades e questões
- `notificacoes/` — alertas e avisos

Rodar o servidor do Grupo 2:
```bash
python manage_frontend.py runserver 8001
```

---

## Ponto de Integração entre os Grupos

O Grupo 2 se comunica com o Grupo 1 exclusivamente pela API:

```
POST http://127.0.0.1:8000/api/perguntar/

Body JSON:
{
    "pergunta": "texto digitado pelo aluno",
    "aluno_id": "identificador do aluno"
}

Retorno:
{
    "resposta": "resposta do tutor",
    "fontes": [],
    "aluno_id": "identificador do aluno"
}
```

---

## Como começar

### Pré-requisitos
- Python 3.10+
- Git

### Instalação
```bash
# Clone o repositório
git clone https://github.com/projetoecossistemaunilasalle/tutores_inteligentes

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Instale as dependências
pip install -r requirements.txt
pip install groq

# Configure as variáveis de ambiente
copy .env.example .env  # edite com suas chaves
```

### Variáveis de ambiente (.env)
```
GROQ_API_KEY=sua_chave_aqui
EXA_API_KEY=sua_chave_aqui
API_BACKEND_URL=http://127.0.0.1:8000
```

---

## Stack
Python · Django · Groq (LLaMA) · ChromaDB · SQLite → PostgreSQL · Git/GitHub