#questions/views.py
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags
from django.utils.encoding import force_str
from .models import Questao, Simulado, QuestaoSimulado, VersaoGabarito
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
from django.utils import timezone
from .pdf_performance_logger import PerformanceTimer, time_function, perf_logger, log_file_size

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
    """View simplificada para exibir detalhes de um simulado."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

    # Buscar questões ordenadas
    questoes = simulado.questoes.all().order_by('questaosimulado__ordem')

    # Buscar histórico de gabaritos apenas para exibição
    historico_gabaritos = simulado.get_historico_gabaritos()
    total_versoes = simulado.get_total_versoes_gabarito()

    # ✅ CORREÇÃO PRINCIPAL - Usar versão OFICIAL ao invés da última gerada
    versoes = []
    gabaritos_processados = []
    versao_oficial = None

    # Obter a versão oficial do gabarito
    if simulado.versao_gabarito_oficial:
        versao_oficial = simulado.versao_gabarito_oficial
        print(f"DEBUG - Exibindo versão oficial: {versao_oficial.get_versao_curta()}")
    elif historico_gabaritos.exists():
        # Fallback: se não há oficial, usar a mais recente
        versao_oficial = historico_gabaritos.first()
        print(f"DEBUG - Sem versão oficial, usando mais recente: {versao_oficial.get_versao_curta()}")

    if versao_oficial and versao_oficial.gabaritos_gerados:
        try:
            # Processar os gabaritos da versão OFICIAL
            for versao_data in versao_oficial.gabaritos_gerados[:5]:
                if isinstance(versao_data, dict) and 'gabarito' in versao_data:
                    versoes.append(versao_data)

            # Obter todas as questões do gabarito oficial
            todas_questoes = set()
            for versao in versao_oficial.gabaritos_gerados:
                if isinstance(versao, dict) and 'gabarito' in versao:
                    todas_questoes.update(versao['gabarito'].keys())

            # Converter para lista e ordenar
            todas_questoes = sorted(list(todas_questoes), key=lambda x: int(x))

            # Para cada questão, obter as respostas em cada versão
            for questao_idx in todas_questoes:
                row = {'questao_idx': int(questao_idx)}

                # Para cada versão
                for i, versao_data in enumerate(versao_oficial.gabaritos_gerados[:5]):
                    if isinstance(versao_data, dict) and 'gabarito' in versao_data:
                        gabarito = versao_data['gabarito']
                        if questao_idx in gabarito:
                            questao_data = gabarito[questao_idx]
                            if isinstance(questao_data, dict):
                                resposta = questao_data.get('tipo1', '-')
                            else:
                                resposta = str(questao_data)
                        else:
                            resposta = '-'
                    else:
                        resposta = '-'

                    row[f'versao_{i+1}'] = resposta

                # Preencher versões restantes com '-' se necessário
                for i in range(len(versao_oficial.gabaritos_gerados), 5):
                    row[f'versao_{i+1}'] = '-'

                gabaritos_processados.append(row)

            # Ordenar gabaritos processados pelo número da questão
            gabaritos_processados.sort(key=lambda x: x['questao_idx'])

        except Exception as e:
            logger.error(f"Erro ao processar gabaritos oficiais do simulado {pk}: {str(e)}")
            messages.error(request, f"Erro ao processar gabaritos: {str(e)}")
            versoes = []
            gabaritos_processados = []

    if settings.DEBUG:
        logger.debug(f"Gabaritos processados (versão oficial): {gabaritos_processados}")

    return render(request, 'questions/simulado_detail.html', {
        'simulado': simulado,
        'questoes': questoes,
        'versoes': versoes,
        'gabaritos_processados': gabaritos_processados,
        'versao_oficial': versao_oficial,  # ✅ Mudança: passa versão oficial
        'historico_gabaritos': historico_gabaritos,
        'total_versoes': total_versoes,
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

        # Verificar se houve mudança real na ordem antes de atualizar
        questoes_atuais = list(QuestaoSimulado.objects.filter(simulado=simulado).order_by('ordem').values_list('questao_id', flat=True))

        # Se a ordem é exatamente a mesma, não faz nada
        if questoes_atuais == questoes:
            logger.info(f"Ordem do simulado {pk} não foi alterada")
            return JsonResponse({
                'status': 'success',
                'message': 'Nenhuma alteração necessária'
            })

        logger.info(f"Ordem alterada no simulado {pk}: {questoes_atuais} -> {questoes}")

        with transaction.atomic():
            logger.debug("Iniciando transação atômica para atualizar questões do simulado")

            # CORRIGIDO: Limpar cache ANTES de fazer as alterações
            simulado.limpar_todo_cache()
            logger.info(f"Cache limpo para simulado {pk} devido à reordenação")

            # Deletar todas as questões existentes
            QuestaoSimulado.objects.filter(simulado=simulado).delete()

            # Recriar as questões na nova ordem
            for ordem, questao_id in enumerate(questoes, 1):
                QuestaoSimulado.objects.create(
                    simulado=simulado,
                    questao_id=questao_id,
                    ordem=ordem
                )

            # Atualizar timestamp do simulado
            simulado.ultima_modificacao = timezone.now()
            simulado.save(update_fields=['ultima_modificacao'])

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
def confirm_regenerate(request, pk):
    """View para confirmar nova geração de PDF quando já existem versões"""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

    # Buscar informações das versões existentes
    versoes_existentes = simulado.versoes_gabarito.all()[:5]  # Últimas 5
    total_versoes = simulado.get_total_versoes_gabarito()

    # URL para gerar novamente com force=true
    redirect_url = reverse('questions:gerar_pdf', kwargs={'pk': pk}) + '?force=true'

    context = {
        'simulado': simulado,
        'versoes_existentes': versoes_existentes,
        'total_versoes': total_versoes,
        'redirect_url': redirect_url,
        'mensagem_extra': 'Este simulado já possui versões geradas anteriormente.'
    }

    return render(request, 'questions/confirm_regenerate.html', context)

@login_required
def gerar_pdf(request, pk):
    """View para gerar PDF - SEMPRE com novo embaralhamento a cada download."""
    import zipfile
    from .pdf_performance_logger import PerformanceTimer, perf_logger, start_operation_timer, end_operation_timer
    import socket

    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

    # VERIFICAR SE JÁ EXISTEM VERSÕES E SE NÃO É GERAÇÃO FORÇADA
    versoes_existentes = simulado.get_total_versoes_gabarito()
    force_regenerate = request.GET.get('force', 'false').lower() == 'true'

    if versoes_existentes > 0 and not force_regenerate:
        print(f"DEBUG - Simulado {pk} já tem {versoes_existentes} versões, redirecionando para confirmação")
        return redirect('questions:confirm_regenerate', pk=pk)

    # Detectar ambiente PythonAnywhere
    IS_PYTHONANYWHERE = 'pythonanywhere' in os.environ.get('HOSTNAME', '')

    if IS_PYTHONANYWHERE:
        socket.setdefaulttimeout(300)
        import logging
        logging.getLogger('weasyprint').setLevel(logging.ERROR)

    operation_id = f"pdf_gen_{pk}_{int(time.time())}"
    start_operation_timer(operation_id, f"Geração completa de PDF para simulado {pk}")

    try:
        with PerformanceTimer("gerar_pdf_completo", user=request.user.username, simulado_id=pk):
            print(f"DEBUG - SEMPRE gerando NOVO embaralhamento para simulado {pk}")

            # SEMPRE limpar qualquer cache existente
            simulado.limpar_todo_cache()

            # Motivo sempre é novo embaralhamento
            motivo_str = "Novo embaralhamento sempre"
            perf_logger.info(f"Simulado {pk} - {motivo_str.lower()}, gerando nova versão")

            # Buscar questões apenas uma vez
            with PerformanceTimer("carregar_questoes", simulado_id=pk):
                questoes = list(simulado.questoes.all().order_by('questaosimulado__ordem'))
                perf_logger.info(f"Carregadas {len(questoes)} questões para simulado {pk}")

            if len(questoes) > 45:
                perf_logger.warning(f"Simulado {pk} excede o limite de 45 questões: tem {len(questoes)}")
                messages.error(request, 'O simulado não pode ter mais que 45 questões')
                end_operation_timer(operation_id, success=False, reason="too_many_questions")
                return redirect('questions:simulado_edit', pk=simulado.pk)

            # Criar diretório temporário para os arquivos
            with tempfile.TemporaryDirectory() as tmpdirname:
                perf_logger.debug(f"Diretório temporário criado: {tmpdirname}")

                # Arrays para armazenar resultados
                embaralhamentos = [None] * 5
                all_pdfs = [None] * 5
                cartoes_resposta = [None] * 5

                # SEMPRE gerar novos embaralhamentos
                perf_logger.info(f"Gerando NOVO embaralhamento para simulado {pk}")
                max_workers = 3 if IS_PYTHONANYWHERE else 5

                # Processamento paralelo - SEMPRE regenerar
                with PerformanceTimer("processamento_paralelo", simulado_id=pk):
                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        perf_logger.debug(f"Iniciando execução paralela com {max_workers} workers para simulado {pk}")

                        # Submeter tarefas para as versões do simulado - SEM CACHE
                        versao_futures = {
                            executor.submit(_gerar_versao_simulado, simulado, questoes, tmpdirname, versao): versao
                            for versao in range(1, 6)
                        }

                        # Coletar resultados das versões
                        for future in concurrent.futures.as_completed(versao_futures):
                            versao = versao_futures[future]
                            try:
                                pdf_path, embaralhamento = future.result()
                                all_pdfs[versao-1] = pdf_path
                                embaralhamentos[versao-1] = embaralhamento
                                perf_logger.debug(f"Versão {versao} concluída com sucesso")
                            except Exception as exc:
                                perf_logger.error(f"Erro ao gerar versão {versao}: {str(exc)}")
                                perf_logger.error(traceback.format_exc())
                                messages.error(request, f"Erro ao gerar versão {versao}: {str(exc)}")
                                end_operation_timer(operation_id, success=False, reason="version_generation_failed", version=versao)
                                return redirect('questions:simulado_edit', pk=simulado.pk)

                # Gerar cartões resposta
                with PerformanceTimer("gerar_cartoes_resposta", simulado_id=pk):
                    for versao in range(1, 6):
                        try:
                            cartao_path = _gerar_cartao_resposta(tmpdirname, versao, versao, len(questoes))
                            cartoes_resposta[versao-1] = cartao_path
                        except Exception as exc:
                            perf_logger.error(f"Erro ao gerar cartão resposta {versao}: {str(exc)}")
                            messages.error(request, f"Erro ao gerar cartão resposta {versao}: {str(exc)}")
                            end_operation_timer(operation_id, success=False, reason="answer_card_generation_failed", version=versao)
                            return redirect('questions:simulado_edit', pk=simulado.pk)

                # Verificar se todos os arquivos foram gerados
                if None in all_pdfs or None in cartoes_resposta:
                    perf_logger.error(f"Arquivos incompletos gerados para simulado {pk}")
                    messages.error(request, "Falha ao gerar alguns arquivos necessários.")
                    end_operation_timer(operation_id, success=False, reason="incomplete_files")
                    return redirect('questions:simulado_edit', pk=simulado.pk)

                # Combinar PDFs
                with PerformanceTimer("combinar_pdfs", simulado_id=pk):
                    versoes_pdf_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_todas_versoes.pdf')
                    _combinar_pdfs_versoes(all_pdfs, versoes_pdf_path)

                    cartoes_pdf_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_cartoes_resposta.pdf')
                    _combinar_pdfs_simples(cartoes_resposta, cartoes_pdf_path)

                # SEMPRE criar nova versão no histórico (para auditoria)
                with PerformanceTimer("salvar_gabaritos", simulado_id=pk):
                    nova_versao = VersaoGabarito.objects.create(
                        simulado=simulado,
                        gabaritos_gerados=embaralhamentos,
                        usuario_geracao=request.user,
                        total_questoes=len(questoes)
                    )

                    # SEMPRE definir a nova versão como oficial (mais recente)
                    simulado.versao_gabarito_oficial = nova_versao
                    simulado.save()
                    print(f"DEBUG - Nova versão definida como oficial: {nova_versao.get_versao_curta()}")

                    perf_logger.info(f"Nova versão de gabarito criada para simulado {pk}: {nova_versao.get_versao_curta()}")

                # Criar o arquivo ZIP (sempre único, sem cache)
                with PerformanceTimer("criar_zip", simulado_id=pk):
                    versao_nome = nova_versao.get_versao_curta()  # Usa o mesmo nome da página
                    zip_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_materiais_{versao_nome}.zip')

                    with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(versoes_pdf_path, os.path.basename(versoes_pdf_path))
                        zipf.write(cartoes_pdf_path, os.path.basename(cartoes_pdf_path))

                        # Arquivo README
                        readme_path = os.path.join(tmpdirname, 'README.txt')
                        with open(readme_path, 'w', encoding='utf-8') as readme:
                            readme.write(f"""SIMULADO: {simulado.titulo}
VERSÃO DO GABARITO: {nova_versao.get_versao_curta()}
GERADO EM: {nova_versao.data_geracao.strftime('%d/%m/%Y às %H:%M')}

Este pacote contém dois arquivos PDF com as questões embaralhadas em 5 versões diferentes.

IMPORTANTE: CADA DOWNLOAD GERA UM NOVO EMBARALHAMENTO COMPLETO!
Não existe cache - sempre são geradas novas ordens das questões.

CONTEÚDO:
- simulado_{simulado.pk}_todas_versoes.pdf: 5 versões embaralhadas
- simulado_{simulado.pk}_cartoes_resposta.pdf: Cartões de resposta

VERSÃO: {nova_versao.get_versao_curta()} (salva apenas para histórico)
""")
                        zipf.write(readme_path, 'README.txt')

                # Ler o ZIP e retornar
                with PerformanceTimer("ler_zip_final", simulado_id=pk):
                    with open(zip_path, 'rb') as f:
                        zip_content = f.read()

                    zip_size = len(zip_content) / 1024.0  # KB
                    perf_logger.info(f"ZIP gerado (sem cache): {zip_size:.2f} KB")

                # Finalizar logs
                perf_logger.info(f"Finalizada geração de PDF SEMPRE NOVO para simulado {pk}")
                end_operation_timer(operation_id, success=True, action="generated_always_new_pdf", size_kb=zip_size)

                # DECIDIR O RETORNO BASEADO SE É NOVA GERAÇÃO
                if force_regenerate:
                    # É nova geração - adicionar mensagem de sucesso e redirecionar
                    messages.success(request, f'PDF gerado com sucesso! Versão: {versao_nome}')

                    # Retornar o arquivo E adicionar script para redirecionamento
                    response = HttpResponse(zip_content, content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_materiais_{versao_nome}.zip"'
                    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response['Pragma'] = 'no-cache'
                    response['Expires'] = '0'

                    # Adicionar JavaScript para redirecionamento após download
                    response['X-Redirect-After-Download'] = reverse('questions:simulado_list')

                    return response
                else:
                    # Primeira geração - download normal
                    response = HttpResponse(zip_content, content_type='application/zip')
                    response['Content-Disposition'] = f'attachment; filename="simulado_{simulado.pk}_materiais_{versao_nome}.zip"'
                    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                    response['Pragma'] = 'no-cache'
                    response['Expires'] = '0'
                    return response

    except Exception as e:
        perf_logger.error(f"Erro geral ao gerar PDF para simulado {pk}: {str(e)}")
        perf_logger.error(traceback.format_exc())
        end_operation_timer(operation_id, success=False, reason="general_error", error=str(e))
        messages.error(request, f"Erro ao gerar os arquivos: {str(e)}")
        return redirect('questions:simulado_edit', pk=simulado.pk)

@time_function
def _combinar_pdfs_simples(pdfs_list, output_path):
    """Combina vários PDFs em sequência em um único arquivo, com logs."""
    with PerformanceTimer("combinar_pdfs_simples",
                         extra_data={'num_pdfs': len(pdfs_list)}):
        from PyPDF2 import PdfWriter, PdfReader

        writer = PdfWriter()
        total_pages = 0

        for i, pdf_path in enumerate(pdfs_list):
            with PerformanceTimer(f"processar_pdf_{i+1}",
                                 extra_data={'arquivo': os.path.basename(pdf_path)}):
                reader = PdfReader(pdf_path)
                num_pages = len(reader.pages)
                total_pages += num_pages

                for page in reader.pages:
                    writer.add_page(page)

                perf_logger.debug(f"PDF {i+1}: {num_pages} páginas processadas")

        perf_logger.debug(f"Escrevendo PDF combinado com {total_pages} páginas: {output_path}")
        with open(output_path, 'wb') as f:
            writer.write(f)

        log_file_size(output_path, "PDFs Combinados")
        return output_path

@time_function
def _combinar_pdfs_versoes(pdfs_list, output_path):
    """
    Combina as versões dos simulados em um único PDF, garantindo que cada versão
    termine com um número par de páginas, com logs detalhados.
    """
    with PerformanceTimer("combinar_pdfs_versoes",
                        extra_data={'num_pdfs': len(pdfs_list), 'saida': os.path.basename(output_path)}):
        from PyPDF2 import PdfWriter, PdfReader
        import io
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        writer = PdfWriter()
        total_paginas = 0
        paginas_adicionadas = 0

        # Função para criar uma página em branco
        def criar_pagina_branca():
            with PerformanceTimer("criar_pagina_branca"):
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=A4)
                c.setFillColorRGB(1, 1, 1)  # Branco
                c.circle(1, 1, 1, fill=1)  # Pequeno círculo invisível para garantir que a página seja válida
                c.save()
                packet.seek(0)
                return PdfReader(packet).pages[0]

        # Para cada versão do simulado
        for i, pdf_path in enumerate(pdfs_list):
            with PerformanceTimer(f"processar_versao_{i+1}",
                               extra_data={'arquivo': os.path.basename(pdf_path)}):
                # Adicionar um marcador sutil da versão no canto da primeira página
                reader = PdfReader(pdf_path)
                num_paginas = len(reader.pages)
                total_paginas += num_paginas

                # Adicionar as páginas do simulado
                for j, page in enumerate(reader.pages):
                    writer.add_page(page)
                    paginas_adicionadas += 1

                perf_logger.debug(f"Versão {i+1}: {num_paginas} páginas processadas")

                # Se a versão tem um número ímpar de páginas, adicionar uma página em branco
                if num_paginas % 2 == 1:
                    writer.add_page(criar_pagina_branca())
                    paginas_adicionadas += 1
                    perf_logger.debug(f"Adicionada página em branco após versão {i+1}")

        # Salvar o PDF combinado
        with PerformanceTimer("salvar_pdf_combinado"):
            with open(output_path, 'wb') as f:
                writer.write(f)

            log_file_size(output_path, "PDF Combinado de Versões")
            perf_logger.info(f"PDF combinado gerado com {paginas_adicionadas} páginas ({total_paginas} originais)")

        return output_path

@time_function
def _gerar_versao_simulado(simulado, questoes, tmpdirname, versao):
    """Função para gerar uma versão do simulado SEMPRE com novo embaralhamento - SEM CACHE."""
    with PerformanceTimer(f"gerar_versao_simulado_{versao}",
                         simulado_id=simulado.pk,
                         extra_data={'num_questoes': len(questoes)}):

        print(f"DEBUG - Gerando versão {versao} com NOVO embaralhamento para simulado {simulado.pk}")

        # Detectar ambiente
        IS_PYTHONANYWHERE = 'pythonanywhere' in os.environ.get('HOSTNAME', '')

        # SEMPRE embaralhar as questões para esta versão - SEM VERIFICAR CACHE
        with PerformanceTimer("embaralhar_questoes", simulado_id=simulado.pk,
                            extra_data={'versao': versao}):
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

        # Pré-processar as imagens (sem cache)
        with PerformanceTimer("pre_processar_imagens", simulado_id=simulado.pk,
                            extra_data={'versao': versao}):
            imagens_count = 0
            for q in questoes_shuffled:
                if q.imagem:
                    imagens_count += 1
                    q.imagem_path = q.imagem.path if os.path.exists(q.imagem.path) else None

                    # Otimizar imagens para melhor performance
                    if hasattr(q.imagem, 'path') and os.path.exists(q.imagem.path) and IS_PYTHONANYWHERE:
                        try:
                            from PIL import Image
                            import io

                            img = Image.open(q.imagem.path)
                            buffer = io.BytesIO()
                            img.save(buffer, format=img.format or 'JPEG', optimize=True, quality=85)
                            q.imagem_otimizada = buffer.getvalue()
                        except Exception as e:
                            perf_logger.warning(f"Erro ao otimizar imagem: {str(e)}")

            perf_logger.debug(f"Versão {versao}: {imagens_count} imagens processadas")

        # SEMPRE renderizar novo HTML - SEM CACHE
        with PerformanceTimer("renderizar_html", simulado_id=simulado.pk,
                            extra_data={'versao': versao}):
            html_string = render_to_string('questions/simulado_pdf.html', {
                'simulado': simulado,
                'questoes': questoes_shuffled,
                'versao': versao,
                'MEDIA_ROOT': settings.MEDIA_ROOT,
                'is_pythonanywhere': IS_PYTHONANYWHERE
            })

            # Otimização: Simplificar HTML para processamento mais rápido
            import re
            html_string = re.sub(r'<!--.*?-->', '', html_string, flags=re.DOTALL)
            html_string = re.sub(r'\s{2,}', ' ', html_string)

            perf_logger.debug(f"HTML para versão {versao} gerado NOVO: {len(html_string)/1024:.2f} KB")

        # SEMPRE gerar novo PDF - SEM CACHE
        with PerformanceTimer("gerar_pdf_weasyprint", simulado_id=simulado.pk,
                             extra_data={'versao': versao}):
            versao_pdf_path = os.path.join(tmpdirname, f'simulado_{simulado.pk}_v{versao}.pdf')

            # Configuração otimizada para WeasyPrint
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration

            # Configurar fonte específica para evitar subsetting excessivo
            font_config = FontConfiguration()

            # Reduzir logging e avisos
            import logging
            import warnings

            if IS_PYTHONANYWHERE:
                logging.getLogger('weasyprint').setLevel(logging.ERROR)
                warnings.filterwarnings("ignore", category=UserWarning)

            # CSS adicional para garantir uso de fontes simples
            css_simples = CSS(string='''
                @page { size: A4; margin: 1cm; }
                body, p, div, span, h1, h2, h3, h4, h5, h6 {
                    font-family: Arial, Helvetica, sans-serif !important;
                }
            ''')

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # Gerar o PDF com configuração otimizada
                html = HTML(string=html_string, base_url=settings.BASE_DIR)
                html.write_pdf(
                    versao_pdf_path,
                    font_config=font_config,
                    stylesheets=[css_simples],
                    optimize_size=('fonts',)
                )

            # SEM CACHE - não armazenar PDF gerado
            # Apenas registrar tamanho do arquivo gerado
            log_file_size(versao_pdf_path, f"PDF Versão {versao} (SEMPRE NOVO)")

        return versao_pdf_path, ordem_atual
@time_function
def _gerar_cartao_resposta(tmpdirname, caderno, tipo, num_questoes):
    """Versão otimizada da função de geração de cartão resposta com logs."""
    with PerformanceTimer(f"gerar_cartao_resposta_tipo{tipo}",
                         extra_data={'num_questoes': num_questoes, 'caderno': caderno}):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm

        nome_arquivo = os.path.join(tmpdirname, f'Cartao_Resposta_{caderno}_Tipo{tipo}.pdf')
        perf_logger.debug(f"Gerando cartão resposta: {nome_arquivo}")

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
    log_file_size(nome_arquivo, f"Cartão Resposta Tipo {tipo}")
    return nome_arquivo

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

            # Capturar pontuação total (campo simples)
            pontuacao_total = request.POST.get('pontuacao_total', 5)
            try:
                simulado.pontuacao_total = int(pontuacao_total)
                if simulado.pontuacao_total <= 0:
                    simulado.pontuacao_total = 5
            except (ValueError, TypeError):
                simulado.pontuacao_total = 5
                messages.warning(request, 'Valor de pontuação inválido. Usando valor padrão: 5')

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

@login_required
def simulado_gabaritos_historico(request, pk):
    """View para exibir o histórico de gabaritos de um simulado."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

    # Buscar todas as versões de gabarito (histórico)
    versoes = simulado.get_historico_gabaritos()

    # ✅ LÓGICA CORRIGIDA - Só define oficial se NÃO EXISTIR nenhuma
    # NÃO sobrescreve escolhas manuais do usuário
    if versoes.exists() and not simulado.versao_gabarito_oficial:
        versao_mais_recente = versoes.first()  # Primeira = mais recente (order by -data_geracao)
        simulado.versao_gabarito_oficial = versao_mais_recente
        simulado.save()
        print(f"DEBUG - Primeira versão oficial definida: {versao_mais_recente.get_versao_curta()}")
    elif versoes.exists() and simulado.versao_gabarito_oficial:
        # Verificar se a versão oficial ainda existe no histórico
        if not versoes.filter(versao_id=simulado.versao_gabarito_oficial.versao_id).exists():
            # Só redefine se a versão oficial atual foi deletada
            versao_mais_recente = versoes.first()
            simulado.versao_gabarito_oficial = versao_mais_recente
            simulado.save()
            print(f"DEBUG - Versão oficial inexistente substituída: {versao_mais_recente.get_versao_curta()}")
        else:
            print(f"DEBUG - Mantendo versão oficial escolhida: {simulado.versao_gabarito_oficial.get_versao_curta()}")

    # Paginação
    paginator = Paginator(versoes, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Estatísticas simplificadas
    total_versoes = simulado.get_total_versoes_gabarito()
    ultima_versao = versoes.first() if versoes.exists() else None

    # Informações adicionais
    total_questoes = simulado.questoes.count()
    tem_questoes = total_questoes > 0

    context = {
        'simulado': simulado,
        'page_obj': page_obj,
        'total_versoes': total_versoes,
        'ultima_versao': ultima_versao,
        'total_questoes': total_questoes,
        'tem_questoes': tem_questoes,
        'versao_oficial': simulado.versao_gabarito_oficial,
        'questoes_alteradas': False,
        'aviso_novo_sistema': True,
    }

    return render(request, 'questions/simulado_gabaritos_historico.html', context)

@login_required
def visualizar_gabarito_versao(request, pk, versao_id):
    """View para visualizar uma versão específica do gabarito."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
    versao = get_object_or_404(VersaoGabarito, simulado=simulado, versao_id=versao_id)

    # Processar os gabaritos para exibição
    gabaritos_processados = []
    versoes_data = []

    if versao.gabaritos_gerados:
        try:
            # Processar os dados de gabarito para facilitar uso no template
            for versao_data in versao.gabaritos_gerados:
                versoes_data.append({'gabarito': versao_data.get('gabarito', {})})

            # Obter todas as chaves de questões da primeira versão
            if versao.gabaritos_gerados:
                primeira_versao = versao.gabaritos_gerados[0]
                questao_indices = list(primeira_versao.get('gabarito', {}).keys())

                # Ordenar questões numericamente
                questao_indices.sort(key=lambda x: int(x))

                # Para cada questão, obter as respostas em cada versão
                for questao_idx in questao_indices:
                    row = {'questao_idx': int(questao_idx)}

                    # Obter resposta para cada versão
                    for i in range(len(versoes_data)):
                        if i < len(versao.gabaritos_gerados):
                            gabarito = versao.gabaritos_gerados[i].get('gabarito', {})
                            questao_data = gabarito.get(questao_idx, {})

                            if isinstance(questao_data, dict):
                                resposta = questao_data.get('tipo1', '-')
                            else:
                                resposta = str(questao_data) if questao_data else '-'

                            row[f'versao_{i+1}'] = resposta
                        else:
                            row[f'versao_{i+1}'] = '-'

                    # Preencher versões restantes se necessário
                    for i in range(len(versao.gabaritos_gerados), 5):
                        row[f'versao_{i+1}'] = '-'

                    gabaritos_processados.append(row)

        except Exception as e:
            logger.error(f"Erro ao processar gabaritos da versão {versao_id}: {str(e)}")
            messages.error(request, f"Erro ao processar gabaritos: {str(e)}")
            versoes_data = []
            gabaritos_processados = []

    # Verificar se há resultados vinculados
    tem_resultados = versao.tem_resultados_vinculados()

    # Verificar se é a versão mais recente
    ultima_versao = simulado.get_historico_gabaritos().first()
    is_mais_recente = ultima_versao and ultima_versao.versao_id == versao.versao_id

    # Estatísticas da versão
    total_versoes_simulado = simulado.get_total_versoes_gabarito()
    posicao_versao = list(simulado.get_historico_gabaritos().values_list('versao_id', flat=True)).index(versao.versao_id) + 1

    context = {
        'simulado': simulado,
        'versao': versao,
        'versoes': versoes_data,
        'gabaritos_processados': gabaritos_processados,
        'tem_resultados': tem_resultados,
        'is_mais_recente': is_mais_recente,
        'total_versoes_simulado': total_versoes_simulado,
        'posicao_versao': posicao_versao,
        'aviso_historico': True,  # Indica que é apenas histórico
    }

    return render(request, 'questions/visualizar_gabarito_versao.html', context)

@login_required
def comparar_versoes_gabarito(request, pk):
    """View para comparar duas versões de gabarito do histórico."""
    simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

    # Obter as versões para comparação dos parâmetros GET
    versao1_id = request.GET.get('versao1')
    versao2_id = request.GET.get('versao2')

    # Buscar todas as versões disponíveis para seleção
    versoes_disponiveis = simulado.get_historico_gabaritos()

    # Contexto base
    context = {
        'simulado': simulado,
        'versoes_disponiveis': versoes_disponiveis,
        'total_versoes': simulado.get_total_versoes_gabarito(),
        'aviso_historico': True,  # Indica que é apenas histórico
    }

    # Se ambas as versões foram selecionadas, fazer a comparação
    if versao1_id and versao2_id:
        try:
            # Converter strings para UUID se necessário
            if isinstance(versao1_id, str):
                versao1_id = uuid.UUID(versao1_id)
            if isinstance(versao2_id, str):
                versao2_id = uuid.UUID(versao2_id)

            # Buscar as versões no histórico
            versao1 = simulado.versoes_gabarito.get(versao_id=versao1_id)
            versao2 = simulado.versoes_gabarito.get(versao_id=versao2_id)

            # Verificar se as versões são diferentes
            if versao1.versao_id == versao2.versao_id:
                messages.warning(request, 'Você selecionou a mesma versão para comparação.')
                return render(request, 'questions/comparar_versoes_gabarito.html', context)

            # Comparar as versões
            diferencas = _comparar_gabaritos(versao1, versao2)

            # Adicionar informações das versões
            versao1_info = {
                'versao': versao1,
                'versao_curta': versao1.get_versao_curta(),
                'data_geracao': versao1.data_geracao,
                'total_questoes': versao1.total_questoes,
                'tem_resultados': versao1.tem_resultados_vinculados(),
                'observacoes': versao1.observacoes or 'Nenhuma observação'
            }

            versao2_info = {
                'versao': versao2,
                'versao_curta': versao2.get_versao_curta(),
                'data_geracao': versao2.data_geracao,
                'total_questoes': versao2.total_questoes,
                'tem_resultados': versao2.tem_resultados_vinculados(),
                'observacoes': versao2.observacoes or 'Nenhuma observação'
            }

            # Gerar resumo da comparação
            resumo_comparacao = {
                'total_diferencas': diferencas['total_diferencas'],
                'questoes_diferentes': len(diferencas['questoes_diferentes']),
                'questoes_adicionadas': len(diferencas['questoes_adicionadas']),
                'questoes_removidas': len(diferencas['questoes_removidas']),
                'percentual_diferenca': 0
            }

            # Calcular percentual de diferença
            if versao1.total_questoes > 0:
                total_comparacoes = max(versao1.total_questoes, versao2.total_questoes)
                resumo_comparacao['percentual_diferenca'] = round(
                    (diferencas['total_diferencas'] / total_comparacoes) * 100, 2
                )

            context.update({
                'versao1_info': versao1_info,
                'versao2_info': versao2_info,
                'diferencas': diferencas,
                'resumo_comparacao': resumo_comparacao,
                'versao1_selecionada': str(versao1_id),
                'versao2_selecionada': str(versao2_id),
                'comparacao_realizada': True,
            })

            # Log da comparação
            logger.info(f"Comparação realizada entre versões {versao1.get_versao_curta()} e {versao2.get_versao_curta()} do simulado {pk}")

        except VersaoGabarito.DoesNotExist:
            messages.error(request, 'Uma das versões selecionadas não foi encontrada no histórico.')
            logger.warning(f"Tentativa de comparar versão inexistente no simulado {pk}")
        except ValueError as e:
            messages.error(request, 'ID de versão inválido fornecido.')
            logger.warning(f"ID de versão inválido na comparação do simulado {pk}: {str(e)}")
        except Exception as e:
            messages.error(request, f'Erro ao comparar versões: {str(e)}')
            logger.error(f"Erro na comparação de versões do simulado {pk}: {str(e)}")

    elif versao1_id or versao2_id:
        # Se apenas uma versão foi selecionada
        messages.info(request, 'Selecione duas versões diferentes para comparar.')

    return render(request, 'questions/comparar_versoes_gabarito.html', context)

@login_required
@require_POST
def definir_gabarito_oficial(request, pk):
    """Debug version - retorna informações detalhadas"""
    debug_info = []

    try:
        debug_info.append(f"🔍 Simulado ID: {pk}")
        simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)
        debug_info.append(f"🔍 Simulado encontrado: {simulado.titulo}")

        versao_id = request.POST.get('versao_id')
        debug_info.append(f"🔍 versao_id recebido: {versao_id}")
        debug_info.append(f"🔍 POST data: {dict(request.POST)}")

        if not versao_id:
            debug_info.append("❌ versao_id não fornecido")
            return JsonResponse({
                'success': False,
                'error': 'ID da versão não fornecido',
                'debug': debug_info
            })

        # Resto da lógica...
        versao_uuid = uuid.UUID(versao_id)
        versao = simulado.versoes_gabarito.get(versao_id=versao_uuid)
        debug_info.append(f"🔍 Versão encontrada: {versao.get_versao_curta()}")

        versao_anterior = simulado.versao_gabarito_oficial
        debug_info.append(f"🔍 Versão anterior: {versao_anterior.get_versao_curta() if versao_anterior else 'Nenhuma'}")

        simulado.versao_gabarito_oficial = versao
        simulado.save(update_fields=['versao_gabarito_oficial'])
        debug_info.append(f"✅ Simulado salvo!")

        # Verificar se salvou
        simulado.refresh_from_db()
        debug_info.append(f"🔍 Verificação: {simulado.versao_gabarito_oficial.get_versao_curta()}")

        return JsonResponse({
            'success': True,
            'message': f'Versão {versao.get_versao_curta()} definida como oficial!',
            'debug': debug_info,
            'versao_info': {
                'id': str(versao.versao_id),
                'versao_curta': versao.get_versao_curta(),
                'data_geracao': versao.data_geracao.strftime('%d/%m/%Y às %H:%M'),
            }
        })

    except Exception as e:
        debug_info.append(f"❌ ERRO: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'debug': debug_info
        })

@login_required
@require_POST
@csrf_exempt
def excluir_versao_gabarito(request, pk, versao_id):
    """
    View AJAX para excluir uma versão do histórico de gabaritos.
    ATENÇÃO: Não afeta a geração futura de PDFs.
    """
    try:
        simulado = get_object_or_404(Simulado, pk=pk, professor=request.user)

        # Converter string para UUID se necessário
        if isinstance(versao_id, str):
            versao_id = uuid.UUID(versao_id)

        versao = get_object_or_404(VersaoGabarito, simulado=simulado, versao_id=versao_id)

        # Verificar se não há resultados vinculados
        if versao.tem_resultados_vinculados():
            return JsonResponse({
                'success': False,
                'error': 'Não é possível excluir uma versão que possui resultados de alunos vinculados'
            })

        # Verificar se não é a única versão restante
        total_versoes = simulado.get_total_versoes_gabarito()
        if total_versoes <= 1:
            return JsonResponse({
                'success': False,
                'error': 'Não é possível excluir a única versão restante no histórico'
            })

        # Verificar se não é uma versão muito recente (últimas 24h)
        from django.utils import timezone
        limite_tempo = timezone.now() - timezone.timedelta(hours=24)

        if versao.data_geracao > limite_tempo:
            return JsonResponse({
                'success': False,
                'error': 'Não é possível excluir versões criadas nas últimas 24 horas'
            })

        versao_curta = versao.get_versao_curta()
        data_geracao = versao.data_geracao.strftime('%d/%m/%Y às %H:%M')

        # Excluir a versão
        versao.delete()

        return JsonResponse({
            'success': True,
            'message': f'Versão {versao_curta} (gerada em {data_geracao}) excluída do histórico com sucesso',
            'aviso': 'A exclusão do histórico não afeta gerações futuras de PDF.',
            'versoes_restantes': simulado.get_total_versoes_gabarito()
        })

    except VersaoGabarito.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Versão não encontrada no histórico'})
    except ValueError:
        return JsonResponse({'success': False, 'error': 'ID de versão inválido'})
    except Exception as e:
        logger.error(f"Erro ao excluir versão do histórico: {str(e)}")
        return JsonResponse({'success': False, 'error': f'Erro interno: {str(e)}'})

# FUNÇÃO AUXILIAR: Comparar Gabaritos
def _comparar_gabaritos(versao1, versao2):
    """Compara duas versões de gabarito e retorna as diferenças."""
    diferencas = {
        'questoes_diferentes': [],
        'questoes_adicionadas': [],
        'questoes_removidas': [],
        'total_diferencas': 0
    }

    if not versao1.gabaritos_gerados or not versao2.gabaritos_gerados:
        return diferencas

    # Comparar primeira versão de cada gabarito (pode ser expandido para comparar todas)
    gab1 = versao1.gabaritos_gerados[0].get('gabarito', {}) if versao1.gabaritos_gerados else {}
    gab2 = versao2.gabaritos_gerados[0].get('gabarito', {}) if versao2.gabaritos_gerados else {}

    # Questões em comum
    questoes_comuns = set(gab1.keys()) & set(gab2.keys())

    # Questões diferentes
    for questao in questoes_comuns:
        resp1 = gab1[questao].get('tipo1', '') if isinstance(gab1[questao], dict) else gab1[questao]
        resp2 = gab2[questao].get('tipo1', '') if isinstance(gab2[questao], dict) else gab2[questao]

        if resp1 != resp2:
            diferencas['questoes_diferentes'].append({
                'questao': questao,
                'resposta_v1': resp1,
                'resposta_v2': resp2
            })

    # Questões adicionadas (presentes em v2 mas não em v1)
    questoes_adicionadas = set(gab2.keys()) - set(gab1.keys())
    for questao in questoes_adicionadas:
        resp2 = gab2[questao].get('tipo1', '') if isinstance(gab2[questao], dict) else gab2[questao]
        diferencas['questoes_adicionadas'].append({
            'questao': questao,
            'resposta': resp2
        })

    # Questões removidas (presentes em v1 mas não em v2)
    questoes_removidas = set(gab1.keys()) - set(gab2.keys())
    for questao in questoes_removidas:
        resp1 = gab1[questao].get('tipo1', '') if isinstance(gab1[questao], dict) else gab1[questao]
        diferencas['questoes_removidas'].append({
            'questao': questao,
            'resposta': resp1
        })

    diferencas['total_diferencas'] = (
        len(diferencas['questoes_diferentes']) +
        len(diferencas['questoes_adicionadas']) +
        len(diferencas['questoes_removidas'])
    )

    return diferencas
