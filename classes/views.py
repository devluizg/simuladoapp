from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Class, Student
from .forms import ClassForm, StudentForm
from .utils import extract_students_from_pdf, extract_students_from_excel
from questions.models import Simulado, QuestaoSimulado

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
            student.save()
            class_obj.students.add(student)
    return redirect('class_edit', pk=pk)

@login_required
def class_remove_student(request, class_pk, student_pk):
    class_obj = get_object_or_404(Class, pk=class_pk, user=request.user)
    student = get_object_or_404(Student, pk=student_pk, user=request.user)
    if request.method == 'POST':
        class_obj.students.remove(student)
    return redirect('class_edit', pk=class_pk)

# Student views
@login_required
def student_list(request):
    students = Student.objects.filter(user=request.user)
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
            student.save()
            messages.success(request, 'Aluno adicionado com sucesso!')
            return redirect('class_list')
    else:
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
            return redirect('class_students', pk=student.classes.first().id)
    else:
        form = StudentForm(instance=student)
    return render(request, 'classes/student_form.html', {'form': form})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk, user=request.user)
    if request.method == 'POST':
        student.delete()
        return redirect('student_list')
    return render(request, 'classes/student_confirm_delete.html', {'student': student})

@login_required
def student_dashboard(request, student_id):
    student = get_object_or_404(Student, id=student_id, user=request.user)
    classes = student.classes.filter(user=request.user)
    simulados = Simulado.objects.filter(classes__in=classes).distinct()
    total_simulados = simulados.count()
    total_questoes = QuestaoSimulado.objects.filter(simulado__in=simulados).count()
    
    context = {
        'student': student,
        'classes': classes,
        'total_simulados': total_simulados,
        'total_questoes': total_questoes,
        'simulados': simulados[:5]  # Mostrar os 5 últimos simulados
    }
    
    return render(request, 'classes/student_dashboard.html', context)

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
        return redirect('student_dashboard', student_id=student_id)
    
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
            last_student = Student.objects.filter(user=request.user).order_by('-student_id').first()
            next_id = (last_student.student_id + 1) if last_student else 1
            
            for student_data in students_data:
                name = student_data['name']
                email = student_data.get('email') or f"{name.lower().replace(' ', '.')}@escola.com"
                
                student = Student.objects.create(
                    name=name,
                    email=email,
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
