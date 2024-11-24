from django.db import models
from django.conf import settings
from django.utils import timezone

class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    student_id = models.IntegerField()
    classes = models.ManyToManyField('Class', related_name='students')

    def __str__(self):
        return f"{self.student_id} - {self.name}"

    class Meta:
        pass