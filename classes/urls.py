from django.urls import path
from . import views

urlpatterns = [
    # Rotas para Turmas
    path('', views.class_list, name='class_list'),
    path('create/', views.class_create, name='class_create'),
    path('<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('<int:pk>/delete/', views.class_delete, name='class_delete'),
    
    # Rotas para Estudantes
    path('student/form/', views.student_form, name='student_form'),  # Nova rota
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/edit/', views.student_edit, name='student_edit'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('class/<int:pk>/students/', views.class_students, name='class_students'),

    
    # Rotas para gerenciamento de alunos em turmas
    path('<int:pk>/add_students/', views.class_add_students, name='class_add_students'),
    path('<int:class_pk>/remove_student/<int:student_pk>/', views.class_remove_student, name='class_remove_student'),
    path('import-students/', views.import_students, name='import_students'),
    path('student/<int:pk>/edit/', views.student_edit, name='student_edit'),
]