from rest_framework import serializers
from classes.models import Class, Student
from questions.models import Questao, Simulado, QuestaoSimulado

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'email', 'student_id', 'classes']

class QuestaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questao
        fields = ['id', 'disciplina', 'conteudo', 'enunciado', 'alternativa_a', 'alternativa_b', 
                  'alternativa_c', 'alternativa_d', 'alternativa_e', 'resposta_correta', 
                  'nivel_dificuldade']

class QuestaoSimuladoSerializer(serializers.ModelSerializer):
    questao = QuestaoSerializer()

    class Meta:
        model = QuestaoSimulado
        fields = ['ordem', 'questao']

class SimuladoSerializer(serializers.ModelSerializer):
    questoes = QuestaoSimuladoSerializer(source='questaosimulado_set', many=True, read_only=True)

    class Meta:
        model = Simulado
        fields = ['id', 'titulo', 'descricao', 'questoes', 'data_criacao', 'ultima_modificacao', 
                  'cabecalho', 'instrucoes', 'classes']

class CartaoRespostaSerializer(serializers.Serializer):
    aluno_id = serializers.IntegerField()
    simulado_id = serializers.IntegerField()
    respostas = serializers.JSONField()