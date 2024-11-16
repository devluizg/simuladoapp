from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from io import BytesIO
import os
from django.conf import settings
from django.template.loader import render_to_string

def generate_pdf(simulado):
    # Renderiza o template HTML
    html_string = render_to_string('questions/simulado_pdf.html', {
        'simulado': simulado,
        'questoes': simulado.questoes.all(),
    })
    
    # Cria um arquivo PDF
    result = BytesIO()
    
    # Configurações do PDF
    pdf_options = {
        'page-size': 'A4',
        'margin-top': '2cm',
        'margin-right': '2cm',
        'margin-bottom': '2cm',
        'margin-left': '2cm',
        'allow-spliting': True,
    }
    
    # Converte HTML para PDF com as configurações
    pdf = pisa.CreatePDF(
        BytesIO(html_string.encode('UTF-8')),
        result,
        encoding='UTF-8',
        link_callback=fetch_resources
    )
    
    if not pdf.err:
        return HttpResponse(
            result.getvalue(),
            content_type='application/pdf'
        )
    return None

def fetch_resources(uri, rel):
    """
    Callback para recuperar recursos (imagens, etc)
    """
    if uri.startswith('http'):
        return uri
    
    if uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    elif uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.STATIC_ROOT, uri.replace(settings.STATIC_URL, ""))
    else:
        path = os.path.join(settings.STATIC_ROOT, uri)
    
    if not os.path.isfile(path):
        return uri
        
    return path