from django import forms
from .models import Questao, Simulado
from ckeditor.widgets import CKEditorWidget

from django import forms
from .models import Questao, Simulado
from ckeditor.widgets import CKEditorWidget

class QuestaoForm(forms.ModelForm):
    class Meta:
        model = Questao
        fields = [
            'disciplina',
            'conteudo',
            'enunciado',
            'imagem',
            'alternativa_a',
            'alternativa_b',
            'alternativa_c',
            'alternativa_d',
            'alternativa_e',
            'resposta_correta',
            'nivel_dificuldade'
        ]
        widgets = {
            'enunciado': CKEditorWidget(config_name='default'),
            'alternativa_a': CKEditorWidget(config_name='alternativas'),
            'alternativa_b': CKEditorWidget(config_name='alternativas'),
            'alternativa_c': CKEditorWidget(config_name='alternativas'),
            'alternativa_d': CKEditorWidget(config_name='alternativas'),
            'alternativa_e': CKEditorWidget(config_name='alternativas'),
        }


class SimuladoForm(forms.ModelForm):
    class Meta:
        model = Simulado
        fields = ['titulo', 'descricao', 'cabecalho', 'instrucoes']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-light',
                'placeholder': 'Digite o título do simulado'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light',
                'rows': 3,
                'placeholder': 'Digite uma descrição para o simulado'
            }),
            'cabecalho': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light',
                'rows': 4
            }),
            'instrucoes': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light',
                'rows': 4
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        # Aqui você pode adicionar validações adicionais se necessário
        return cleaned_data

class QuestaoFilterForm(forms.Form):
    disciplina = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control bg-dark text-light',
        'placeholder': 'Filtrar por disciplina'
    }))
    conteudo = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control bg-dark text-light',
        'placeholder': 'Filtrar por conteúdo'
    }))
    nivel_dificuldade = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos')] + Questao.NIVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'})
    )
