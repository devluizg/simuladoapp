from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from .models import Questao, Simulado, QuestaoSimulado
from .forms import QuestaoForm, SimuladoForm, QuestaoFilterForm
from django.db.models import Max
from django.db import transaction
from django.db import models
from .templatetags import custom_filters
import json
from django.views.decorators.csrf import csrf_exempt
from weasyprint import HTML
import tempfile
from django.conf import settings
import os

@login_required
def dashboard(request):
    """View para o dashboard principal do professor."""
    total_questoes = Questao.objects.filter(professor=request.user).count()
    total_simulados = Simulado.objects.filter(professor=request.user).count()
    ultimas_questoes = Questao.objects.filter(professor=request.user).order_by('-data_criacao')[:5]
    ultimos_simulados = Simulado.objects.filter(professor=request.user).order_by('-data_criacao')[:5]

    context = {
        'total_questoes': total_questoes,
        'total_simulados': total_simulados,
        'ultimas_questoes': ultimas_questoes,
        'ultimos_simulados': ultimos_simulados
    }
    return render(request, 'questions/questions_dashboard.html', context)

@login_required
def questao_list(request):
    """View para listar e filtrar questões."""
    form = QuestaoFilterForm(request.GET)
    questoes = Questao.objects.filter(professor=request.user)

    if form.is_valid():
        if form.cleaned_data['disciplina']:
            questoes = questoes.filter(disciplina__icontains=form.cleaned_data['disciplina'])
        if form.cleaned_data['conteudo']:
            questoes = questoes.filter(conteudo__icontains=form.cleaned_data['conteudo'])
        if form.cleaned_data['nivel_dificuldade']:
            questoes = questoes.filter(nivel_dificuldade=form.cleaned_data['nivel_dificuldade'])

    questoes = questoes.order_by('-data_criacao')
    
    for questao in questoes:
        questao.enunciado_preview = force_str(strip_tags(questao.enunciado))

    paginator = Paginator(questoes, 10)
    page = request.GET.get('page')
    questoes_paginadas = paginator.get_page(page)

    # Obter simulados do usuário atual
    simulados = Simulado.objects.filter(professor=request.user).order_by('-data_criacao')

    return render(request, 'questions/questao_list.html', {
        'questoes': questoes_paginadas,
        'form': form,
        'simulados': simulados  # Adicionando simulados ao contexto
    })

@login_required
def questao_create(request):
    """View para criar uma nova questão."""
    if request.method == 'POST':
        form = QuestaoForm(request.POST, request.FILES)
        if form.is_valid():
            questao = form.save(commit=False)
            questao.professor = request.user
            
            if 'imagem' in request.FILES:
                imagem = request.FILES['imagem']
                if imagem.size > 5 * 1024 * 1024:  # 5MB
                    messages.error(request, 'A imagem deve ter no máximo 5MB.')
                    return render(request, 'questions/questao_form.html', {'form': form})

            try:
                questao.save()
                messages.success(request, 'Questão criada com sucesso!')
                return redirect('questions:questao_list')
            except ValidationError as e:
                messages.error(request, str(e))
    else:
        form = QuestaoForm()
    
    return render(request, 'questions/questao_form.html', {'form': form})

@login_required
@require_POST
@csrf_exempt
def adicionar_questao_simulado(request):
    try:
        data = json.loads(request.body)
        questao_id = data.get('questao_id')
        simulado_id = data.get('simulado_id')

        if not questao_id or not simulado_id:
            return JsonResponse({'success': False, 'error': 'IDs de questão e simulado são necessários.'}, status=400)

        questao = Questao.objects.get(id=questao_id, professor=request.user)
        simulado = Simulado.objects.get(id=simulado_id, professor=request.user)

        # Verifica se a questão já está no simulado
        if QuestaoSimulado.objects.filter(simulado=simulado, questao=questao).exists():
            return JsonResponse({'success': False, 'error': 'Esta questão já está no simulado.'})

        with transaction.atomic():
            # Encontra a próxima ordem disponível
            max_ordem = QuestaoSimulado.objects.filter(simulado=simulado).aggregate(Max('ordem'))['ordem__max'] or 0
            proxima_ordem = max_ordem + 1

            # Cria a nova relação QuestaoSimulado
            QuestaoSimulado.objects.create(
                simulado=simulado,
                questao=questao,
                ordem=proxima_ordem
            )

        return JsonResponse({'success': True})

    except Questao.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Questão não encontrada.'}, status=404)
    except Simulado.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Simulado não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
@login_required
def questao_update(request, pk):
    """View para atualizar uma questão existente."""
    questao = get_object_or_404(Questao, pk=pk, professor=request.user)
    
    if request.method == 'POST':
        form = QuestaoForm(request.POST, request.FILES, instance=questao)
        if form.is_valid():
            if 'imagem' in request.FILES:
                imagem = request.FILES['imagem']
                if imagem.size > 5 * 1024 * 1024:  # 5MB
                    messages.error(request, 'A imagem deve ter no máximo 5MB.')
                    return render(request, 'questions/questao_form.html', {'form': form, 'questao': questao})

            form.save()
            messages.success(request, 'Questão atualizada com sucesso!')
            return redirect('questions:questao_list')
    else:
        form = QuestaoForm(instance=questao)
    
    return render(request, 'questions/questao_form.html', {
        'form': form,
        'questao': questao
    })

@login_required
def questao_delete(request, pk):
    """View para excluir uma questão."""
    questao = get_object_or_404(Questao, pk=pk, professor=request.user)
    
    if request.method == 'POST':
        if questao.imagem:
            if os.path.isfile(questao.imagem.path):
                os.remove(questao.imagem.path)
        
        questao.delete()
        messages.success(request, 'Questão excluída com sucesso!')
        return redirect('questions:questao_list')
    
    return render(request, 'questions/questao_confirm_delete.html', {
        'questao': questao
    })

@login_required
def simulado_list(request):
    """View para listar simulados."""
    simulados = Simulado.objects.filter(professor=request.user).order_by('-data_criacao')
    return render(request, 'questions/simulado_list.html', {
        'simulados': simulados
    })

@login_required
def simulado_create(request):
    """View para criar um novo simulado."""
    if request.method == 'POST':
        form = SimuladoForm(request.POST)
        if form.is_valid():
            simulado = form.save(commit=False)
            simulado.professor = request.user
            simulado.save()
            messages.success(request, 'Simulado criado com sucesso!')
            return redirect('questions:simulado_edit', pk=simulado.pk)
    else:
        form = SimuladoForm()
    
    return render(request, 'questions/simulado_form.html', {'form': form})

@login_required
def simulado_edit(request, pk):
    """View para editar um simulado existente."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    
    questoes_selecionadas = simulado.questoes.all().order_by('questaosimulado__ordem')
    
    questoes_disponiveis = Questao.objects.filter(
        professor=request.user
    ).exclude(
        id__in=questoes_selecionadas.values_list('id', flat=True)
    ).order_by('disciplina', 'conteudo')

    if request.method == 'POST':
        form = SimuladoForm(request.POST, instance=simulado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Simulado atualizado com sucesso!')
            return redirect('questions:simulado_list')
    else:
        form = SimuladoForm(instance=simulado)

    context = {
        'form': form,
        'simulado': simulado,
        'questoes_selecionadas': questoes_selecionadas,
        'questoes_disponiveis': questoes_disponiveis
    }
    
    return render(request, 'questions/simulado_edit.html', context)

@login_required
@require_POST
def simulado_delete(request, pk):
    """View para excluir um simulado."""
    try:
        simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
        simulado.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Simulado excluído com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def simulado_detail(request, pk):
    """View para exibir detalhes de um simulado."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    questoes = simulado.questoes.all().order_by('questaosimulado__ordem')
    
    return render(request, 'questions/simulado_detail.html', {
        'simulado': simulado,
        'questoes': questoes
    })

@login_required
@require_POST
def update_questoes_ordem(request, pk):
    """View para atualizar a ordem das questões no simulado via AJAX."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    try:
        data = json.loads(request.body)
        questoes = data.get('questoes', [])

        if not questoes:
            return JsonResponse({
                'status': 'error',
                'message': 'O simulado deve ter pelo menos uma questão'
            }, status=400)

        if len(questoes) > 45:
            return JsonResponse({
                'status': 'error',
                'message': 'O simulado não pode ter mais que 45 questões'
            }, status=400)

        if len(questoes) != len(set(questoes)):
            return JsonResponse({
                'status': 'error',
                'message': 'Existem questões duplicadas na lista'
            }, status=400)

        questoes_validas = Questao.objects.filter(
            id__in=questoes,
            professor=request.user
        ).count()
        
        if questoes_validas != len(questoes):
            return JsonResponse({
                'status': 'error',
                'message': 'Algumas questões selecionadas são inválidas'
            }, status=400)

        QuestaoSimulado.objects.filter(simulado=simulado).delete()

        for ordem, questao_id in enumerate(questoes, 1):
            QuestaoSimulado.objects.create(
                simulado=simulado,
                questao_id=questao_id,
                ordem=ordem
            )

        simulado.save()
        return JsonResponse({
            'status': 'success',
            'message': 'Simulado atualizado com sucesso!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao atualizar simulado: {str(e)}'
        }, status=400)

@login_required
def gerar_pdf(request, pk):
    """View para gerar o PDF do simulado com 5 versões."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    questoes = list(simulado.questoes.all().order_by('questaosimulado__ordem'))
    
    html_string = render_to_string('questions/simulado_pdf.html', {
        'simulado': simulado,
        'questoes': questoes,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    })
    
    with tempfile.NamedTemporaryFile(suffix='.pdf') as output:
        HTML(string=html_string).write_pdf(output)
        output.seek(0)
        response = HttpResponse(output.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_5versoes.pdf"'
        
    return response


@login_required
def gerar_pdf_todos(request):
    simulados = Simulado.objects.all()
    # Implemente a lógica para gerar um PDF com todos os simulados
    # Você pode usar o mesmo SimuladoPDFGenerator ou criar uma nova classe
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="todos_simulados.pdf"'
    
    # Adicione sua lógica de geração de PDF aqui
    
    return response