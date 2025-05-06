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

@login_required
def student_dashboard(request, student_id):
    student = get_object_or_404(Student, id=student_id, user=request.user)
    classes = student.classes.filter(user=request.user)
    
    # Obter todos os simulados que o aluno realizou
    performances = StudentPerformance.objects.filter(student=student).order_by('-date_taken')
    
    # Estatísticas gerais
    total_simulados = performances.count()
    media_geral = performances.aggregate(media=Avg('score'))['media'] or 0
    
    # Simulados recentes
    simulados_recentes = performances[:5]  
    
    # Progresso ao longo do tempo (últimos 10 simulados)
    progresso_simulados = performances[:10]
    
    context = {
        'student': student,
        'classes': classes,
        'total_simulados': total_simulados,
        'media_geral': media_geral,
        'simulados_recentes': simulados_recentes,
        'progresso_simulados': progresso_simulados,
        'performances': performances
    }
    
    return render(request, 'classes/student_dashboard.html', context)

@login_required
def student_simulado_detail(request, student_id, simulado_id):
    """Ver o desempenho detalhado de um aluno em um simulado específico"""
    student = get_object_or_404(Student, id=student_id, user=request.user)
    simulado = get_object_or_404(Simulado, id=simulado_id)
    
    # Verificar se o aluno está em alguma turma que tem acesso ao simulado
    if not student.classes.filter(id__in=simulado.classes.all()).exists():
        messages.error(request, "Este aluno não tem acesso a este simulado.")
        return redirect('student_dashboard', student_id=student_id)
    
    # Obter desempenho do aluno
    performance = get_object_or_404(StudentPerformance, student=student, simulado=simulado)
    
    # Obter respostas do aluno
    respostas = StudentAnswer.objects.filter(student=student, simulado=simulado).order_by('question__ordem')
    
    context = {
        'student': student,
        'simulado': simulado,
        'performance': performance,
        'respostas': respostas
    }
    
    return render(request, 'classes/student_simulado_detail.html', context)

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
        
        # Salvar ou atualizar desempenho
        performance, created = StudentPerformance.objects.update_or_create(
            student=student,
            simulado=simulado,
            defaults={
                'score': score,
                'correct_answers': correct_answers,
                'total_questions': total_questions
            }
        )
        
        return JsonResponse({
            'success': True,
            'student': student.name,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions
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