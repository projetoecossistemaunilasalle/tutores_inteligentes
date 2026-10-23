import django.db.models.deletion
from django.db import migrations, models

import sti.infraestrutura.validadores_arquivo


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0007_use_aula_labels"),
        ("banco_dados", "0005_associate_knowledge_and_qa"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArquivoRespostaExercicio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "arquivo",
                    models.FileField(
                        upload_to="exercicios/respostas/",
                        validators=[sti.infraestrutura.validadores_arquivo.validar_arquivo_exercicio],
                        verbose_name="Arquivo",
                    ),
                ),
                (
                    "enviado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Enviado em"),
                ),
                (
                    "resposta_exercicio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="arquivos_anexados",
                        to="app.respostaexercicio",
                        verbose_name="Resposta do exercício",
                    ),
                ),
            ],
            options={
                "verbose_name": "Arquivo de resposta de exercício",
                "verbose_name_plural": "Arquivos de respostas de exercícios",
                "ordering": ["enviado_em", "id"],
            },
        ),
    ]
