#questions/views.py
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
import logging
from django.shortcuts import render
import traceback
from classes.models import Class

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
    if request.method == 'POST':
        form = SimuladoForm(request.POST, user=request.user)
        if form.is_valid():
            simulado = form.save(commit=False)
            simulado.professor = request.user
            simulado.save()
            
            # Salvar as turmas selecionadas
            turmas = form.cleaned_data['turmas']
            simulado.classes.set(turmas)
            
            messages.success(request, 'Simulado criado com sucesso!')
            return redirect('questions:simulado_edit', pk=simulado.pk)
    else:
        form = SimuladoForm(user=request.user)
    
    context = {
        'form': form,
        'titulo': 'Novo Simulado'
    }
    return render(request, 'questions/simulado_form.html', context)


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
        form = SimuladoForm(request.POST, instance=simulado, user=request.user)
        if form.is_valid():
            simulado = form.save()
            
            # Atualizar as turmas selecionadas
            if 'turmas' in form.cleaned_data:
                turmas = form.cleaned_data['turmas']
                simulado.classes.set(turmas)
            
            messages.success(request, 'Simulado atualizado com sucesso!')
            return redirect('questions:simulado_list')
    else:
        form = SimuladoForm(instance=simulado, user=request.user)

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
    """View para exibir detalhes de um simulado e seus gabaritos."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    questoes = simulado.questoes.all().order_by('questaosimulado__ordem')
    
    # Aqui você poderia adicionar lógica para calcular diferentes embaralhamentos
    # por enquanto estamos usando uma simulação no template
    
    return render(request, 'questions/simulado_detail.html', {
        'simulado': simulado,
        'questoes': questoes
    })

logger = logging.getLogger(__name__)

@login_required
@require_POST
def update_questoes_ordem(request, pk):
    logger.info(f"Atualizando ordem do simulado {pk} para usuário {request.user.username}")
    try:
        simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
        data = json.loads(request.body)
        questoes = data.get('questoes', [])

        # Remover valores None e converter para inteiros
        questoes = [int(q) for q in questoes if q is not None]
        logger.debug(f"Questões recebidas após limpeza: {questoes}")

        if not questoes:
            logger.warning("Tentativa de salvar simulado sem questões")
            return JsonResponse({
                'status': 'error',
                'message': 'O simulado deve ter pelo menos uma questão'
            }, status=400)

        if len(questoes) > 45:
            logger.warning(f"Tentativa de salvar simulado com {len(questoes)} questões (máximo: 45)")
            return JsonResponse({
                'status': 'error',
                'message': 'O simulado não pode ter mais que 45 questões'
            }, status=400)

        if len(questoes) != len(set(questoes)):
            logger.warning("Detectadas questões duplicadas na lista")
            return JsonResponse({
                'status': 'error',
                'message': 'Existem questões duplicadas na lista'
            }, status=400)

        questoes_validas = set(Questao.objects.filter(
            id__in=questoes,
            professor=request.user
        ).values_list('id', flat=True))
        
        questoes_invalidas = set(questoes) - questoes_validas
        
        if questoes_invalidas:
            logger.warning(f"Questões inválidas detectadas: {questoes_invalidas}")
            return JsonResponse({
                'status': 'error',
                'message': f'Algumas questões selecionadas são inválidas: {", ".join(map(str, questoes_invalidas))}'
            }, status=400)

        with transaction.atomic():
            logger.debug("Iniciando transação atômica para atualizar questões do simulado")
            QuestaoSimulado.objects.filter(simulado=simulado).delete()

            for ordem, questao_id in enumerate(questoes, 1):
                QuestaoSimulado.objects.create(
                    simulado=simulado,
                    questao_id=questao_id,
                    ordem=ordem
                )

        simulado.save()
        logger.info(f"Simulado {pk} atualizado com sucesso")
        return JsonResponse({
            'status': 'success',
            'message': 'Simulado atualizado com sucesso!'
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar simulado {pk}: {str(e)}")
        logger.error(traceback.format_exc())
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao atualizar simulado: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)

@login_required
def gerar_pdf(request, pk):
    """View para gerar o PDF do simulado com 5 versões e cartão resposta atualizado."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    questoes = list(simulado.questoes.all().order_by('questaosimulado__ordem'))
    
    # Criar diretório temporário para os arquivos
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Gerar o PDF principal do simulado
        html_string = render_to_string('questions/simulado_pdf.html', {
            'simulado': simulado,
            'questoes': questoes,
            'MEDIA_ROOT': settings.MEDIA_ROOT,
        })
        
        simulado_pdf_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}.pdf')
        HTML(string=html_string).write_pdf(simulado_pdf_path)
        
        # Gerar cartão resposta usando a nova função
        from .pdf_generator import gerar_cartao_resposta_pdf
        
        # Gerar um cartão de resposta para cada versão (1-5)
        cartoes_resposta = []
        for versao in range(1, 6):
            # Agora passamos o número do tipo (1-5) para a função
            cartao_path = gerar_cartao_resposta_pdf(tmpdirname, versao, versao, len(questoes))
            cartoes_resposta.append(cartao_path)
        
        # Combinar todos os PDFs (simulado + cartões resposta)
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        # Adicionar simulado
        merger.append(simulado_pdf_path)
        
        # Adicionar cartões de resposta
        for cartao_path in cartoes_resposta:
            if os.path.exists(cartao_path):
                merger.append(cartao_path)
        
        # Salvar PDF combinado
        output_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_completo.pdf')
        merger.write(output_path)
        merger.close()
        
        # Retornar o PDF combinado
        with open(output_path, 'rb') as f:
            pdf_content = f.read()
            
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_5versoes.pdf"'
        
    return response


@login_required
def simulado_form(request, pk=None):
    """View para criar ou editar um simulado."""
    # Inicializa o simulado como None (para criação)
    simulado = None
    
    # Se um pk foi fornecido, tenta buscar o simulado existente
    if pk:
        simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    
    if request.method == 'POST':
        # Passa o parâmetro user para o formulário
        form = SimuladoForm(request.POST, instance=simulado, user=request.user)
        if form.is_valid():
            simulado = form.save(commit=False)
            # Sempre define o professor como o usuário atual antes de salvar
            simulado.professor = request.user
            simulado.save()
            
            # Salvar as turmas selecionadas
            turmas = form.cleaned_data['turmas']
            simulado.classes.set(turmas)
            
            messages.success(request, 'Alterações salvas com sucesso!')
            return redirect('questions:simulado_edit', pk=simulado.pk)
    else:
        # Passa o parâmetro user para o formulário
        form = SimuladoForm(instance=simulado, user=request.user)
    
    context = {
        'form': form,
        'simulado': simulado,
        'titulo': 'Editar Simulado' if pk else 'Novo Simulado'
    }
    return render(request, 'questions/simulado_form.html', context)