from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Class, Student
from .forms import ClassForm, StudentForm
from django.contrib.auth import get_user_model
from django.contrib import messages

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
    students = class_obj.students.all()
    return render(request, 'classes/class_students.html', {'class': class_obj, 'students': students})