from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from classes.models import Class, Student
from questions.models import Questao, Simulado
from .serializers import ClassSerializer, StudentSerializer, QuestaoSerializer, SimuladoSerializer, CartaoRespostaSerializer
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated

class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class QuestaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer

class SimuladoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Simulado.objects.all()
    serializer_class = SimuladoSerializer

    @action(detail=True, methods=['post'])
    def corrigir(self, request, pk=None):
        simulado = self.get_object()
        serializer = CartaoRespostaSerializer(data=request.data)
        
        if serializer.is_valid():
            aluno_id = serializer.validated_data['aluno_id']
            respostas = serializer.validated_data['respostas']
            
            try:
                aluno = Student.objects.get(id=aluno_id)
            except Student.DoesNotExist:
                return Response({'error': 'Aluno não encontrado'}, status=status.HTTP_404_NOT_FOUND)

            # Lógica de correção aqui
            pontuacao = self.calcular_pontuacao(simulado, respostas)

            return Response({
                'aluno': aluno.name,
                'simulado': simulado.titulo,
                'pontuacao': pontuacao,
                'data_correcao': timezone.now()
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def calcular_pontuacao(self, simulado, respostas):
        # Implemente a lógica de cálculo da pontuação
        # Comparar as respostas com o gabarito do simulado
        # Retornar a pontuação calculada
        pass

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    return Response({"message": "Conexão bem-sucedida!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    user = request.user
    return Response({
        'name': user.get_full_name() or user.username,
        'email': user.email,
        # Adicione outros campos conforme necessário
    })