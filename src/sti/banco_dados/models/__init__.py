"""Reúne todos os modelos do STI para o Django (app 'banco_dados') reconhecê-los,
criar as tabelas (migrations) e exibi-los no Admin.
Ao criar um novo modelo, adicione a linha de import abaixo."""

# --- Módulo do Aluno ---
from sti.modulo_aluno.perfil.perfil_aluno import PerfilAluno
from sti.modulo_aluno.historico.historico_interacoes import HistoricoInteracoes

# --- Módulo de Domínio ---
from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import (
    ConteudoAlgoritmos,
)
from sti.modulo_dominio.repositorio_qa.repositorio import RepositorioQA
from sti.modulo_dominio.exercicios.exercicio import Exercicio
from sti.modulo_dominio.exercicios.gabarito import Gabarito
