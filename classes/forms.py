from django import forms
from .models import Class, Student
from django.contrib.auth import get_user_model

User = get_user_model()

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['name', 'description']
        labels = {
            'name': 'Nome',
            'description': 'Descrição',
        }

class StudentForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=30, label='Sobrenome')
    class_pk = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Student
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'class_pk' in kwargs['initial']:
            self.fields['class_pk'].initial = kwargs['initial']['class_pk']

    def save(self, commit=True):
        user_data = {
            'username': self.cleaned_data['email'],
            'email': self.cleaned_data['email'],
            'first_name': self.cleaned_data['first_name'],
            'last_name': self.cleaned_data['last_name'],
        }
        
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults=user_data
        )
        
        student, created = Student.objects.get_or_create(
            user=user
        )

        class_pk = self.cleaned_data.get('class_pk')
        if class_pk:
            try:
                class_obj = Class.objects.get(pk=class_pk)
                student.classes.add(class_obj)
            except Class.DoesNotExist:
                pass

        return student
