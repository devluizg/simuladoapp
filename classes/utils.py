import pandas as pd
from io import BytesIO
import PyPDF2
import re

from classes.models import Student

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
                students.append({
                    'name': name,
                    'email': None  # PDF normalmente não terá email
                })
    
    return students

def extract_students_from_excel(excel_file):
    """Extrai nomes de alunos de um arquivo Excel do Diário de Classe Digital."""
    df = pd.read_excel(excel_file)
    
    # Procura por colunas de nome e email
    name_column = None
    email_column = None
    
    # Procura por colunas com nomes
    for col in df.columns:
        col_lower = col.lower().strip()
        if 'aluno' in col_lower or 'nome' in col_lower:
            name_column = col
        elif 'email' in col_lower or 'e-mail' in col_lower:
            email_column = col
    
    if name_column is None:
        raise ValueError("Não foi possível encontrar a coluna com nomes dos alunos")
    
    students = []
    for _, row in df.iterrows():
        name = str(row[name_column]).strip()
        if name and name.lower() != 'nan' and name.lower() != 'aluno(a)':
            email = str(row[email_column]).strip() if email_column else None
            # Verifica se o email é válido
            if email and (email.lower() == 'nan' or len(email) < 5):
                email = None
                
            students.append({
                'name': name,
                'email': email
            })
    
    return students

def process_students_file(file, turma):
    """Processa o arquivo e cria os alunos na turma especificada."""
    if file.name.endswith('.pdf'):
        students_data = extract_students_from_pdf(file)
    elif file.name.endswith('.xlsx') or file.name.endswith('.xls'):
        students_data = extract_students_from_excel(file)
    else:
        raise ValueError("Formato de arquivo não suportado")
    
    # Criar os alunos com IDs sequenciais
    for i, student_data in enumerate(students_data, 1):
        student = Student.objects.create(
            name=student_data['name'],
            email=student_data['email'],
            student_id=i
        )
        student.classes.add(turma)
    
    return len(students_data)  # Retorna quantidade de alunos criados