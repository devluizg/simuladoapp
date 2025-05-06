#api/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.models import Resultado, DetalhesResposta
from classes.models import Class, Student
from questions.models import Questao, Simulado, QuestaoSimulado
from .serializers import (
    ClassSerializer, StudentSerializer, QuestaoSerializer, 
    SimuladoSerializer, CartaoRespostaSerializer, ResultadoSerializer,
    DetalhesRespostaSerializer, DashboardAlunoSerializer
)
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Sum, F, Q
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken

class ClassViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar e detalhar turmas.
    """
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas as turmas do usuário autenticado"""
        return Class.objects.filter(user=self.request.user).order_by('id')
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Retorna todos os alunos de uma turma específica"""
        turma = self.get_object()
        students = Student.objects.filter(classes=turma)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def simulados(self, request, pk=None):
        """Retorna todos os simulados associados a uma turma específica"""
        turma = self.get_object()
        simulados = Simulado.objects.filter(classes=turma)
        serializer = SimuladoSerializer(simulados, many=True)
        return Response(serializer.data)

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar e detalhar alunos.
    """
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna apenas os alunos do usuário autenticado"""
        return Student.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def simulados(self, request, pk=None):
        """Retorna todos os simulados disponíveis para um aluno específico"""
        aluno = self.get_object()
        simulados = Simulado.objects.filter(classes__in=aluno.classes.all()).distinct()
        serializer = SimuladoSerializer(simulados, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def resultados(self, request, pk=None):
        """Retorna todos os resultados de simulados de um aluno específico"""
        aluno = self.get_object()
        resultados = Resultado.objects.filter(aluno=aluno)
        serializer = ResultadoSerializer(resultados, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Retorna dados do dashboard de desempenho do aluno"""
        aluno = self.get_object()
        
        # Estatísticas gerais
        total_simulados = Resultado.objects.filter(aluno=aluno).count()
        media_geral = Resultado.objects.filter(aluno=aluno).aggregate(Avg('pontuacao'))['pontuacao__avg'] or 0
        
        # Desempenho por disciplina
        desempenho_disciplinas = []
        disciplinas = Questao.objects.values_list('disciplina', flat=True).distinct()
        
        for disciplina in disciplinas:
            # Calcular média por disciplina
            detalhes = DetalhesResposta.objects.filter(
                resultado__aluno=aluno,
                questao__disciplina=disciplina
            )
            
            total_questoes = detalhes.count()
            acertos = detalhes.filter(acertou=True).count()
            
            if total_questoes > 0:
                taxa_acerto = (acertos / total_questoes) * 100
            else:
                taxa_acerto = 0
                
            desempenho_disciplinas.append({
                'disciplina': disciplina,
                'total_questoes': total_questoes,
                'acertos': acertos,
                'taxa_acerto': taxa_acerto
            })
        
        # Evolução ao longo do tempo
        resultados_timeline = Resultado.objects.filter(aluno=aluno).order_by('data_correcao').values(
            'simulado__titulo', 'pontuacao', 'data_correcao'
        )
        
        dashboard_data = {
            'aluno': aluno.name,
            'total_simulados': total_simulados,
            'media_geral': media_geral,
            'desempenho_disciplinas': desempenho_disciplinas,
            'evolucao_timeline': list(resultados_timeline)
        }
        
        serializer = DashboardAlunoSerializer(data=dashboard_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

class QuestaoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar e detalhar questões.
    """
    queryset = Questao.objects.all()
    serializer_class = QuestaoSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def por_disciplina(self, request):
        """Retorna questões filtradas por disciplina"""
        disciplina = request.query_params.get('disciplina', None)
        if disciplina:
            questoes = Questao.objects.filter(disciplina=disciplina)
            serializer = self.get_serializer(questoes, many=True)
            return Response(serializer.data)
        return Response({'error': 'Parâmetro disciplina é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

class SimuladoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para listar e detalhar simulados.
    """
    serializer_class = SimuladoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna simulados disponíveis para o usuário"""
        user = self.request.user
        # Obter simulados associados às turmas do usuário
        return Simulado.objects.filter(classes__user=user).distinct()

    @action(detail=True, methods=['get'])
    def gabarito(self, request, pk=None):
        """Retorna o gabarito de um simulado específico"""
        simulado = self.get_object()
        questoes_simulado = QuestaoSimulado.objects.filter(simulado=simulado).order_by('ordem')
        
        gabarito = {}
        for item in questoes_simulado:
            gabarito[str(item.ordem)] = item.questao.resposta_correta
            
        return Response({
            'simulado_id': simulado.id,
            'titulo': simulado.titulo,
            'gabarito': gabarito
        })

    @action(detail=True, methods=['post'])
    def corrigir(self, request, pk=None):
        """Corrige um simulado baseado nas respostas enviadas"""
        simulado = self.get_object()
        serializer = CartaoRespostaSerializer(data=request.data)
        
        if serializer.is_valid():
            aluno_id = serializer.validated_data['aluno_id']
            respostas = serializer.validated_data['respostas']
            
            try:
                aluno = Student.objects.get(id=aluno_id)
            except Student.DoesNotExist:
                return Response({'error': 'Aluno não encontrado'}, status=status.HTTP_404_NOT_FOUND)

            # Lógica de correção
            resultado = self.processar_correcao(simulado, aluno, respostas)
            
            return Response(resultado)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def processar_correcao(self, simulado, aluno, respostas):
        """Processa a correção do simulado e salva os resultados"""
        # Obter o gabarito do simulado
        questoes_simulado = QuestaoSimulado.objects.filter(simulado=simulado).order_by('ordem')
        gabarito = {str(item.ordem): item.questao.resposta_correta for item in questoes_simulado}
        
        # Calcular pontuação e detalhes
        total_questoes = len(gabarito)
        acertos = 0
        detalhes = []
        
        for ordem, resposta_aluno in respostas.items():
            questao_simulado = get_object_or_404(QuestaoSimulado, simulado=simulado, ordem=int(ordem))
            questao = questao_simulado.questao
            resposta_correta = gabarito.get(ordem)
            acertou = resposta_aluno == resposta_correta
            
            if acertou:
                acertos += 1
                
            detalhes.append({
                'ordem': ordem,
                'questao_id': questao.id,
                'disciplina': questao.disciplina,
                'resposta_aluno': resposta_aluno,
                'resposta_correta': resposta_correta,
                'acertou': acertou
            })
            
        pontuacao = (acertos / total_questoes) * 100 if total_questoes > 0 else 0
        
        # Salvar o resultado no banco
        resultado = Resultado.objects.create(
            aluno=aluno,
            simulado=simulado,
            pontuacao=pontuacao,
            total_questoes=total_questoes,
            acertos=acertos,
            data_correcao=timezone.now()
        )
        
        # Salvar detalhes de cada resposta
        for detalhe in detalhes:
            questao = Questao.objects.get(id=detalhe['questao_id'])
            DetalhesResposta.objects.create(
                resultado=resultado,
                questao=questao,
                ordem=detalhe['ordem'],
                resposta_aluno=detalhe['resposta_aluno'],
                resposta_correta=detalhe['resposta_correta'],
                acertou=detalhe['acertou']
            )
        
        return {
            'id': resultado.id,
            'aluno': aluno.name,
            'simulado': simulado.titulo,
            'pontuacao': pontuacao,
            'acertos': acertos,
            'total_questoes': total_questoes,
            'data_correcao': resultado.data_correcao,
            'detalhes': detalhes
        }

class CustomAuthToken(ObtainAuthToken):
    """
    API para autenticação e obtenção de token.
    Retorna o token junto com informações do usuário.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.get_full_name() or user.username,
            'is_staff': user.is_staff
        })

@api_view(['GET'])
@permission_classes([AllowAny])
def test_connection(request):
    """Endpoint simples para testar a conexão com a API"""
    return Response({"message": "Conexão bem-sucedida!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    """Retorna informações do usuário autenticado"""
    user = request.user
    return Response({
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'email': user.email,
        'is_staff': user.is_staff
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def app_config(request):
    """Endpoint para fornecer configurações para o aplicativo mobile"""
    disciplines = Questao.objects.values_list('disciplina', flat=True).distinct()
    classes = Class.objects.count()
    simulados = Simulado.objects.count()
    
    return Response({
        'disciplines': list(disciplines),
        'total_classes': classes,
        'total_simulados': simulados,
        'api_version': '1.0.0',
        'app_info': {
            'min_version': '1.0.0',
            'current_version': '1.0.0',
            'update_required': False
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def procesar_cartao_resposta(request):
    """Endpoint para receber dados de cartão resposta já processados pelo app Flutter"""
    if not all(key in request.data for key in ['simulado_id', 'aluno_id', 'respostas']):
        return Response({'error': 'Dados incompletos'}, status=status.HTTP_400_BAD_REQUEST)
        
    try:
        simulado = Simulado.objects.get(id=request.data['simulado_id'])
        aluno = Student.objects.get(id=request.data['aluno_id'])
    except (Simulado.DoesNotExist, Student.DoesNotExist):
        return Response({'error': 'Simulado ou aluno não encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    # Delegar a lógica de correção para o método do SimuladoViewSet
    viewset = SimuladoViewSet()
    resultado = viewset.processar_correcao(simulado, aluno, request.data['respostas'])
    
    return Response(resultado)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_classes(request):
    """
    Endpoint simplificado para listar todas as turmas do usuário.
    Útil para o app Flutter na tela de seleção.
    """
    classes = Class.objects.filter(user=request.user).order_by('name')
    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_class_students(request, class_id):
    """
    Endpoint simplificado para listar alunos de uma turma específica.
    Útil para o app Flutter na tela de seleção.
    """
    try:
        class_obj = Class.objects.get(id=class_id, user=request.user)
        students = Student.objects.filter(classes=class_obj).order_by('name')
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    except Class.DoesNotExist:
        return Response({"error": "Turma não encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_class_simulados(request, class_id):
    """
    Endpoint simplificado para listar simulados de uma turma específica.
    Útil para o app Flutter na tela de seleção.
    """
    try:
        class_obj = Class.objects.get(id=class_id, user=request.user)
        simulados = Simulado.objects.filter(classes=class_obj).order_by('-data_criacao')
        serializer = SimuladoSerializer(simulados, many=True)
        return Response(serializer.data)
    except Class.DoesNotExist:
        return Response({"error": "Turma não encontrada"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_token_request(request):
    """Debug view for token requests"""
    return Response({
        'received_data': request.data,
        'content_type': request.content_type,
        'auth_header': request.META.get('HTTP_AUTHORIZATION', None),
    })