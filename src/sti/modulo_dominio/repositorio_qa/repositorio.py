"""Guarda pares pergunta-resposta já validados pelo professor (um FAQ da disciplina).
Se a pergunta do aluno já existe aqui, o tutor responde sem custo de API."""

from django.db import models

# Importamos o tópico para poder LIGAR cada pergunta ao assunto a que pertence.
from sti.modulo_dominio.base_conhecimento.conteudo_algoritmos import ConteudoAlgoritmos


class RepositorioQA(models.Model):
    """Um par pergunta-resposta validado pelo professor."""

    # ------------------------------------------------------------------ #
    # 1) O PAR PERGUNTA / RESPOSTA                                        #
    # ------------------------------------------------------------------ #
    pergunta = models.TextField("Pergunta")
    resposta = models.TextField("Resposta validada pelo professor")

    # ------------------------------------------------------------------ #
    # 2) A QUE TÓPICO PERTENCE                                            #
    # ------------------------------------------------------------------ #
    # Liga a pergunta a um tópico da base de conhecimento (opcional).
    topico = models.ForeignKey(
        ConteudoAlgoritmos,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,   # se o tópico for apagado, só limpa o vínculo
        related_name="perguntas",
        verbose_name="Tópico relacionado",
    )

    # ------------------------------------------------------------------ #
    # 3) APOIO À BUSCA                                                    #
    # ------------------------------------------------------------------ #
    # Palavras-chave ajudam a encontrar esta pergunta quando o aluno
    # escrever algo parecido (busca simples, antes de recorrer ao RAG).
    palavras_chave = models.CharField(
        "Palavras-chave",
        max_length=255,
        blank=True,
    )

    # ------------------------------------------------------------------ #
    # 4) CONTROLE                                                         #
    # ------------------------------------------------------------------ #
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        app_label = "banco_dados"
        verbose_name = "Pergunta e Resposta (Q&A)"
        verbose_name_plural = "Repositório de Q&A"
        ordering = ["-atualizado_em"]

    def __str__(self):
        # Mostra os primeiros caracteres da pergunta na listagem do admin.
        return self.pergunta[:60]