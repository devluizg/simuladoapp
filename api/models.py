from django.db import models
from classes.models import Student
from questions.models import Simulado, Questao

class Resultado(models.Model):
    """Modelo para armazenar os resultados de um simulado para um aluno"""
    aluno = models.ForeignKey(Student, on_delete=models.CASCADE)
    simulado = models.ForeignKey(Simulado, on_delete=models.CASCADE)
    pontuacao = models.FloatField()
    total_questoes = models.IntegerField()
    acertos = models.IntegerField()
    data_correcao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('aluno', 'simulado', 'data_correcao')
        ordering = ['-data_correcao']
        
    def __str__(self):
        return f"{self.aluno.name} - {self.simulado.titulo} - {self.pontuacao}%"
        
class DetalhesResposta(models.Model):
    """Modelo para armazenar os detalhes das respostas de um resultado"""
    resultado = models.ForeignKey(Resultado, on_delete=models.CASCADE, related_name='detalhes')
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE)
    ordem = models.CharField(max_length=10)  # Número da questão no simulado
    resposta_aluno = models.CharField(max_length=1)  # A, B, C, D ou E
    resposta_correta = models.CharField(max_length=1)  # A, B, C, D ou E
    acertou = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['ordem']
        
    def __str__(self):
        return f"Q{self.ordem}: {self.resposta_aluno} ({'✓' if self.acertou else '✗'})"