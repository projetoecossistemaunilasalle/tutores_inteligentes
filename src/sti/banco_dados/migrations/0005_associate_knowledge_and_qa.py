import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_usuario_avatar_cor_usuario_reduzir_animacoes_and_more"),
        ("banco_dados", "0004_delete_videoaula"),
    ]

    operations = [
        migrations.AddField(
            model_name="conteudoalgoritmos",
            name="disciplina",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="topicos_conhecimento",
                to="app.disciplina",
                verbose_name="Disciplina",
            ),
        ),
        migrations.AddField(
            model_name="conteudoalgoritmos",
            name="aula",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="topicos_base_conhecimento",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
        migrations.AddField(
            model_name="repositorioqa",
            name="disciplina",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="registros_qa",
                to="app.disciplina",
                verbose_name="Disciplina",
            ),
        ),
        migrations.AddField(
            model_name="repositorioqa",
            name="aula",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="registros_qa",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
    ]
