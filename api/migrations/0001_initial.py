# Generated by Django 5.2 on 2025-05-09 21:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('classes', '0003_alter_student_options_student_created_at_and_more'),
        ('questions', '0003_add_gabaritos_gerados'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resultado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pontuacao', models.FloatField()),
                ('total_questoes', models.IntegerField()),
                ('acertos', models.IntegerField()),
                ('data_correcao', models.DateTimeField(auto_now_add=True)),
                ('versao', models.CharField(blank=True, max_length=20, null=True)),
                ('tipo_prova', models.CharField(blank=True, max_length=10, null=True)),
                ('aluno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_resultados', to='classes.student')),
                ('simulado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_resultados', to='questions.simulado')),
            ],
            options={
                'verbose_name': 'Resultado',
                'verbose_name_plural': 'Resultados',
                'ordering': ['-data_correcao'],
                'unique_together': {('aluno', 'simulado', 'data_correcao')},
            },
        ),
        migrations.CreateModel(
            name='DetalhesResposta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.CharField(max_length=10)),
                ('resposta_aluno', models.CharField(max_length=1)),
                ('resposta_correta', models.CharField(max_length=1)),
                ('acertou', models.BooleanField(default=False)),
                ('questao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='questions.questao')),
                ('resultado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalhes', to='api.resultado')),
            ],
            options={
                'verbose_name': 'Detalhe de Resposta',
                'verbose_name_plural': 'Detalhes de Respostas',
                'ordering': ['ordem'],
            },
        ),
    ]
