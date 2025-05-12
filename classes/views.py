#classes/views.py
from asyncio.log import logger
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Avg, Count, Max, F, Q, Case, When, Value, IntegerField
from .models import Class, Student, StudentPerformance, StudentAnswer
from .forms import ClassForm, StudentForm
from .utils import extract_students_from_pdf, extract_students_from_excel, get_next_student_id
from questions.models import Simulado, QuestaoSimulado, Questao
from api.models import Resultado, DetalhesResposta
from collections import defaultdict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
import json


# Class views
@login_required
def class_list(request):
    classes = Class.objects.filter(user=request.user)
    return render(request, 'classes/class_list.html', {'classes': classes})

@login_required
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.user = request.user
            class_obj.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'classes/class_form.html', {'form': form})

@login_required
def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm(instance=class_obj)
    return render(request, 'classes/class_form.html', {'form': form})

@login_required
def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, user=request.user)
    if request.method == 'POST':
        class_obj.delete()
        return redirect('class_list')
    return render(request, 'classes/class_confirm_delete.html', {'class': class_obj})

@login_required
def class_students(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, user=request.user)
    students = class_obj.students.all().order_by('student_id')
    return render(request, 'classes/class_students.html', {
        'class': class_obj, 
        'students': students
    })

@login_required
def class_add_students(request, pk):
    class_obj = get_object_or_404(Class, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            
            # Verificar se o student_id já existe
            if Student.objects.filter(user=request.user, student_id=student.student_id).exists():
                messages.error(request, f'Número de matrícula {student.student_id} já existe.')
                return redirect('class_edit', pk=pk)
                
            student.save()
            class_obj.students.add(student)
            messages.success(request, f'Aluno {student.name} adicionado com sucesso.')
    return redirect('class_students', pk=pk)

@login_required
def class_remove_student(request, class_pk, student_pk):
    class_obj = get_object_or_404(Class, pk=class_pk, user=request.user)
    student = get_object_or_404(Student, pk=student_pk, user=request.user)
    if request.method == 'POST':
        class_obj.students.remove(student)
        messages.success(request, f'Aluno {student.name} removido da turma {class_obj.name}.')
    return redirect('class_students', pk=class_pk)

# Student views
@login_required
def student_list(request):
    students = Student.objects.filter(user=request.user).order_by('student_id')
    return render(request, 'classes/student_list.html', {'students': students})

@login_required
def student_form(request):
    class_pk = request.GET.get('class_pk')
    initial_data = {'class_pk': class_pk} if class_pk else {}

    if request.method == 'POST':
        form = StudentForm(request.POST, initial=initial_data)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            
            # Verificar se o student_id já existe
            if Student.objects.filter(user=request.user, student_id=student.student_id).exists():
                messages.error(request, f'Número de matrícula {student.student_id} já existe.')
                return render(request, 'classes/student_form.html', {
                    'form': form,
                    'class_pk': class_pk
                })
                
            student.save()
            
            # Associar à turma se especificado
            if class_pk:
                try:
                    class_obj = get_object_or_404(Class, pk=class_pk, user=request.user)
                    student.classes.add(class_obj)
                    return redirect('class_students', pk=class_pk)
                except Class.DoesNotExist:
                    pass
                    
            messages.success(request, 'Aluno adicionado com sucesso!')
            return redirect('student_list')
    else:
        # Sugerir próximo ID disponível
        next_id = get_next_student_id(request.user)
        initial_data['student_id'] = next_id
        form = StudentForm(initial=initial_data)

    return render(request, 'classes/student_form.html', {
        'form': form,
        'class_pk': class_pk
    })

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk, user=request.user)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações do aluno atualizadas com sucesso.')
            
            # Redirecionar para a última turma, caso exista
            if student.classes.exists():
                return redirect('class_students', pk=student.classes.first().id)
            return redirect('student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'classes/student_form.html', {'form': form})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk, user=request.user)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Aluno removido com sucesso.')
        return redirect('student_list')
    return render(request, 'classes/student_confirm_delete.html', {'student': student})

def preparar_dados_progresso_aluno(simulados):
    """
    Prepara dados para o gráfico de progresso simplificado do aluno.
    Retorna apenas os dados essenciais para um gráfico minimalista.
    
    Args:
        simulados: Lista de simulados realizados pelo aluno
        
    Returns:
        Dicionário com dados formatados para o gráfico simplificado
    """
    import json
    from django.utils.safestring import mark_safe
    
    try:
        # Verificar se há simulados
        if not simulados:
            # Sem simulados
            return {
                'labels': [],
                'valores': [],
                'simulados_info': []
            }
        
        # Ordenar simulados por data (do mais antigo para o mais recente)
        simulados_ordenados = sorted(simulados, key=lambda x: x['data'])
        
        # Extrair dados para o gráfico
        datas = [sim['data'].strftime('%d/%m/%Y') for sim in simulados_ordenados]
        notas = [float(sim['nota']) for sim in simulados_ordenados]
        
        # Dados simplificados dos simulados para tooltips
        info_simulados = []
        for sim in simulados_ordenados:
            info_simulados.append({
                'simulado': sim['simulado'],
                'acertos': sim['acertos'],
                'total': sim['total']
            })
        
        # Retornar apenas os dados necessários para o gráfico simplificado
        dados_grafico = {
            'labels': datas,
            'valores': notas,
            'simulados_info': info_simulados
        }
        
        return dados_grafico
        
    except Exception as e:
        # Em caso de erro, retornar dados vazios para evitar quebras na UI
        import logging
        logging.error(f"Erro ao preparar dados do gráfico: {str(e)}")
        
        return {
            'labels': [],
            'valores': [],
            'simulados_info': [],
            'erro': str(e)
        }

@login_required
def student_dashboard(request, student_id):
    import json
    from decimal import Decimal
    from collections import defaultdict
    import logging
    
    student = get_object_or_404(Student, id=student_id, user=request.user)
    classes = student.classes.filter(user=request.user)
    
    # Obter os resultados de simulados do sistema web
    performances = StudentPerformance.objects.filter(student=student).order_by('-date_taken')
    
    # Obter os resultados do aplicativo Flutter
    from api.models import Resultado, DetalhesResposta
    app_resultados = Resultado.objects.filter(aluno=student).order_by('-data_correcao')
    
    # Verificar se cada resultado ainda existe antes de incluir
    simulados_app = []
    for r in app_resultados:
        # Verificar se o resultado ainda tem detalhes de respostas
        if DetalhesResposta.objects.filter(resultado=r).exists():
            simulados_app.append({
                'data': r.data_correcao, 
                'tipo': 'App',
                'simulado': r.simulado.titulo,
                'simulado_id': r.simulado.id,
                'nota': float(r.pontuacao),
                'acertos': r.acertos,
                'total': r.total_questoes,
                'id': r.id,
                'fonte': 'app',
                'versao': r.versao if hasattr(r, 'versao') and r.versao else 'Padrão'
            })
    
    # Combinar todos os simulados
    todos_simulados_raw = simulados_app 
    
    # Agrupar por título de simulado e manter apenas o mais recente
    simulados_mais_recentes = {}
    for sim in todos_simulados_raw:
        # A chave é o título do simulado
        titulo = sim['simulado']
        # Se ainda não tivermos esse título ou se a data for mais recente, atualizamos
        if titulo not in simulados_mais_recentes or sim['data'] > simulados_mais_recentes[titulo]['data']:
            simulados_mais_recentes[titulo] = sim
    
    # Converter o dicionário em lista e ordenar por data (mais recentes primeiro)
    todos_simulados = sorted(
        simulados_mais_recentes.values(),
        key=lambda x: x['data'],
        reverse=True
    )
    
    # Simulados recentes (já agrupados e filtrados)
    simulados_recentes = todos_simulados[:5]
    
    # Estatísticas gerais (agora com simulados únicos)
    total_simulados = len(todos_simulados)
    
    # Calcular média geral dos simulados únicos
    if total_simulados > 0:
        media_geral = sum(sim['nota'] for sim in todos_simulados) / total_simulados
    else:
        media_geral = 0
    
    # Usar a função auxiliar simplificada para preparar dados do gráfico
    dados_progresso = preparar_dados_progresso_aluno(todos_simulados)
    
    # Preparar todos os dados em um único JSON para o template
    try:
        progresso_json = json.dumps(dados_progresso)
    except Exception as e:
        logging.error(f"Erro ao serializar dados do progresso: {str(e)}")
        # Dados fallback caso ocorra erro
        progresso_json = json.dumps({
            'labels': [],
            'valores': [],
            'simulados_info': []
        })
    
    context = {
        'student': student,
        'classes': classes,
        'total_simulados': total_simulados,
        'media_geral': media_geral,
        'simulados_recentes': simulados_recentes,
        'todos_simulados': todos_simulados,
        # Mantemos esses para compatibilidade
        'performances': performances,
        'app_resultados': app_resultados,
        # Todos os dados do gráfico simplificado em um único JSON
        'progresso_json': progresso_json
    }
    
    return render(request, 'classes/student_dashboard.html', context)


def normalizar_nivel(nivel):
    """Normaliza o nível de dificuldade para um formato padrão"""
    if not nivel:
        return 'medio'
        
    nivel = str(nivel).lower()
    
    if nivel in ['facil', 'fácil', 'f']:
        return 'facil'
    elif nivel in ['medio', 'médio', 'm']:
        return 'medio'
    elif nivel in ['dificil', 'difícil', 'd']:
        return 'dificil'
    else:
        return 'medio'  # padrão

def calcular_estatisticas_nivel_disciplina(respostas, estatisticas_disciplina):
    """
    Calcula estatísticas de desempenho por nível de dificuldade e disciplina
    
    Args:
        respostas: Lista de respostas do aluno
        estatisticas_disciplina: Lista de estatísticas por disciplina
        
    Returns:
        Lista de dicionários com estatísticas por nível de dificuldade para cada disciplina
    """
    resultado = []
    
    for disciplina_stats in estatisticas_disciplina:
        disciplina = disciplina_stats['disciplina']
        
        # Inicializar contadores para cada nível
        niveis = {
            'facil': {'acertos': 0, 'total': 0},
            'medio': {'acertos': 0, 'total': 0},
            'dificil': {'acertos': 0, 'total': 0},
        }
        
        # Processar respostas para esta disciplina
        for resposta in respostas:
            if resposta['disciplina'] == disciplina:
                nivel_normalizado = normalizar_nivel(resposta.get('nivel', 'medio'))
                
                if nivel_normalizado in niveis:
                    niveis[nivel_normalizado]['total'] += 1
                    if resposta['acertou']:
                        niveis[nivel_normalizado]['acertos'] += 1
        
        # Calcular percentuais
        for nivel, dados in niveis.items():
            if dados['total'] > 0:
                dados['percentual'] = (dados['acertos'] / dados['total']) * 100
            else:
                dados['percentual'] = 0
        
        # Adicionar ao resultado
        resultado.append({
            'disciplina': disciplina,
            'total_acertos': disciplina_stats['acertos'],
            'total_questoes': disciplina_stats['total'],
            'percentual_total': disciplina_stats['percentual'],
            'facil': niveis['facil'],
            'medio': niveis['medio'],
            'dificil': niveis['dificil']
        })
        
    return resultado

@login_required
def student_simulado_detail(request, student_id, simulado_id, fonte="web", resultado_id=None):
    """Ver o desempenho detalhado de um aluno em um simulado específico"""
    from collections import defaultdict
    import logging
    
    logger = logging.getLogger(__name__)
    
    student = get_object_or_404(Student, id=student_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Função auxiliar para normalização de nomes de disciplinas e assuntos
    def normalizar_nome(texto):
        """Normaliza nomes de disciplinas e assuntos para formato consistente"""
        if not texto:
            return "Não definido"
            
        # Converter para título (primeira letra de cada palavra maiúscula)
        texto = texto.strip().title()
        
        # Correções específicas para disciplinas
        correcoes = {
            'Biologia': 'Biologia',
            'Matematica': 'Matemática',
            'Fisica': 'Física',
            'Quimica': 'Química',
            'Historia': 'História',
            'Portugues': 'Português',
            'Ingles': 'Inglês',
            'Espanhol': 'Espanhol',
            'Geografia': 'Geografia',
            'Filosofia': 'Filosofia',
            'Sociologia': 'Sociologia'
        }
        
        # Aplicar correções se o texto existir no dicionário
        for chave, valor in correcoes.items():
            if texto.lower() == chave.lower():
                return valor
        
        return texto
    
    # Inicializar variáveis para estatísticas
    acertos_por_disciplina = defaultdict(lambda: {"acertos": 0, "total": 0})
    acertos_por_assunto = defaultdict(lambda: {"acertos": 0, "total": 0})
    respostas = []
    resultado = None  # Inicializar a variável resultado
    
    # Função para mapear o código do nível para o nome por extenso
    def mapear_nivel(nivel_codigo):
        nivel_mapeado = {
            'F': 'facil',
            'M': 'medio',
            'D': 'dificil'
        }.get(nivel_codigo, 'medio')
        return nivel_mapeado
    
    # Função auxiliar para obter o gabarito de uma versão específica
    def get_gabarito_versao(versao):
        if not versao or not hasattr(simulado, 'gabaritos_gerados') or not simulado.gabaritos_gerados:
            return {}
        
        try:
            # Verificar se a versão começa com 'versao' e extrair o número
            if isinstance(versao, str) and versao.startswith('versao'):
                versao_numero = versao.replace('versao', '')
                versao_indice = int(versao_numero) - 1
            else:
                # Caso contrário, tentar converter diretamente
                versao_indice = int(versao) - 1
                
            if 0 <= versao_indice < len(simulado.gabaritos_gerados):
                return simulado.gabaritos_gerados[versao_indice].get('gabarito', {})
            else:
                logger.warning(f"Versão {versao} fora do intervalo disponível para o simulado {simulado_id}")
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"Erro ao obter gabarito da versão {versao}: {str(e)}")
        
        return {}
    
    # NOVO: Função para obter os dados da questão correta baseada na ordem e versão do simulado
    def obter_dados_questao_correta(ordem, versao):
        try:
            # Converter a versão para índice (base 0)
            versao_indice = None
            if isinstance(versao, str) and versao.startswith('versao'):
                versao_indice = int(versao.replace('versao', '')) - 1
            else:
                versao_indice = int(versao) - 1
            
            # Verificar se o índice da versão é válido
            if not hasattr(simulado, 'gabaritos_gerados') or not simulado.gabaritos_gerados or versao_indice < 0 or versao_indice >= len(simulado.gabaritos_gerados):
                logger.warning(f"Versão inválida ou gabaritos não gerados: {versao}")
                return "Não definido", "Não definido", "medio"
            
            # Obter os dados da versão específica
            versao_data = simulado.gabaritos_gerados[versao_indice]
            
            # Verificar se a estrutura de dados da versão é válida
            if not isinstance(versao_data, dict) or 'questoes' not in versao_data:
                # Tentar um fallback para a primeira versão
                if simulado.gabaritos_gerados and len(simulado.gabaritos_gerados) > 0 and 'questoes' in simulado.gabaritos_gerados[0]:
                    logger.warning(f"Usando ordem da primeira versão como fallback para versão {versao}")
                    versao_data = simulado.gabaritos_gerados[0]
                else:
                    logger.error(f"Estrutura de dados inválida para versão {versao}")
                    return "Não definido", "Não definido", "medio"
            
            # Obter a lista de questões na ordem desta versão específica
            ordem_questoes = versao_data.get('questoes', [])
            
            # Verificar se temos uma lista válida de questões
            if not ordem_questoes or not isinstance(ordem_questoes, list):
                logger.error(f"Lista de questões inválida para versão {versao}")
                return "Não definido", "Não definido", "medio"
            
            # Converter ordem para inteiro, se for string
            ordem_int = ordem
            if isinstance(ordem, str):
                ordem_int = int(''.join(filter(str.isdigit, ordem)))
            
            # Índice ajustado (arrays são base 0, ordens são base 1)
            indice = ordem_int - 1
            
            # Verificar se o índice é válido
            if indice < 0 or indice >= len(ordem_questoes):
                logger.error(f"Índice de questão inválido: {indice} (ordem {ordem}) para versão {versao} com {len(ordem_questoes)} questões")
                return "Não definido", "Não definido", "medio"
            
            # Obter o ID da questão correspondente a esta ordem na versão específica
            questao_id = ordem_questoes[indice]
            
            # Buscar a questão original do banco de dados
            try:
                questao = Questao.objects.get(id=questao_id)
                disciplina = normalizar_nome(questao.disciplina if hasattr(questao, 'disciplina') else "")
                assunto = normalizar_nome(questao.conteudo if hasattr(questao, 'conteudo') else "")
                nivel = mapear_nivel(questao.nivel_dificuldade if hasattr(questao, 'nivel_dificuldade') else 'M')
                
                # Log para debug
                logger.debug(f"Versão {versao}, Ordem {ordem}: Questão ID={questao_id}, Disciplina={disciplina}, Assunto={assunto}")
                
                return disciplina, assunto, nivel
            except Questao.DoesNotExist:
                logger.error(f"Questão ID {questao_id} não encontrada")
                
        except Exception as e:
            logger.error(f"Erro ao obter dados da questão para ordem {ordem}, versão {versao}: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        return "Não definido", "Não definido", "medio"
    
    # Verificar a fonte dos dados (app ou web)
    if fonte == "app":
        from api.models import Resultado, DetalhesResposta
        resultado = get_object_or_404(Resultado, id=resultado_id, aluno=student)
        
        # Obter a versão do simulado do modelo Resultado
        versao_usada = resultado.versao
        
        # Obter gabarito específico para a versão
        gabarito_versao = get_gabarito_versao(versao_usada)
        
        # Obter as respostas detalhadas
        detalhes = DetalhesResposta.objects.filter(resultado=resultado).select_related('questao')
        
        # Verificar se há detalhes antes de processar
        if not detalhes.exists():
            messages.warning(request, "Os detalhes deste resultado foram excluídos.")
            return redirect('student_dashboard', student_id=student.id)
    
        # Processar as respostas para estatísticas e display
        for detalhe in detalhes:
            questao = detalhe.questao
            
            # Obter dados corretos da questão baseados na ordem e versão
            disciplina, assunto, nivel_extenso = obter_dados_questao_correta(detalhe.ordem, versao_usada)
            
            # Incrementar contadores para estatísticas
            acertos_por_disciplina[disciplina]["total"] += 1
            acertos_por_assunto[assunto]["total"] += 1
            
            if detalhe.acertou:
                acertos_por_disciplina[disciplina]["acertos"] += 1
                acertos_por_assunto[assunto]["acertos"] += 1
            
            # Determinar a resposta correta com base na versão
            resposta_correta = detalhe.resposta_correta  # Valor padrão
            
            # Tentar obter o gabarito específico da versão para esta questão
            num_questao = str(detalhe.ordem)
            if gabarito_versao and num_questao in gabarito_versao:
                # Tentar obter a resposta do gabarito específico da versão
                tipo_key = 'tipo1'  # Ajuste conforme necessário
                if tipo_key in gabarito_versao[num_questao]:
                    resposta_correta = gabarito_versao[num_questao][tipo_key]
                    logger.debug(f"Usando gabarito da versão {versao_usada} para questão {num_questao}")
            
            respostas.append({
                'questao': questao,
                'ordem': detalhe.ordem,
                'resposta_aluno': detalhe.resposta_aluno,
                'resposta_correta': resposta_correta,
                'acertou': detalhe.acertou,
                'disciplina': disciplina,
                'assunto': assunto,
                'nivel': nivel_extenso
            })
        
        # Informações do desempenho
        performance = {
            'score': resultado.pontuacao,
            'correct_answers': resultado.acertos,
            'total_questions': resultado.total_questoes,
            'versao': versao_usada or "Padrão"
        }
        
    else:  # fonte == "web"
        # Verificar se o aluno está em alguma turma que tem acesso ao simulado
        if not student.classes.filter(id__in=simulado.classes.all()).exists():
            messages.error(request, "Este aluno não tem acesso a este simulado.")
            return redirect('student_dashboard', student_id=student_id)
        
        # Obter desempenho do aluno
        performance = get_object_or_404(StudentPerformance, student=student, simulado=simulado)
        
        # Obter a versão do simulado para este aluno
        # 1. Verificar se há um campo versão no modelo StudentPerformance
        versao_usada = None
        if hasattr(performance, 'versao') and performance.versao:
            versao_usada = performance.versao
        
        # 2. Se não tiver, verificar na sessão
        if not versao_usada:
            versao_usada = request.session.get(f'simulado_{simulado_id}_versao')
        
        # 3. Verificar na URL
        if not versao_usada:
            versao_usada = request.GET.get('versao')
        
        # 4. Se ainda não tiver, usar versão padrão
        versao_usada = versao_usada or "1"
        
        # Obter gabarito específico para a versão
        gabarito_versao = get_gabarito_versao(versao_usada)
        
        # Obter respostas do aluno - importante usar select_related para evitar consultas N+1
        student_answers = StudentAnswer.objects.filter(
            student=student, 
            simulado=simulado
        ).select_related('question__questao').order_by('question__ordem')
        
        # Processar as respostas para estatísticas e display
        for answer in student_answers:
            questao_simulado = answer.question
            
            # Obter dados corretos da questão baseados na ordem e versão
            disciplina, assunto, nivel_extenso = obter_dados_questao_correta(questao_simulado.ordem, versao_usada)
            
            # Adicionar logs para debug
            logger.debug(f"Questão {questao_simulado.ordem}: disciplina={disciplina}, assunto={assunto}")
            
            # Incrementar contadores para estatísticas
            acertos_por_disciplina[disciplina]["total"] += 1
            acertos_por_assunto[assunto]["total"] += 1
            
            if answer.is_correct:
                acertos_por_disciplina[disciplina]["acertos"] += 1
                acertos_por_assunto[assunto]["acertos"] += 1
            
            # Determinar a resposta correta com base na versão
            resposta_correta = answer.question.questao.resposta_correta  # Valor padrão inicial
            
            # Tentar obter o gabarito específico da versão para esta questão
            num_questao = str(questao_simulado.ordem)
            if gabarito_versao and num_questao in gabarito_versao:
                # Obter a resposta do gabarito específico
                tipo_key = 'tipo1'  # Ajuste conforme necessário
                if tipo_key in gabarito_versao[num_questao]:
                    resposta_correta = gabarito_versao[num_questao][tipo_key]
                    logger.debug(f"Usando gabarito da versão {versao_usada} para questão {num_questao}")
            
            respostas.append({
                'questao': answer.question.questao,
                'ordem': questao_simulado.ordem,
                'resposta_aluno': answer.chosen_option,
                'resposta_correta': resposta_correta,
                'acertou': answer.is_correct,
                'disciplina': disciplina,
                'assunto': assunto,
                'nivel': nivel_extenso
            })
        
        # Adicionar informação de versão ao objeto performance para o template
        if isinstance(performance, dict):
            performance['versao'] = versao_usada
        else:
            # Se for um objeto do modelo, adicionar a versão como atributo
            performance.versao = versao_usada
    
    # Função para garantir a ordenação correta das respostas por número da questão
    def ordem_numerica(item):
        ordem = item['ordem']
        # Converter para inteiro, independentemente do formato
        if isinstance(ordem, str):
            # Remover caracteres não numéricos, se existirem
            apenas_numeros = ''.join(c for c in ordem if c.isdigit())
            return int(apenas_numeros) if apenas_numeros else 0
        return ordem if isinstance(ordem, int) else 0

    # Ordenar questões numericamente
    respostas = sorted(respostas, key=ordem_numerica)
    
    # Verificar se as questões e respostas estão completas - para debug
    logger.debug(f"Total de respostas: {len(respostas)}")
    for i, resp in enumerate(respostas[:5]):  # Mostrar as primeiras 5 para debug
        logger.debug(f"Resposta {i+1}: ordem={resp['ordem']}, disciplina={resp['disciplina']}, assunto={resp['assunto']}")
    
    # Calcular percentuais para estatísticas
    estatisticas_disciplina = []
    for disciplina, dados in acertos_por_disciplina.items():
        if dados["total"] > 0:
            percentual = (dados["acertos"] / dados["total"]) * 100
            estatisticas_disciplina.append({
                'disciplina': disciplina,
                'acertos': dados["acertos"],
                'total': dados["total"],
                'percentual': percentual
            })
    
    estatisticas_assunto = []
    for assunto, dados in acertos_por_assunto.items():
        if dados["total"] > 0:
            percentual = (dados["acertos"] / dados["total"]) * 100
            estatisticas_assunto.append({
                'assunto': assunto,
                'acertos': dados["acertos"],
                'total': dados["total"],
                'percentual': percentual
            })
    
    # Ordenar estatísticas do maior para o menor percentual
    estatisticas_disciplina.sort(key=lambda x: x['percentual'], reverse=True)
    estatisticas_assunto.sort(key=lambda x: x['percentual'], reverse=True)
    
    # NOVA ADIÇÃO: Calcular estatísticas por nível de dificuldade e disciplina
    estatisticas_nivel_disciplina = calcular_estatisticas_nivel_disciplina(respostas, estatisticas_disciplina)
    
    context = {
        'student': student,
        'simulado': simulado,
        'performance': performance,
        'respostas': respostas,
        'estatisticas_disciplina': estatisticas_disciplina,
        'estatisticas_assunto': estatisticas_assunto,
        'estatisticas_nivel_disciplina': estatisticas_nivel_disciplina,  # Nova estatística adicionada
        'fonte': fonte,
        'versao_usada': versao_usada or "Padrão",
        'resultado': resultado
    }
    
    return render(request, 'classes/student_simulado_detail.html', context)

@login_required
def class_select_simulado(request, class_id):
    """Página para selecionar um simulado específico da turma para visualizar o desempenho"""
    from api.models import Resultado
    from django.db.models import Avg, Count
    from decimal import Decimal
    
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    
    # Obter todos os simulados associados a esta turma
    simulados = Simulado.objects.filter(classes=class_obj).order_by('-data_criacao')
    
    # Contar alunos na turma
    students_count = class_obj.students.count()
    
    # Número total de resultados para esta turma (app + web)
    total_resultados = 0
    
    # Para cada simulado, adicionar informações de participação e desempenho
    for simulado in simulados:
        # Contar resultados do sistema web
        web_count = StudentPerformance.objects.filter(
            student__in=class_obj.students.all(),
            simulado=simulado
        ).count()
        
        # Contar resultados do app
        app_count = Resultado.objects.filter(
            aluno__in=class_obj.students.all(),
            simulado=simulado
        ).count()
        
        # Total de participantes neste simulado (sem duplicar alunos)
        students_with_web = set(StudentPerformance.objects.filter(
            student__in=class_obj.students.all(),
            simulado=simulado
        ).values_list('student_id', flat=True))
        
        students_with_app = set(Resultado.objects.filter(
            aluno__in=class_obj.students.all(),
            simulado=simulado
        ).values_list('aluno_id', flat=True))
        
        # União dos conjuntos para obter total único de alunos
        all_participants = students_with_web.union(students_with_app)
        total_participants = len(all_participants)
        
        # Atualizar o contador total de resultados
        total_resultados += (web_count + app_count)
        
        # Calcular média de notas do sistema web
        web_avg = StudentPerformance.objects.filter(
            student__in=class_obj.students.all(),
            simulado=simulado
        ).aggregate(avg=Avg('score'))['avg'] or Decimal('0')
        
        # Certifique-se de que web_avg é um Decimal
        if not isinstance(web_avg, Decimal):
            web_avg = Decimal(str(web_avg))
        
        # Calcular média de notas do app
        app_avg_raw = Resultado.objects.filter(
            aluno__in=class_obj.students.all(),
            simulado=simulado
        ).aggregate(avg=Avg('pontuacao'))['avg'] or 0
        
        # Converter app_avg para Decimal
        app_avg = Decimal(str(app_avg_raw))
        
        # Calcular média ponderada com base na quantidade de resultados
        if web_count + app_count > 0:
            media = (web_avg * web_count + app_avg * app_count) / Decimal(web_count + app_count)
            media_formatada = f"{media:.2f}"
        else:
            media_formatada = "N/A"
        
        # Adicionar atributos ao objeto simulado
        simulado.participantes = total_participants
        simulado.media = media_formatada
    
    context = {
        'class': class_obj,
        'simulados': simulados,
        'students_count': students_count,
        'total_resultados': total_resultados
    }
    
    return render(request, 'classes/class_select_simulado.html', context)


@login_required
def app_resultados_limpar(request):
    """Página para excluir todos os dados de resultados vindos do aplicativo Flutter."""
    from api.models import Resultado, DetalhesResposta
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Obter estatísticas para exibição
    total_resultados = Resultado.objects.filter(aluno__user=request.user).count()
    total_detalhes = DetalhesResposta.objects.filter(resultado__aluno__user=request.user).count()
    alunos_afetados = Resultado.objects.filter(aluno__user=request.user).values('aluno').distinct().count()
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao')
        
        # Verificar se o usuário marcou a confirmação
        if confirmacao:
            try:
                logger.info(f"Iniciando exclusão de dados do app para usuário {request.user.id}")
                
                # 1. Primeiro excluir os detalhes (chave estrangeira)
                detalhes_excluidos = DetalhesResposta.objects.filter(
                    resultado__aluno__user=request.user
                ).delete()
                
                # 2. Depois excluir os resultados
                resultados_excluidos = Resultado.objects.filter(
                    aluno__user=request.user
                ).delete()
                
                # 3. Limpar possíveis dados em cache da sessão
                # Lista de chaves que podem conter dados relacionados
                cache_keys = [
                    'simulados_recentes', 
                    'app_resultados', 
                    'dashboard_data',
                    'resultados_recentes'
                ]
                
                for key in cache_keys:
                    if key in request.session:
                        del request.session[key]
                
                # Salvar mudanças na sessão
                request.session.modified = True
                
                logger.info(f"Exclusão concluída para usuário {request.user.id}. Detalhes: {detalhes_excluidos}, Resultados: {resultados_excluidos}")
                
                # Redirecionar com mensagem de sucesso para a página de simulados
                messages.success(
                    request, 
                    f"Dados excluídos com sucesso! Foram removidos {total_resultados} resultados e {total_detalhes} respostas detalhadas."
                )
                return redirect('class_list')  # Redirecionando para simulado_list em vez de dashboard
                
            except Exception as e:
                logger.error(f"Erro ao excluir dados para usuário {request.user.id}: {str(e)}")
                messages.error(request, f"Erro ao excluir dados: {str(e)}")
        else:
            # Confirmação não marcada
            messages.error(request, "Por favor, marque a caixa de confirmação para confirmar a exclusão.")
    
    # Contexto para renderizar o template
    context = {
        'total_resultados': total_resultados,
        'total_detalhes': total_detalhes,
        'alunos_afetados': alunos_afetados,
    }
    
    return render(request, 'classes/app_resultados_limpar.html', context)

@login_required
def delete_student_performance(request, performance_id):
    """Excluir desempenho de um aluno em um simulado"""
    performance = get_object_or_404(StudentPerformance, id=performance_id)
    student = performance.student
    
    # Verificar se o usuário tem permissão para excluir este desempenho
    if student.user != request.user:
        messages.error(request, "Você não tem permissão para excluir este desempenho.")
        return redirect('student_list')
    
    if request.method == 'POST':
        # Excluir também as respostas do aluno para este simulado
        StudentAnswer.objects.filter(student=student, simulado=performance.simulado).delete()
        performance.delete()
        messages.success(request, "Dados do simulado excluídos com sucesso.")
        return redirect('student_dashboard', student_id=student.id)
    
    return render(request, 'classes/performance_confirm_delete.html', {
        'performance': performance,
        'student': student
    })

@login_required
def student_select_dashboard(request):
    classes = Class.objects.filter(user=request.user).order_by('name')
    selected_class = request.GET.get('class_id')

    if selected_class:
        students = Student.objects.filter(classes__id=selected_class, user=request.user).order_by('name')
    else:
        students = Student.objects.filter(user=request.user).order_by('name')

    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        if student_id:
            # Modificando para usar o ID primário
            return redirect('student_dashboard', student_id=student_id)
        else:
            messages.error(request, "Selecione um aluno.")
    
    context = {
        'classes': classes,
        'students': students,
        'selected_class': selected_class
    }
    return render(request, 'classes/student_select_dashboard.html', context)

# Import view
@login_required
def import_students(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        class_id = request.POST.get('class_id')
        
        try:
            class_obj = get_object_or_404(Class, id=class_id, user=request.user) if class_id else None
            if not class_obj:
                raise ValidationError("É necessário selecionar uma turma.")
            
            if file.name.endswith('.pdf'):
                students_data = extract_students_from_pdf(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                students_data = extract_students_from_excel(file)
            else:
                raise ValidationError("Formato de arquivo não suportado. Use PDF ou Excel.")
            
            created_count = 0
            next_id = get_next_student_id(request.user)
            
            for student_data in students_data:
                name = student_data['name']
                
                # Verificar se já existe um aluno com mesmo nome na mesma turma
                existing_student = Student.objects.filter(
                    user=request.user, 
                    name=name, 
                    classes=class_obj
                ).first()
                
                if existing_student:
                    # Se já existe, apenas adiciona à turma atual se necessário
                    if not existing_student.classes.filter(id=class_obj.id).exists():
                        existing_student.classes.add(class_obj)
                    continue
                
                # Criar novo aluno
                student = Student.objects.create(
                    name=name,
                    email=student_data.get('email'),  # Email é opcional
                    student_id=next_id,
                    user=request.user
                )
                next_id += 1
                created_count += 1
                class_obj.students.add(student)
            
            messages.success(request, f'Importação concluída! {created_count} alunos criados para a turma {class_obj.name}.')
            
        except Exception as e:
            messages.error(request, f'Erro na importação: {str(e)}')
            
        return redirect('class_students', pk=class_id)
        
    return render(request, 'classes/import_students.html', {
        'classes': Class.objects.filter(user=request.user)
    })

# API para aplicativo móvel
@login_required
def api_submit_answers(request):
    """API para receber respostas do aplicativo móvel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        data = request.POST
        student_id = data.get('student_id')
        simulado_id = data.get('simulado_id')
        versao = data.get('versao', '1')  # Obter a versão, padrão é '1'
        answers = data.getlist('answers[]')  # Lista de respostas no formato: questão_id:resposta
        
        # Validar dados
        if not student_id or not simulado_id or not answers:
            return JsonResponse({'error': 'Dados incompletos'}, status=400)
        
        student = get_object_or_404(Student, student_id=student_id, user=request.user)
        simulado = get_object_or_404(Simulado, id=simulado_id)
        
        # Verificar se o aluno está em alguma turma que tem acesso ao simulado
        if not student.classes.filter(id__in=simulado.classes.all()).exists():
            return JsonResponse({'error': 'Aluno não tem acesso a este simulado'}, status=403)
        
        # Processar respostas
        correct_answers = 0
        total_questions = len(answers)
        
        # Limpar respostas anteriores, se existirem
        StudentAnswer.objects.filter(student=student, simulado=simulado).delete()
        
        for answer_data in answers:
            try:
                question_id, chosen_option = answer_data.split(':')
                question = get_object_or_404(QuestaoSimulado, id=question_id, simulado=simulado)
                
                # Verificar se a resposta está correta
                correct_option = question.questao.resposta_correta
                is_correct = (chosen_option == correct_option)
                
                if is_correct:
                    correct_answers += 1
                
                # Salvar resposta
                StudentAnswer.objects.create(
                    student=student,
                    question=question,
                    simulado=simulado,
                    chosen_option=chosen_option,
                    is_correct=is_correct
                )
            except Exception as e:
                # Continuar mesmo se uma resposta der erro
                continue
        
        # Calcular pontuação
        if total_questions > 0:
            score = (correct_answers / total_questions) * 100
        else:
            score = 0
        
        # Salvar ou atualizar desempenho incluindo a versão
        performance, created = StudentPerformance.objects.update_or_create(
            student=student,
            simulado=simulado,
            defaults={
                'score': score,
                'correct_answers': correct_answers,
                'total_questions': total_questions,
                'versao': versao  # Adicionar a versão ao salvar
            }
        )
        
        return JsonResponse({
            'success': True,
            'student': student.name,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'versao': versao  # Incluir a versão na resposta
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def class_simulado_report(request, class_id, simulado_id):
    """Relatório de desempenho de uma turma em um simulado específico"""
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Verificar se o simulado está associado à turma
    if not simulado.classes.filter(id=class_id).exists():
        messages.error(request, "Este simulado não está associado a esta turma.")
        return redirect('class_list')
    
    # Estatísticas gerais
    students = class_obj.students.all()
    performances = StudentPerformance.objects.filter(
        student__in=students, 
        simulado=simulado
    )
    
    # Média da turma
    class_avg = performances.aggregate(avg=Avg('score'))['avg'] or 0
    
    # Total de alunos que fizeram o simulado
    total_participants = performances.count()
    
    # Análise por questão
    questions = QuestaoSimulado.objects.filter(simulado=simulado).order_by('ordem')
    
    question_stats = []
    for question in questions:
        # Respostas para esta questão
        answers = StudentAnswer.objects.filter(
            student__in=students, 
            simulado=simulado,
            question=question
        )
        
        # Total de acertos
        correct_count = answers.filter(is_correct=True).count()
        
        if answers.count() > 0:
            percent_correct = (correct_count / answers.count()) * 100
        else:
            percent_correct = 0
            
        # Contagem de respostas por alternativa
        option_counts = {}
        for option in ['A', 'B', 'C', 'D', 'E']:
            option_counts[option] = answers.filter(chosen_option=option).count()
        
        # Encontrar a alternativa mais marcada
        most_chosen = max(option_counts.items(), key=lambda x: x[1]) if option_counts else ('', 0)
        
        question_stats.append({
            'question': question,
            'correct': correct_count,
            'percent_correct': percent_correct,
            'option_counts': option_counts,
            'most_chosen': most_chosen[0],
            'most_chosen_count': most_chosen[1]
        })
    
    # Ordenar estatísticas para encontrar questões mais acertadas/erradas
    sorted_by_correct = sorted(question_stats, key=lambda x: x['percent_correct'], reverse=True)
    most_correct = sorted_by_correct[0] if sorted_by_correct else None
    least_correct = sorted_by_correct[-1] if sorted_by_correct else None
    
    context = {
        'class': class_obj,
        'simulado': simulado,
        'class_avg': class_avg,
        'total_participants': total_participants,
        'total_students': students.count(),
        'question_stats': question_stats,
        'most_correct': most_correct,
        'least_correct': least_correct,
        'performances': performances.order_by('-score')  # Ordenar por nota (decrescente)
    }
    
    return render(request, 'classes/class_simulado_report.html', context)

@login_required
def student_all_simulados(request, student_id):
    """Ver todos os simulados realizados por um aluno"""
    student = get_object_or_404(Student, id=student_id, user=request.user)
    performances = StudentPerformance.objects.filter(student=student).order_by('-date_taken')
    
    context = {
        'student': student,
        'performances': performances
    }
    
    return render(request, 'classes/student_all_simulados.html', context)

@login_required
def class_all_simulados(request, class_id):
    """Listar todos os simulados associados a uma turma"""
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    simulados = Simulado.objects.filter(classes=class_obj).order_by('-data_criacao')
    
    # Para cada simulado, calcular estatísticas básicas
    for simulado in simulados:
        performances = StudentPerformance.objects.filter(
            student__in=class_obj.students.all(),
            simulado=simulado
        )
        
        simulado.participants_count = performances.count()
        simulado.avg_score = performances.aggregate(avg=Avg('score'))['avg'] or 0
    
    context = {
        'class': class_obj,
        'simulados': simulados
    }
    
    return render(request, 'classes/class_all_simulados.html', context)

@login_required
def app_resultados(request):
    """Página para visualizar resultados enviados pelo aplicativo."""
    from api.models import Resultado, DetalhesResposta
    
    # Obter o ID do aluno da URL, se fornecido
    aluno_id = request.GET.get('aluno_id')
    turma_id = request.GET.get('turma_id')
    
    # Obter todas as turmas para o filtro
    turmas = Class.objects.filter(user=request.user).order_by('name')
    
    # Construir a consulta base
    query = Resultado.objects.filter(aluno__user=request.user)
    
    # Filtrar por aluno, se especificado
    aluno = None
    if aluno_id:
        try:
            aluno = Student.objects.get(id=aluno_id, user=request.user)
            query = query.filter(aluno=aluno)
        except Student.DoesNotExist:
            messages.error(request, f"Aluno com ID {aluno_id} não encontrado.")
    
    # Filtrar por turma, se especificado
    if turma_id:
        try:
            turma = Class.objects.get(id=turma_id, user=request.user)
            query = query.filter(aluno__classes=turma)
        except Class.DoesNotExist:
            messages.error(request, f"Turma com ID {turma_id} não encontrada.")
    
    # Obtém a lista de alunos para o filtro
    if turma_id:
        alunos = Student.objects.filter(classes__id=turma_id, user=request.user).order_by('name')
    else:
        alunos = Student.objects.filter(user=request.user).order_by('name')
    
    # Executar a consulta e obter os resultados
    resultados = query.order_by('-data_correcao')
    
    context = {
        'resultados': resultados,
        'aluno': aluno,
        'alunos': alunos,
        'turmas': turmas,
        'turma_id': turma_id,
        'aluno_id': aluno_id,
    }
    
    return render(request, 'classes/app_resultados.html', context)

@login_required
def app_resultado_detalhes(request, resultado_id):
    """Página para visualizar detalhes de um resultado específico."""
    from api.models import Resultado, DetalhesResposta
    
    try:
        resultado = Resultado.objects.get(id=resultado_id)
        detalhes = DetalhesResposta.objects.filter(resultado=resultado).order_by('ordem')
        
        context = {
            'resultado': resultado,
            'detalhes': detalhes
        }
        
        return render(request, 'classes/app_resultado_detalhes.html', context)
        
    except Resultado.DoesNotExist:
        messages.error(request, f"Resultado com ID {resultado_id} não encontrado.")
        return redirect('app_resultados')
    
@login_required
def resultado_detalhes_redirect(request, fonte, resultado_id):
    """Redireciona para a página de detalhes correta com base na fonte do resultado"""
    if fonte == 'app':
        return redirect('app_resultado_detalhes', resultado_id=resultado_id)
    else:  # web
        # Obtém o student_id e simulado_id a partir do resultado
        performance = get_object_or_404(StudentPerformance, id=resultado_id)
        return redirect('student_simulado_detail', 
                        student_id=performance.student.id,
                        simulado_id=performance.simulado.id)

@login_required
def resultado_detalhes(request, fonte, resultado_id):
    """Redireciona para o detalhe correto com base na fonte (app ou web)"""
    if fonte == "app":
        from api.models import Resultado
        resultado = get_object_or_404(Resultado, id=resultado_id)
        if request.user != resultado.aluno.user:
            messages.error(request, "Você não tem permissão para ver esse resultado.")
            return redirect('dashboard')
        
        return student_simulado_detail(
            request, 
            student_id=resultado.aluno.id, 
            simulado_id=resultado.simulado.id,
            fonte="app", 
            resultado_id=resultado.id
        )
    else:  # fonte == "web"
        performance = get_object_or_404(StudentPerformance, id=resultado_id)
        if request.user != performance.student.user:
            messages.error(request, "Você não tem permissão para ver esse resultado.")
            return redirect('dashboard')
        
        return student_simulado_detail(
            request, 
            student_id=performance.student.id, 
            simulado_id=performance.simulado.id,
            fonte="web"
        )
    
def class_performance_dashboard(request, class_id, simulado_id):
    """Dashboard de desempenho da turma em um simulado específico"""
    from collections import defaultdict
    from django.utils.safestring import mark_safe
    import json
    from api.models import Resultado, DetalhesResposta
    
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Verificar se o simulado está associado à turma
    if not simulado.classes.filter(id=class_id).exists():
        messages.error(request, "Este simulado não está associado a esta turma.")
        return redirect('class_list')
    
    # Obter todos os alunos da turma
    students = class_obj.students.all()
    
    # Obter desempenhos dos alunos no simulado (tanto do sistema web quanto do app)
    web_performances = StudentPerformance.objects.filter(
        student__in=students, 
        simulado=simulado
    ).select_related('student')
    
    # Importar modelo Resultado do app
    app_resultados = Resultado.objects.filter(
        aluno__in=students,
        simulado=simulado
    ).select_related('aluno')
    
    # IMPORTANTE: Verificar se cada resultado do app tem detalhes associados
    # Se não tiver, significa que foi parcialmente excluído
    app_resultados_validos = []
    for resultado in app_resultados:
        if DetalhesResposta.objects.filter(resultado=resultado).exists():
            app_resultados_validos.append(resultado)
        else:
            # Opcional: Excluir resultados sem detalhes para limpeza completa
            resultado.delete()
    
    # Dicionário para armazenar o melhor resultado por aluno
    # (chave: aluno_id, valor: dicionário com os dados do resultado)
    melhores_resultados = {}
    
    # Processar resultados do sistema web
    for perf in web_performances:
        aluno_id = perf.student.id
        resultado = {
            "aluno": perf.student,
            "nota": float(perf.score),
            "acertos": perf.correct_answers,
            "total": perf.total_questions,
            "fonte": "web"
        }
        
        # Se ainda não temos um resultado para este aluno, ou se a nota atual é maior
        if aluno_id not in melhores_resultados or resultado["nota"] > melhores_resultados[aluno_id]["nota"]:
            melhores_resultados[aluno_id] = resultado
    
    # Processar resultados do app (usando apenas os validados)
    for res in app_resultados_validos:
        aluno_id = res.aluno.id
        resultado = {
            "aluno": res.aluno,
            "nota": float(res.pontuacao),
            "acertos": res.acertos,
            "total": res.total_questoes,
            "fonte": "app"
        }
        
        # Se ainda não temos um resultado para este aluno, ou se a nota atual é maior
        if aluno_id not in melhores_resultados or resultado["nota"] > melhores_resultados[aluno_id]["nota"]:
            melhores_resultados[aluno_id] = resultado
    
    # Converter o dicionário para lista
    todos_resultados = list(melhores_resultados.values())
    
    # Verificar se temos resultados para exibir
    if not todos_resultados:
        messages.info(request, "Não há dados de resultados para este simulado nesta turma.")
        return redirect('class_select_simulado', class_id=class_id)
    
    # Consolidar estatísticas por disciplinas e assuntos da turma toda
    todas_disciplinas = defaultdict(lambda: {"acertos": 0, "total": 0})
    todos_assuntos = defaultdict(lambda: {"acertos": 0, "total": 0})
    
    # Processar respostas do sistema web
    for perf in web_performances:
        respostas = StudentAnswer.objects.filter(
            student=perf.student,
            simulado=simulado
        ).select_related('question__questao')
        
        for resp in respostas:
            questao = resp.question.questao
            disciplina = questao.disciplina
            assunto = questao.conteudo
            
            todas_disciplinas[disciplina]["total"] += 1
            todos_assuntos[assunto]["total"] += 1
            
            if resp.is_correct:
                todas_disciplinas[disciplina]["acertos"] += 1
                todos_assuntos[assunto]["acertos"] += 1
    
    # Processar respostas do app (apenas resultados válidos)
    for res in app_resultados_validos:
        detalhes = DetalhesResposta.objects.filter(
            resultado=res
        ).select_related('questao')
        
        for det in detalhes:
            questao = det.questao
            disciplina = questao.disciplina
            assunto = questao.conteudo
            
            todas_disciplinas[disciplina]["total"] += 1
            todos_assuntos[assunto]["total"] += 1
            
            if det.acertou:
                todas_disciplinas[disciplina]["acertos"] += 1
                todos_assuntos[assunto]["acertos"] += 1
    
    # Converter para listas e calcular percentuais
    estatisticas_disciplinas = []
    for nome, dados in todas_disciplinas.items():
        if dados["total"] > 0:
            percentual = (dados["acertos"] / dados["total"]) * 100
            estatisticas_disciplinas.append({
                "nome": nome,
                "acertos": dados["acertos"],
                "total": dados["total"],
                "percentual": percentual
            })
    
    estatisticas_assuntos = []
    for nome, dados in todos_assuntos.items():
        if dados["total"] > 0:
            percentual = (dados["acertos"] / dados["total"]) * 100
            estatisticas_assuntos.append({
                "nome": nome,
                "acertos": dados["acertos"],
                "total": dados["total"],
                "percentual": percentual
            })
    
    # Ordenar estatísticas do maior para o menor percentual
    estatisticas_disciplinas.sort(key=lambda x: x["percentual"], reverse=True)
    estatisticas_assuntos.sort(key=lambda x: x["percentual"], reverse=True)
    
    # Ordenar resultados dos alunos por nota (mais alta primeiro)
    todos_resultados.sort(key=lambda x: x["nota"], reverse=True)
    
    # Preparar dados para gráfico de notas dos alunos
    nomes_alunos = []
    notas_alunos = []
    
    for resultado in todos_resultados:
        nome_completo = resultado["aluno"].name
        # Pegar primeiro nome e último sobrenome para nomes muito longos
        partes_nome = nome_completo.split()
        if len(partes_nome) > 1:
            nome_formatado = f"{partes_nome[0]} {partes_nome[-1]}"
        else:
            nome_formatado = nome_completo
            
        nomes_alunos.append(nome_formatado)
        notas_alunos.append(float(resultado["nota"]))
    
    # Preparar dados para gráfico de disciplinas
    disciplinas_nomes = [d["nome"] for d in estatisticas_disciplinas[:5]]  # Top 5
    disciplinas_percentuais = [d["percentual"] for d in estatisticas_disciplinas[:5]]
    
    # Calcular média da turma
    media_turma = sum(r["nota"] for r in todos_resultados) / len(todos_resultados) if todos_resultados else 0
    
    # IMPORTANTE: Converter todos os dados para JSON usando json.dumps
    # E usar mark_safe para evitar escape de caracteres
    context = {
        'class': class_obj,
        'simulado': simulado,
        'total_participantes': len(todos_resultados),
        'total_alunos': students.count(),
        'media_turma': media_turma,
        'resultados': todos_resultados,
        'estatisticas_disciplinas': estatisticas_disciplinas,
        'estatisticas_assuntos': estatisticas_assuntos,
        # Dados para gráficos - convertidos para JSON e marcados como safe
        'nomes_alunos_json': mark_safe(json.dumps(nomes_alunos)),
        'notas_alunos_json': mark_safe(json.dumps(notas_alunos)),
        'disciplinas_nomes_json': mark_safe(json.dumps(disciplinas_nomes)),
        'disciplinas_percentuais_json': mark_safe(json.dumps(disciplinas_percentuais))
    }
    
    return render(request, 'classes/class_performance_dashboard.html', context)

@login_required
def class_simulado_limpar(request, class_id, simulado_id):
    """Excluir dados de um simulado específico para uma turma específica"""
    from api.models import Resultado, DetalhesResposta
    
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Verificar se o simulado está associado à turma
    if not simulado.classes.filter(id=class_id).exists():
        messages.error(request, "Este simulado não está associado a esta turma.")
        return redirect('class_list')
    
    if request.method == 'POST':
        confirmacao = request.POST.get('confirmacao')
        
        if confirmacao == 'on':
            try:
                # Obter alunos da turma
                students = class_obj.students.all()
                
                # 1. Excluir dados do sistema web
                performances = StudentPerformance.objects.filter(
                    student__in=students,
                    simulado=simulado
                )
                
                # Obter IDs das performances para excluir respostas
                performance_ids = list(performances.values_list('id', flat=True))
                
                # Excluir respostas
                resposta_count = StudentAnswer.objects.filter(
                    student__in=students,
                    simulado=simulado
                ).delete()[0]
                
                # Excluir performances
                performance_count = performances.delete()[0]
                
                # 2. Excluir dados do app
                # Obter resultados do app
                resultados_app = Resultado.objects.filter(
                    aluno__in=students,
                    simulado=simulado
                )
                
                # Obter IDs dos resultados para excluir detalhes
                resultado_ids = list(resultados_app.values_list('id', flat=True))
                
                # Excluir detalhes de respostas
                detalhes_count = DetalhesResposta.objects.filter(
                    resultado__in=resultado_ids
                ).delete()[0]
                
                # Excluir resultados
                resultado_count = resultados_app.delete()[0]
                
                # Mostrar mensagem de sucesso
                messages.success(
                    request, 
                    f"Dados excluídos com sucesso! Foram removidos {performance_count} resultados web e {resultado_count} resultados do app, "
                    f"junto com {resposta_count} respostas web e {detalhes_count} detalhes do app."
                )
                
                return redirect('class_select_simulado', class_id=class_id)
                
            except Exception as e:
                messages.error(request, f"Erro ao excluir dados: {str(e)}")
                return redirect('class_performance_dashboard', class_id=class_id, simulado_id=simulado_id)
        else:
            messages.error(request, "Por favor, marque a caixa de confirmação para confirmar a exclusão.")
            return redirect('class_performance_dashboard', class_id=class_id, simulado_id=simulado_id)
    
    context = {
        'class': class_obj,
        'simulado': simulado,
    }
    
    return render(request, 'classes/class_simulado_limpar.html', context)

def generate_class_dashboard_charts(request, class_id, simulado_id):
    """
    Gera os dados para os gráficos do dashboard de desempenho da turma
    e retorna como JSON para ser renderizado via JavaScript.
    """
    class_obj = get_object_or_404(Class, id=class_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Verificar se o simulado está associado à turma
    if not simulado.classes.filter(id=class_id).exists():
        return JsonResponse({'error': 'Este simulado não está associado a esta turma.'}, status=400)
    
    # Obter todos os alunos da turma
    students = class_obj.students.all()
    
    # Obter desempenhos dos alunos no simulado (tanto do sistema web quanto do app)
    web_performances = StudentPerformance.objects.filter(
        student__in=students, 
        simulado=simulado
    ).select_related('student')
    
    # Importar modelo Resultado do app
    app_resultados = Resultado.objects.filter(
        aluno__in=students,
        simulado=simulado
    ).select_related('aluno')
    
    # Combinar resultados de ambas as fontes
    todos_resultados = []
    
    # Processar resultados do sistema web
    for perf in web_performances:
        todos_resultados.append({
            "aluno": perf.student,
            "nome": perf.student.name,
            "nota": float(perf.score),
            "acertos": perf.correct_answers,
            "total": perf.total_questions,
            "fonte": "web"
        })
    
    # Processar resultados do app
    for res in app_resultados:
        todos_resultados.append({
            "aluno": res.aluno,
            "nome": res.aluno.name,
            "nota": float(res.pontuacao),
            "acertos": res.acertos,
            "total": res.total_questoes,
            "fonte": "app"
        })
    
    # Consolidar estatísticas por disciplinas da turma toda
    todas_disciplinas = defaultdict(lambda: {"acertos": 0, "total": 0})
    
    # Processar respostas do sistema web
    for perf in web_performances:
        respostas = StudentAnswer.objects.filter(
            student=perf.student,
            simulado=simulado
        ).select_related('question__questao')
        
        for resp in respostas:
            questao = resp.question.questao
            disciplina = questao.disciplina
            
            todas_disciplinas[disciplina]["total"] += 1
            if resp.is_correct:
                todas_disciplinas[disciplina]["acertos"] += 1
    
    # Processar respostas do app
    for res in app_resultados:
        detalhes = DetalhesResposta.objects.filter(
            resultado=res
        ).select_related('questao')
        
        for det in detalhes:
            questao = det.questao
            disciplina = questao.disciplina
            
            todas_disciplinas[disciplina]["total"] += 1
            if det.acertou:
                todas_disciplinas[disciplina]["acertos"] += 1
    
    # Converter para listas e calcular percentuais
    disciplinas_dados = []
    for nome, dados in todas_disciplinas.items():
        if dados["total"] > 0:
            percentual = (dados["acertos"] / dados["total"]) * 100
            disciplinas_dados.append({
                "nome": nome,
                "acertos": dados["acertos"],
                "total": dados["total"],
                "percentual": percentual
            })
    
    # Ordenar disciplinas pelo percentual (decrescente)
    disciplinas_dados.sort(key=lambda x: x["percentual"], reverse=True)
    
    # Ordenar resultados dos alunos por nota (decrescente)
    todos_resultados.sort(key=lambda x: x["nota"], reverse=True)
    
    # Preparar dados para o gráfico de notas por aluno
    nomes_alunos = [f"{r['nome'].split()[0]} {r['nome'].split()[-1] if len(r['nome'].split()) > 1 else ''}" for r in todos_resultados]
    notas_alunos = [r["nota"] for r in todos_resultados]
    
    # Preparar dados para o gráfico de pie/bar das disciplinas
    disciplinas_nomes = [d["nome"] for d in disciplinas_dados[:5]]  # Top 5
    disciplinas_percentuais = [d["percentual"] for d in disciplinas_dados[:5]]
    
    # Calcular distribuição de notas em faixas
    faixas = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
    contagem = [0] * 10
    
    for r in todos_resultados:
        nota = r["nota"]
        indice = min(int(nota), 9)
        contagem[indice] += 1
    
    # Calcular média da turma
    media_turma = sum(r["nota"] for r in todos_resultados) / len(todos_resultados) if todos_resultados else 0
    
    # Construir resposta JSON
    response_data = {
        'alunos': {
            'nomes': nomes_alunos,
            'notas': notas_alunos,
        },
        'disciplinas': {
            'nomes': disciplinas_nomes,
            'percentuais': disciplinas_percentuais,
        },
        'distribuicao': {
            'faixas': faixas,
            'contagem': contagem,
        },
        'media_turma': media_turma,
        'total_alunos': len(students),
        'total_participantes': len(todos_resultados),
    }
    
    return JsonResponse(response_data)