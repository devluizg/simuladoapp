from django.db import models
from django.conf import settings
from django.utils.timezone import now

class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name="Professor"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

class Student(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome completo")
    email = models.EmailField(null=True, blank=True, verbose_name="E-mail")
    student_id = models.IntegerField(verbose_name="Número de matrícula")
    classes = models.ManyToManyField('Class', related_name='students', verbose_name="Turmas")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='students',
        verbose_name="Professor"
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.student_id} - {self.name}"

    class Meta:
        unique_together = ['user', 'student_id']
        verbose_name = "Aluno"
        verbose_name_plural = "Alunos"
        ordering = ['student_id', 'name']

class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performances')
    simulado = models.ForeignKey('questions.Simulado', on_delete=models.CASCADE, related_name='student_performances')
    score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Nota")
    correct_answers = models.IntegerField(default=0, verbose_name="Respostas corretas")
    total_questions = models.IntegerField(default=0, verbose_name="Total de questões")
    date_taken = models.DateTimeField(auto_now_add=True, verbose_name="Data de realização")
    
    class Meta:
        unique_together = ['student', 'simulado']
        verbose_name = "Desempenho do aluno"
        verbose_name_plural = "Desempenhos dos alunos"
        
    def __str__(self):
        return f"{self.student.name} - {self.simulado.title} - {self.score}"
        
    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100

class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('questions.QuestaoSimulado', on_delete=models.CASCADE, related_name='student_answers')
    simulado = models.ForeignKey('questions.Simulado', on_delete=models.CASCADE, related_name='student_answers')
    chosen_option = models.CharField(max_length=1, verbose_name="Alternativa escolhida")
    is_correct = models.BooleanField(default=False, verbose_name="Está correta")
    
    class Meta:
        unique_together = ['student', 'question', 'simulado']
        verbose_name = "Resposta do aluno"
        verbose_name_plural = "Respostas dos alunos"
        
    def __str__(self):
        return f"{self.student.name} - Q{self.question.order} - {self.chosen_option}"