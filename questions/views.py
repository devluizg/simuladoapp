#questions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
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
from django.core.cache import cache
import concurrent.futures
from PyPDF2 import PdfMerger
import time
import io

logger = logging.getLogger(__name__)

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

def questao_list(request):
    form = QuestaoFilterForm(request.GET)
    
    # Filtrar apenas as questões do usuário atual
    questoes = Questao.objects.filter(professor=request.user)
    
    if form.is_valid():
        # Filtrar por busca textual se o campo estiver presente
        if form.cleaned_data.get('busca'):
            query = form.cleaned_data['busca']
            questoes = questoes.filter(
                models.Q(enunciado__icontains=query) |
                models.Q(alternativa_a__icontains=query) |
                models.Q(alternativa_b__icontains=query) |
                models.Q(alternativa_c__icontains=query) |
                models.Q(alternativa_d__icontains=query) |
                models.Q(alternativa_e__icontains=query) |
                models.Q(disciplina__icontains=query) |
                models.Q(conteudo__icontains=query)
            )
        
        # Manter os filtros existentes
        if form.cleaned_data.get('disciplina'):
            questoes = questoes.filter(disciplina__icontains=form.cleaned_data['disciplina'])
        
        if form.cleaned_data.get('conteudo'):
            questoes = questoes.filter(conteudo__icontains=form.cleaned_data['conteudo'])
            
        if form.cleaned_data.get('nivel_dificuldade'):
            questoes = questoes.filter(nivel_dificuldade=form.cleaned_data['nivel_dificuldade'])
    
    # Paginação
    paginator = Paginator(questoes, 10)
    page = request.GET.get('page')
    questoes = paginator.get_page(page)
    
    # Obter simulados do professor atual
    simulados = Simulado.objects.filter(professor=request.user)
    
    context = {
        'questoes': questoes,
        'form': form,
        'simulados': simulados,
    }
    
    return render(request, 'questions/questao_list.html', context)

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
    """View para excluir uma questão contornando o problema da tabela inexistente."""
    questao = get_object_or_404(Questao, pk=pk, professor=request.user)
    
    if request.method == 'POST':
        try:
            # Remover manualmente a imagem se existir
            if questao.imagem and hasattr(questao.imagem, 'path') and os.path.isfile(questao.imagem.path):
                os.remove(questao.imagem.path)
            
            # Excluir manualmente as relações primeiro
            from django.db import connection
            with connection.cursor() as cursor:
                # Remover primeiro as questões do simulado
                cursor.execute("DELETE FROM questions_questaosimulado WHERE questao_id = %s", [questao.id])
                # Agora remover a questão diretamente
                cursor.execute("DELETE FROM questions_questao WHERE id = %s", [questao.id])
            
            messages.success(request, 'Questão excluída com sucesso!')
            return redirect('questions:questao_list')
        except Exception as e:
            messages.error(request, f'Erro ao excluir questão: {str(e)}')
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
    
    # Prepara os dados do gabarito para o template
    versoes = []
    questao_range = []
    
    if simulado.gabaritos_gerados:
        # Determinar o número total de questões (usando a primeira versão)
        num_questoes = len(simulado.gabaritos_gerados[0]['gabarito']) if simulado.gabaritos_gerados else 0
        questao_range = range(1, num_questoes + 1)
        
        # Preparar dados de cada versão
        for versao_data in simulado.gabaritos_gerados:
            versoes.append({
                'gabarito': versao_data.get('gabarito', {})
            })
    
    return render(request, 'questions/simulado_detail.html', {
        'simulado': simulado,
        'questoes': questoes,
        'versoes': versoes,
        'questao_range': questao_range
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
    """View otimizada para gerar o PDF do simulado com 5 versões e cartão resposta na ordem correta."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    
    # Verificar o cache (ignorar com parâmetro refresh=true)
    cache_key = f'simulado_pdf_{pk}_{simulado.ultima_modificacao.timestamp()}'
    if not request.GET.get('refresh'):
        cached_pdf = cache.get(cache_key)
        if cached_pdf:
            logger.info(f"Entregando PDF do simulado {pk} do cache")
            response = HttpResponse(cached_pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_5versoes.pdf"'
            return response
    
    # Não está em cache, gerar o PDF
    try:
        # Buscar questões apenas uma vez e converter para lista para melhor performance
        questoes = list(simulado.questoes.all().order_by('questaosimulado__ordem'))
        
        if len(questoes) > 45:
            messages.error(request, 'O simulado não pode ter mais que 45 questões')
            return redirect('questions:simulado_edit', pk=simulado.pk)
        
        # Se estiver em modo debug, mostrar o tempo de processamento
        start_time = time.time()
        
        # Criar diretório temporário para os arquivos
        with tempfile.TemporaryDirectory() as tmpdirname:
            logger.info(f"Iniciando geração das versões do simulado {pk}")
            
            # Gerar versões do simulado em paralelo
            embaralhamentos = [None] * 5  # Lista pré-alocada para 5 versões
            all_pdfs = [None] * 5  # Lista pré-alocada para 5 versões
            cartoes_resposta = [None] * 5  # Lista pré-alocada para 5 versões
            
            # Usar ThreadPoolExecutor para processamento paralelo
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Submeter tarefas para as versões do simulado
                versao_futures = {
                    executor.submit(_gerar_versao_simulado, simulado, questoes, tmpdirname, versao): versao 
                    for versao in range(1, 6)
                }
                
                # Submeter tarefas para os cartões-resposta
                cartao_futures = {
                    executor.submit(_gerar_cartao_resposta, tmpdirname, versao, versao, len(questoes)): versao 
                    for versao in range(1, 6)
                }
                
                # Coletar resultados das versões, preservando a ordem correta
                for future in concurrent.futures.as_completed(versao_futures):
                    versao = versao_futures[future]
                    try:
                        pdf_path, embaralhamento = future.result()
                        # Armazenar resultados na posição correta (índice 0 para versão 1, etc)
                        all_pdfs[versao-1] = pdf_path
                        embaralhamentos[versao-1] = embaralhamento
                        logger.debug(f"Versão {versao} gerada com sucesso e armazenada na posição {versao-1}")
                    except Exception as exc:
                        logger.error(f"Versão {versao} gerou exceção: {exc}")
                        logger.error(traceback.format_exc())
                        messages.error(request, f"Erro ao gerar versão {versao}: {str(exc)}")
                
                # Coletar resultados dos cartões, preservando a ordem
                for future in concurrent.futures.as_completed(cartao_futures):
                    versao = cartao_futures[future]
                    try:
                        cartao_path = future.result()
                        # Armazenar na posição correta
                        cartoes_resposta[versao-1] = cartao_path
                        logger.debug(f"Cartão resposta {versao} gerado com sucesso e armazenado na posição {versao-1}")
                    except Exception as exc:
                        logger.error(f"Cartão resposta versão {versao} gerou exceção: {exc}")
                        logger.error(traceback.format_exc())
            
            # Verificar se todos os PDFs foram gerados corretamente
            if None in all_pdfs or None in cartoes_resposta:
                missing_versions = [i+1 for i, v in enumerate(all_pdfs) if v is None]
                missing_cartoes = [i+1 for i, v in enumerate(cartoes_resposta) if v is None]
                
                error_msg = ""
                if missing_versions:
                    error_msg += f"Falha ao gerar versões: {', '.join(map(str, missing_versions))}. "
                if missing_cartoes:
                    error_msg += f"Falha ao gerar cartões resposta: {', '.join(map(str, missing_cartoes))}."
                
                raise Exception(error_msg)
            
            logger.info(f"Combinando PDFs do simulado {pk}")
            
            # Combinar todos os PDFs na ordem correta (versões de 1 a 5 seguidas pelos cartões resposta)
            output_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_completo.pdf')
            _combinar_pdfs_ordenados(all_pdfs, cartoes_resposta, output_path)
            
            # Salvar as informações de embaralhamento no simulado (já estão na ordem correta)
            simulado.gabaritos_gerados = embaralhamentos
            simulado.save()
            
            # Ler o PDF final
            with open(output_path, 'rb') as f:
                pdf_content = f.read()
            
            # Armazenar em cache por 24 horas (86400 segundos)
            cache.set(cache_key, pdf_content, 86400)
            
            # Retornar o PDF combinado
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_5versoes.pdf"'
            
            # Registrar tempo total de processamento
            elapsed_time = time.time() - start_time
            logger.info(f"PDF gerado com sucesso em {elapsed_time:.2f} segundos para simulado {pk} com {len(questoes)} questões")
            
            return response
            
    except Exception as e:
        logger.error(f"Erro ao gerar PDF do simulado {pk}: {str(e)}")
        logger.error(traceback.format_exc())
        messages.error(request, f"Erro ao gerar o PDF: {str(e)}")
        return redirect('questions:simulado_edit', pk=simulado.pk)
    
def _gerar_versao_simulado(simulado, questoes, tmpdirname, versao):
    """Função auxiliar para gerar uma versão do simulado em paralelo."""
    logger.debug(f"Gerando versão {versao} do simulado {simulado.pk}")
    
    # Embaralhar as questões para esta versão
    questoes_shuffled = list(custom_filters.shuffle(questoes))
    
    # Armazenar a ordem das questões embaralhadas para esta versão
    ordem_atual = {
        'questoes': [q.id for q in questoes_shuffled],
        'gabarito': {}
    }
    
    for ordem, questao in enumerate(questoes_shuffled, 1):
        # Mapear o gabarito
        resp_original = questao.resposta_correta
        
        ordem_atual['gabarito'][ordem] = {
            'tipo1': resp_original,
            'tipo2': resp_original,
            'tipo3': resp_original,
            'tipo4': resp_original,
            'tipo5': resp_original
        }
    
    # Otimização: Pré-processar o HTML com os filtros necessários
    for q in questoes_shuffled:
        # Otimizar imagens se necessário
        if q.imagem:
            # Assegurar que o caminho da imagem está correto
            q.imagem_path = q.imagem.path if os.path.exists(q.imagem.path) else None
    
    # Renderizar o HTML com os dados
    html_string = render_to_string('questions/simulado_pdf.html', {
        'simulado': simulado,
        'questoes': questoes_shuffled,
        'versao': versao,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    })
    
    # Gerar o PDF desta versão
    versao_pdf_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_v{versao}.pdf')
    
    # Usar WeasyPrint com configurações otimizadas
    html = HTML(string=html_string)
    html.write_pdf(versao_pdf_path, optimize_size=('fonts',))
    
    return versao_pdf_path, ordem_atual

def _gerar_cartao_resposta(tmpdirname, caderno, tipo, num_questoes):
    """Versão otimizada da função de geração de cartão resposta."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    
    nome_arquivo = os.path.join(tmpdirname, f'Cartao_Resposta_{caderno}_Tipo{tipo}.pdf')
    c = canvas.Canvas(nome_arquivo, pagesize=A4)
    c.setTitle(f"Cartão Resposta - Tipo {tipo}")
    c.setAuthor("Sistema de Correção")
    c.setSubject("Cartão Resposta")
    c.setPageCompression(1)  # Ativar compressão
    largura, altura = A4
    
    # O restante do código permanece o mesmo da função original gerar_cartao_resposta_pdf
    # Determina o número de colunas
    num_colunas = 1 if num_questoes <= 23 else 2
    
    # Distribuição das questões entre as colunas
    questoes_por_coluna = []
    if num_colunas == 1:
        questoes_por_coluna = [num_questoes]
    else:
        # Se número de questões for ímpar, coloca uma questão a mais na primeira coluna
        if num_questoes % 2 == 0:  # Se for par
            questoes_por_coluna = [num_questoes // 2, num_questoes // 2]
        else:  # Se for ímpar
            questoes_por_coluna = [(num_questoes // 2) + 1, num_questoes // 2]
    
    # Dimensões básicas
    margem_superior = 50 * mm
    margem_lateral = 30 * mm
    espaco_entre_colunas = 15 * mm
    alternativas = ['A', 'B', 'C', 'D', 'E']
    diametro_circulo = 4 * mm
    espaco_entre_circulos = 6 * mm
    espaco_entre_questoes = 8 * mm
    margem_interna = 3 * mm
    largura_bolhas = (5 * espaco_entre_circulos)
    largura_indice = 8 * mm  # Ainda usado, mas agora fora do retângulo
    largura_necessaria = largura_bolhas + (2 * margem_interna)
    
    largura_total_necessaria = (largura_necessaria * num_colunas) + (espaco_entre_colunas * (num_colunas - 1)) + (largura_indice * num_colunas)
    margem_lateral = (largura - largura_total_necessaria) / 2
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margem_lateral- 20 * mm, altura - 20 * mm, f"CARTÃO RESPOSTA - TIPO {tipo}")
    
    questoes_processadas = 0
    
    for coluna in range(num_colunas):
        x_inicial_indice = margem_lateral + (coluna * (largura_necessaria + espaco_entre_colunas + largura_indice))
        x_inicial_retangulo = x_inicial_indice + largura_indice
        largura_bolhas_total = (len(alternativas) - 1) * espaco_entre_circulos
        x_inicial_bolhas = x_inicial_retangulo + ((largura_necessaria - largura_bolhas_total) / 2)
        
        questoes_nesta_coluna = questoes_por_coluna[coluna]
        altura_necessaria = (questoes_nesta_coluna * espaco_entre_questoes) + (2 * margem_interna)
        
        c.setLineWidth(0.7 * mm)
        c.rect(x_inicial_retangulo,
              altura - margem_superior - altura_necessaria,
              largura_necessaria,
              altura_necessaria)
        
        # Cabeçalho das alternativas
        for i, alt in enumerate(alternativas):
            x = x_inicial_bolhas + (i * espaco_entre_circulos)
            y = altura - margem_superior + 5 * mm
            c.setFont("Helvetica", 10)
            c.drawString(x - 1 * mm, y, alt)
        
        for q in range(questoes_nesta_coluna):
            numero_questao = questoes_processadas + q + 1
            y = altura - margem_superior - ((q + 1) * espaco_entre_questoes)
            
            # Número da questão FORA do retângulo
            c.setFont("Helvetica", 10)
            if numero_questao < 10:
                c.drawString(x_inicial_indice, y - 1 * mm, f"0{numero_questao}")
            else:
                c.drawString(x_inicial_indice, y - 1 * mm, f"{numero_questao}")
            
            # Bolhas das alternativas
            for i in range(5):
                x = x_inicial_bolhas + (i * espaco_entre_circulos)
                c.circle(x, y, diametro_circulo / 2, stroke=1, fill=0)
        
        questoes_processadas += questoes_nesta_coluna
    
    c.setFont("Helvetica", 8)
    c.drawString(margem_lateral, 15 * mm, f"Total de questões: {num_questoes}")
    c.drawString(margem_lateral, 10 * mm, "Preencha completamente os círculos com caneta preta ou azul")
    
    c.save()
    return nome_arquivo

def _combinar_pdfs_ordenados(pdfs_simulados, pdfs_cartoes, output_path):
    """Função para combinar PDFs respeitando a ordem das versões."""
    try:
        # Verificar que todos os caminhos existem e têm conteúdo
        for pdf_list in [pdfs_simulados, pdfs_cartoes]:
            for path in pdf_list:
                if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
                    raise ValueError(f"Arquivo PDF inválido ou vazio: {path}")
        
        # Combinar na ordem correta: primeiro todas as versões de simulados, depois todos os cartões resposta
        merger = PdfMerger(strict=False)
        
        # Adicionar simulados na ordem (já estão ordenados)
        for pdf_path in pdfs_simulados:
            merger.append(pdf_path)
        
        # Adicionar cartões resposta na ordem (já estão ordenados)
        for pdf_path in pdfs_cartoes:
            merger.append(pdf_path)
        
        # Escrever o PDF combinado
        merger.write(output_path)
        merger.close()
        
        return True
    except Exception as e:
        logger.error(f"Erro ao combinar PDFs ordenados: {str(e)}")
        logger.error(traceback.format_exc())
        raise

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