import django.db.models.deletion
from django.db import migrations, models

import sti.infraestrutura.validadores_arquivo


class Migration(migrations.Migration):

    dependencies = [
        ("banco_dados", "0005_associate_knowledge_and_qa"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArquivoExercicio",
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
                        upload_to="exercicios/materiais/",
                        validators=[sti.infraestrutura.validadores_arquivo.validar_arquivo_exercicio],
                        verbose_name="Arquivo",
                    ),
                ),
                (
                    "enviado_em",
                    models.DateTimeField(auto_now_add=True, verbose_name="Enviado em"),
                ),
                (
                    "exercicio",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="arquivos",
                        to="banco_dados.exercicio",
                        verbose_name="Exercício",
                    ),
                ),
            ],
            options={
                "verbose_name": "Arquivo de exercício",
                "verbose_name_plural": "Arquivos de exercícios",
                "ordering": ["enviado_em", "id"],
            },
        ),
    ]
