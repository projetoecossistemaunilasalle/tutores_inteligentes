"""Define os dados do perfil do aluno (nível, estilo, estado emocional).
O Diagnóstico escreve aqui; Planejamento e Motor de IA leem para personalizar o ensino."""

from django.db import models


class PerfilAluno(models.Model):
    """Perfil de um aluno atendido pelo STI.

    Cada instância (objeto) desta classe corresponde a UM aluno e reúne os
    dados que o tutor inteligente usa para personalizar o atendimento.
    """
    
    #1) IDENTIFICAÇÃO DO ALUNO
    nome = models.CharField(
        "Nome do aluno",
        max_length=120,
    )
    identificador = models.CharField(
        "Matrícula ou identificador único",
        max_length=50,
        unique=True,  # impede dois alunos com o mesmo identificador
    )

   
    #2) PERFIL DE APRENDIZAGEM (preenchido pelo Diagnóstico)
    NIVEL_CHOICES = [
        ("iniciante", "Iniciante"),
        ("intermediario", "Intermediário"),
        ("avancado", "Avançado"),
    ]
    nivel_proficiencia = models.CharField(
        "Nível de proficiência atual",
        max_length=20,
        choices=NIVEL_CHOICES,
        default="iniciante",
    )
    estilo_aprendizado = models.CharField(
        "Estilo de aprendizado predominante",
        max_length=80,
        blank=True,  # pode ficar vazio até o diagnóstico identificar
    )

   
    #3) ESTADO EMOCIONAL (preenchido pela Análise Emocional / Groq)
  
    estado_emocional = models.CharField(
        "Último estado emocional detectado",
        max_length=40,
        blank=True,
    )

 
    #4) CONTROLE (datas preenchidas automaticamente pelo Django)
  
    criado_em = models.DateTimeField(
        "Criado em",
        auto_now_add=True,  # gravado uma única vez, na criação
    )
    atualizado_em = models.DateTimeField(
        "Atualizado em",
        auto_now=True,  # regravado a cada vez que o perfil é salvo
    )

    class Meta:
        # 'app_label' liga este modelo ao app "banco_dados", que já está
        # registrado no settings.py. Assim o Django cria a tabela e mostra
        # no admin SEM precisarmos registrar 'modulo_aluno' como novo app.
        app_label = "banco_dados"
        verbose_name = "Perfil do Aluno"
        verbose_name_plural = "Perfis dos Alunos"

    def __str__(self):
        # Texto que aparece no admin do Django ao listar os perfis.
        return f"{self.nome} ({self.identificador}) — {self.nivel_proficiencia}"
