from django.urls import path
from . import views

app_name = 'questions'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='questions_dashboard'),
    
    # Questões
    path('questoes/', views.questao_list, name='questao_list'),
    path('questoes/nova/', views.questao_create, name='questao_create'),
    path('questoes/<int:pk>/editar/', views.questao_update, name='questao_update'),
    path('questoes/<int:pk>/excluir/', views.questao_delete, name='questao_delete'),
    
    # Simulados
    path('simulados/', views.simulado_list, name='simulado_list'),
    path('simulados/novo/', views.simulado_create, name='simulado_create'),
    path('simulados/<int:pk>/', views.simulado_detail, name='simulado_detail'),
    path('simulados/<int:pk>/editar/', views.simulado_edit, name='simulado_edit'),
    path('simulados/<int:pk>/excluir/', views.simulado_delete, name='simulado_delete'),
    path('simulados/<int:pk>/pdf/', views.gerar_pdf, name='gerar_pdf'),
    path('adicionar-questao-simulado/', views.adicionar_questao_simulado, name='adicionar_questao_simulado'),
    
    
    # AJAX
    path('simulados/<int:pk>/atualizar-ordem/', views.update_questoes_ordem, name='update_questoes_ordem'),
]