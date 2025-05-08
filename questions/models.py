#questions/models.py
from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from django.core.exceptions import ValidationError
from classes.models import Class  # Importe o modelo Class


class Questao(models.Model):
    NIVEL_CHOICES = [
        ('F', 'Fácil'),
        ('M', 'Médio'),
        ('D', 'Difícil')
    ]

    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questoes'
    )
    disciplina = models.CharField(max_length=100)
    conteudo = models.CharField(max_length=100)
    enunciado = RichTextField()
    imagem = models.ImageField(
        upload_to='questoes/',
        null=True,
        blank=True,
        help_text='Imagens devem ter no máximo 5MB'
    )
    alternativa_a = RichTextField()
    alternativa_b = RichTextField()
    alternativa_c = RichTextField()
    alternativa_d = RichTextField()
    alternativa_e = RichTextField()
    resposta_correta = models.CharField(
        max_length=1,
        choices=[
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('E', 'E')
        ]
    )
    nivel_dificuldade = models.CharField(
        max_length=1,
        choices=NIVEL_CHOICES,
        default='M'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_modificacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Questão {self.id} - {self.disciplina} - {self.conteudo}"

    def clean(self):
        if self.imagem and self.imagem.size > 5 * 1024 * 1024:  # 5MB
            raise ValidationError('O tamanho máximo da imagem é 5MB')

class Simulado(models.Model):
    gabaritos_gerados = models.JSONField(null=True, blank=True, help_text='Armazena as informações de embaralhamento após gerar o PDF')
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='simulados'
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    questoes = models.ManyToManyField(
        'Questao',
        through='QuestaoSimulado',
        related_name='simulados'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_modificacao = models.DateTimeField(auto_now=True)
    cabecalho = RichTextField(blank=True, null=True)
    instrucoes = RichTextField(blank=True, null=True)
    classes = models.ManyToManyField(Class, related_name='simulados', blank=True)  # Nova relação com as turmas

    class Meta:
        verbose_name = 'Simulado'
        verbose_name_plural = 'Simulados'
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

    def clean(self):
        # Só verifica o número de questões se o simulado já foi salvo
        if self.pk:
            if self.questoes.count() > 45:
                raise ValidationError('O simulado não pode ter mais que 45 questões')

class QuestaoSimulado(models.Model):
    simulado = models.ForeignKey(Simulado, on_delete=models.CASCADE)
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    ordem = models.PositiveIntegerField()

    class Meta:
        ordering = ['ordem']
        unique_together = [
            ['simulado', 'questao'],  # Evita duplicatas de questões no mesmo simulado
            ['simulado', 'ordem']     # Garante que cada ordem seja única dentro do simulado
        ]

    def save(self, *args, **kwargs):
        # Se a ordem não foi definida, atribui a próxima ordem disponível
        if not self.ordem:
            max_ordem = QuestaoSimulado.objects.filter(simulado=self.simulado).aggregate(models.Max('ordem'))['ordem__max'] or 0
            self.ordem = max_ordem + 1
        super().save(*args, **kwargs)

    def clean(self):
        # Verifica se a questão já existe no simulado
        if QuestaoSimulado.objects.filter(simulado=self.simulado, questao=self.questao).exclude(pk=self.pk).exists():
            raise ValidationError('Esta questão já foi adicionada ao simulado.')

        # Verifica se a ordem já está em uso no simulado
        if QuestaoSimulado.objects.filter(simulado=self.simulado, ordem=self.ordem).exclude(pk=self.pk).exists():
            raise ValidationError('Esta ordem já está em uso neste simulado.')

    def __str__(self):
        return f"Questão {self.questao.id} no Simulado {self.simulado.id} (Ordem: {self.ordem})"
