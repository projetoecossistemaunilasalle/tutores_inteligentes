"""Junta objetivos, trilha e estratégia num plano de aprendizagem completo,
a partir do perfil do aluno e dos conteúdos do domínio."""

from sti.pedagogico.planejamento.objetivos_aprendizagem import (
    definir_objetivos,
)
from sti.pedagogico.planejamento.trilha_estudos import montar_trilha
from sti.pedagogico.planejamento.estrategia_ensino import (
    definir_estrategia,
)


def montar_plano(perfil, conteudos):
    """Monta o plano de aprendizagem completo do aluno.

    Args:
        perfil: o PerfilAluno (usa .nivel_proficiencia e
            .estilo_aprendizado).
        conteudos: lista de tópicos do domínio
            (ConteudoAlgoritmos).

    Returns:
        dict: {
            "objetivos": list,   # o que o aluno deve alcançar
            "trilha": list,      # tópicos na ordem de estudo
            "estrategia": str,   # como ensinar
        }
    """
    nivel = perfil.nivel_proficiencia
    estilo = perfil.estilo_aprendizado

    return {
        "objetivos": definir_objetivos(nivel, conteudos),
        "trilha": montar_trilha(conteudos, nivel),
        "estrategia": definir_estrategia(estilo),
    }
