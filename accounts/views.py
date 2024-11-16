from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import CustomUserCreationForm
import uuid
from django.contrib.auth.forms import SetPasswordForm
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()

def generate_unique_username(first_name):
    """Gera um username único baseado no primeiro nome."""
    username = first_name.lower()
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{first_name.lower()}{counter}"
        counter += 1
    return username

def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        # Verifica se é uma solicitação de reenvio
        if 'resend_email' in request.POST:
            email = request.POST.get('email')
            try:
                user = User.objects.get(email=email, is_active=False)
                
                # Atualiza o token e a data de expiração
                user.activation_token = uuid.uuid4()
                user.activation_token_expiry = timezone.now() + timedelta(days=2)
                user.save()
                
                # Reenvia o email
                activation_link = request.build_absolute_uri(
                    reverse('accounts:activate', kwargs={'token': str(user.activation_token)})
                )
                
                html_message = render_to_string('accounts/activation_email.html', {
                    'user': user,
                    'activation_link': activation_link,
                })
                
                send_mail(
                    'Ative sua conta - Novo Link',
                    strip_tags(html_message),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                messages.success(
                    request,
                    'Um novo email de ativação foi enviado. Por favor, verifique sua caixa de entrada.'
                )
                return redirect('accounts:login')
            except User.DoesNotExist:
                messages.error(
                    request,
                    'Email não encontrado ou conta já ativada.'
                )
                return redirect('accounts:register')

        # Processo normal de registro
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = generate_unique_username(form.cleaned_data['first_name'])
            user.is_active = False
            user.activation_token = uuid.uuid4()
            user.activation_token_expiry = timezone.now() + timedelta(days=2)
            user.save()
            
            # Envio do email de confirmação
            activation_link = request.build_absolute_uri(
                reverse('accounts:activate', kwargs={'token': str(user.activation_token)})
            )
            
            html_message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'activation_link': activation_link,
            })
            
            try:
                send_mail(
                    'Ative sua conta',
                    strip_tags(html_message),
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                # Retorna JSON se for uma requisição AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'email': user.email,
                        'message': 'Cadastro realizado com sucesso! Por favor, verifique seu email para ativar sua conta.'
                    })
                
                messages.success(
                    request,
                    'Cadastro realizado com sucesso! Por favor, verifique seu email para ativar sua conta.'
                )
                return redirect('accounts:login')
            
            except Exception as e:
                user.delete()
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Erro ao enviar email de confirmação. Por favor, tente novamente.'
                    })
                messages.error(request, 'Erro ao enviar email de confirmação. Por favor, tente novamente.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def activate_account(request, token):
    try:
        user = User.objects.get(activation_token=token, is_active=False)
        if timezone.now() < user.activation_token_expiry:
            user.is_active = True
            user.email_verified = True
            user.save()
            
            messages.success(request, 'Sua conta foi ativada com sucesso! Agora você pode fazer login.')
            return render(request, 'accounts/activation_success.html')
        else:
            messages.error(request, 'O link de ativação expirou. Por favor, registre-se novamente.')
            return render(request, 'accounts/activation_failed.html')
    except User.DoesNotExist:
        messages.error(
            request,
            'O link de ativação é inválido ou já foi usado. Por favor, tente se registrar novamente.'
        )
        return render(request, 'accounts/activation_failed.html')


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Pegando o site atual
            current_site = get_current_site(request)
            domain = current_site.domain
            protocol = 'https' if request.is_secure() else 'http'

            # Renderiza o template do e-mail
            html_message = render_to_string('accounts/password_reset_email.html', {
                'user': user,
                'domain': domain,
                'protocol': protocol,
                'uid': uid,
                'token': token,
            })

            # Envia o e-mail
            send_mail(
                'Redefinição de Senha',
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(
                request,
                'Email enviado! Verifique sua caixa de entrada para redefinir sua senha.'
            )
            return redirect('accounts:password_reset_done')

        except User.DoesNotExist:
            messages.error(
                request,
                'Não encontramos uma conta com este email. Verifique se digitou corretamente.'
            )
    
    return render(request, 'accounts/password_reset.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Sua senha foi redefinida com sucesso!')
                return redirect('accounts:password_reset_complete')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form, 'validlink': True})
    else:
        messages.error(request, 'O link de redefinição de senha é inválido ou expirou.')
        return render(request, 'accounts/password_reset_confirm.html', {'validlink': False})

def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')

def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')

@login_required
def resend_activation(request):
    if request.method == 'POST':
        user = request.user
        
        # Verifica se o email já está verificado
        if user.email_verified:
            messages.info(request, 'Seu email já está verificado.')
            return redirect('accounts:dashboard')
        
        # Verifica se já foi enviado um email recentemente
        if hasattr(user, 'activation_token_expiry') and user.activation_token_expiry:
            time_since_last_email = timezone.now() - user.activation_token_expiry + timedelta(days=1)
            if time_since_last_email < timedelta(minutes=5):
                messages.warning(request, 
                    'Por favor, aguarde 5 minutos antes de solicitar um novo email de verificação.')
                return redirect('accounts:dashboard')
        
        # Gera novo token e atualiza data de expiração
        user.activation_token = uuid.uuid4()
        user.activation_token_expiry = timezone.now() + timedelta(days=1)
        user.save()
        
        # Prepara e envia o email
        activation_link = request.build_absolute_uri(
            reverse('accounts:activate', kwargs={'token': str(user.activation_token)})
        )
        
        context = {
            'user': user,
            'activation_link': activation_link,
        }
        
        html_message = render_to_string('accounts/email/activation_email.html', context)
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                'Ative sua conta - Novo Link',
                plain_message,
                None,  # Usa o DEFAULT_FROM_EMAIL do settings.py
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, 
                'Um novo email de verificação foi enviado. Por favor, verifique sua caixa de entrada.')
        except Exception as e:
            messages.error(request, 
                'Ocorreu um erro ao enviar o email. Por favor, tente novamente mais tarde.')
            
    return redirect('accounts:dashboard')

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('accounts:dashboard')
        
    return redirect('accounts:dashboard')