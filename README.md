# STI — Sistema de Tutores Inteligentes (Grupo 1)

Tutor inteligente hibrido para a disciplina de Algoritmos e Programacao.
Arquitetura: IA Estruturada + RAG local + IA Embarcada (LLaMA/Mistral via
Ollama), com LLM em nuvem apenas como filtro/linguagem.

## Escopo deste repositorio — Grupo 1
- `pedagogico/` — diagnostico, planejamento, adaptacao, acompanhamento
- `modulo_aluno/` — perfil, historico, desempenho
- `modulo_dominio/` — base de conhecimento, Q&A, RAG, exercicios
- `motor_ia/` — IA Estruturada, IA Embarcada, Motor de Decisao
- `banco_dados/` e `seguranca/` — camada transversal (compartilhada)

O **Grupo 2 (Leonardo)** — Interface, Ambiente de Aprendizagem e Integracao
Visual — sera integrado depois. O ponto de entrada para ele e a funcao
`motor_ia.motor_decisao.orquestrador.responder(...)`.

## Como comecar
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env          # e preencha os valores
```

## Stack
Python · Django + DRF · PyTorch · Ollama · ChromaDB · Git/GitHub · VSCode
