from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Class, Student
from .forms import ClassForm, StudentForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib import messages
from .utils import extract_students_from_pdf, extract_students_from_excel
from django.core.exceptions import ValidationError

@login_required
def class_list(request):
    classes = Class.objects.all()
    return render(request, 'classes/class_list.html', {'classes': classes})

@login_required
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'classes/class_form.html', {'form': form})

@login_required
def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
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
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        class_obj.delete()
        return redirect('class_list')
    return render(request, 'classes/class_confirm_delete.html', {'class': class_obj})

@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'classes/student_list.html', {'students': students})

@login_required
def student_create(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm()
    return render(request, 'classes/student_form.html', {'form': form})

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student_list')
    else:
        form = StudentForm(instance=student, initial={
            'email': student.user.email,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
        })
    return render(request, 'classes/student_form.html', {'form': form})

@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.user.delete()  # This will also delete the student due to the CASCADE
        return redirect('student_list')
    return render(request, 'classes/student_confirm_delete.html', {'student': student})

@login_required
def class_add_students(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            User = get_user_model()
            user, created = User.objects.get_or_create(email=email, defaults={'username': email})
            student, created = Student.objects.get_or_create(user=user)
            class_obj.students.add(student)
    return redirect('class_edit', pk=pk)

@login_required
def class_remove_student(request, class_pk, student_pk):
    class_obj = get_object_or_404(Class, pk=class_pk)
    student = get_object_or_404(Student, pk=student_pk)
    if request.method == 'POST':
        class_obj.students.remove(student)
    return redirect('class_edit', pk=class_pk)

def student_form(request):
    # Pegar o class_pk da query string
    class_pk = request.GET.get('class_pk')
    
    initial_data = {}
    if class_pk:
        initial_data['class_pk'] = class_pk

    if request.method == 'POST':
        form = StudentForm(request.POST, initial=initial_data)
        if form.is_valid():
            student = form.save()
            messages.success(request, 'Aluno adicionado com sucesso!')
            return redirect('class_list')
    else:
        form = StudentForm(initial=initial_data)

    return render(request, 'classes/student_form.html', {
        'form': form,
        'class_pk': class_pk
    })

def class_students(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    students = class_obj.students.all().order_by('student_id')
    return render(request, 'classes/class_students.html', {
        'class': class_obj, 
        'students': students
    })

@login_required
def import_students(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        class_id = request.POST.get('class_id')
        
        try:
            class_obj = Class.objects.get(id=class_id) if class_id else None
            if not class_obj:
                raise ValidationError("É necessário selecionar uma turma.")
            
            # Determina o tipo de arquivo e processa
            if file.name.endswith('.pdf'):
                students_data = extract_students_from_pdf(file)
            elif file.name.endswith(('.xlsx', '.xls')):
                students_data = extract_students_from_excel(file)
            else:
                raise ValidationError("Formato de arquivo não suportado. Use PDF ou Excel.")
            
            created_count = 0
            
            # Pega o último ID usado NESTA turma específica
            last_student = Student.objects.filter(classes=class_obj).order_by('-student_id').first()
            next_id = 1  # Sempre começa do 1 para cada turma
            
            for student_data in students_data:
                name = student_data['name']
                email = student_data.get('email')  # Pode ser None
                
                # Se não tiver email, gera um baseado no nome
                if not email:
                    email = f"{name.lower().replace(' ', '.')}@escola.com"
                
                # Cria o estudante
                student = Student.objects.create(
                    name=name,
                    email=email,
                    student_id=next_id
                )
                next_id += 1
                created_count += 1
                
                # Adiciona o aluno à turma
                class_obj.students.add(student)
            
            messages.success(
                request,
                f'Importação concluída! {created_count} alunos criados para a turma {class_obj.name}.'
            )
            
        except Exception as e:
            messages.error(request, f'Erro na importação: {str(e)}')
            
        return redirect('class_students', pk=class_id)
        
    return render(request, 'classes/import_students.html', {
        'classes': Class.objects.all()
    })

@login_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        student.registration_number = request.POST.get('registration_number')
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.save()
        messages.success(request, 'Informações do aluno atualizadas com sucesso.')
        return redirect('class_students', pk=student.classes.first().id)
    return redirect('class_students', pk=student.classes.first().id)