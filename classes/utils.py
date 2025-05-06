import pandas as pd
from io import BytesIO
import PyPDF2
import re

def extract_students_from_pdf(pdf_file):
    """Extrai nomes de alunos de um arquivo PDF do Diário de Classe Digital."""
    students = []
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    
    for page in pdf_reader.pages:
        text = page.extract_text()
        # Padrão atualizado para pegar apenas os nomes, ignorando números
        pattern = r'\d+\s+([A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\s]+(?:\s+[A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\s]+)*)'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            name = match.group(1).strip()
            if name and len(name) > 2:  # Evita nomes muito curtos
                # Verificar se o nome já existe na lista
                if not any(s['name'] == name for s in students):
                    students.append({
                        'name': name,
                        'email': None  # PDF normalmente não terá email
                    })
    
    return students

def extract_students_from_excel(excel_file):
    """Extrai nomes de alunos de um arquivo Excel do Diário de Classe Digital."""
    try:
        df = pd.read_excel(excel_file)
    except Exception as e:
        raise ValueError(f"Erro ao ler arquivo Excel: {str(e)}")
    
    # Procura por colunas de nome e email
    name_column = None
    email_column = None
    
    # Procura por colunas com nomes relacionados
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'aluno' in col_lower or 'nome' in col_lower:
            name_column = col
        elif 'email' in col_lower or 'e-mail' in col_lower:
            email_column = col
    
    # Se não encontrou colunas específicas, assume que a primeira coluna contém os nomes
    if name_column is None and len(df.columns) > 0:
        name_column = df.columns[0]
    
    if name_column is None:
        raise ValueError("Não foi possível encontrar a coluna com nomes dos alunos")
    
    students = []
    for _, row in df.iterrows():
        name = str(row[name_column]).strip()
        if name and name.lower() != 'nan' and name.lower() != 'aluno(a)' and len(name) > 2:
            email = None
            if email_column:
                email_value = str(row[email_column]).strip()
                if email_value and email_value.lower() != 'nan' and '@' in email_value:
                    email = email_value
            
            # Verificar se o nome já existe na lista
            if not any(s['name'] == name for s in students):
                students.append({
                    'name': name,
                    'email': email
                })
    
    return students

def get_next_student_id(user):
    """Determina o próximo ID disponível para um novo aluno."""
    from classes.models import Student
    last_student = Student.objects.filter(user=user).order_by('-student_id').first()
    return (last_student.student_id + 1) if last_student else 1