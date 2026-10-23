import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0006_usuario_avatar_cor_usuario_reduzir_animacoes_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="licao",
            options={
                "ordering": ["disciplina", "ordem"],
                "verbose_name": "Aula",
                "verbose_name_plural": "Aulas",
            },
        ),
        migrations.AlterModelOptions(
            name="progressolicao",
            options={
                "ordering": ["-atualizado_em"],
                "unique_together": {("usuario", "licao")},
                "verbose_name": "Progresso de Aula",
                "verbose_name_plural": "Progressos de Aulas",
            },
        ),
        migrations.AlterField(
            model_name="conversa",
            name="licao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="conversas",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
        migrations.AlterField(
            model_name="progressolicao",
            name="licao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="progressos",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
        migrations.AlterField(
            model_name="quiz",
            name="licao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quizzes",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
        migrations.AlterField(
            model_name="videoaula",
            name="licao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="videoaulas",
                to="app.licao",
                verbose_name="Aula",
            ),
        ),
        migrations.AlterField(
            model_name="conquista",
            name="categoria",
            field=models.CharField(
                choices=[
                    ("inicio", "Primeiros passos"),
                    ("consistencia", "Consistência"),
                    ("conversas", "Conversas com o tutor"),
                    ("licoes", "Aulas"),
                    ("quizzes", "Quizzes"),
                    ("exercicios", "Exercícios"),
                    ("progressao", "Nível & XP"),
                    ("geral", "Geral"),
                ],
                default="geral",
                max_length=20,
                verbose_name="Categoria",
            ),
        ),
    ]
