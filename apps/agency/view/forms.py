from django import forms
from django.core.exceptions import ValidationError
from apps.agency.models import Agencia
import re

def validar_cnpj(cnpj):
    if not cnpj:
        raise ValidationError("O CNPJ não pode ser nulo!")
    if len(cnpj) != 18:
        raise ValidationError("O CNPJ deve ter 18 caracteres!")
    for i, char in enumerate(cnpj):
        if i in [2, 6] and char != ".":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '.'")
        elif i == 10 and char != "/":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '/'")
        elif i == 15 and char != "-":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '-'")
        elif i not in [2, 6, 10, 15] and not char.isdigit():
            raise ValidationError(f"O caracter na posição {i + 1} deve ser um dígito.")



class AgenciaForm(forms.ModelForm):
    telefone1 = forms.CharField(
        label="Telefone 1",
        required=False,  # Adicione esta linha
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone2 = forms.CharField(
        label="Telefone 2",
        required=False,  # Adicione esta linha
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone3 = forms.CharField(
        label="Telefone 3",
        required=False,  # Adicione esta linha
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    contato_ano = forms.CharField(
        label="Contato Ano",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cnpj = forms.CharField(
        label="CNPJ",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cep = forms.CharField(
        label="CEP",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )

    class Meta:
        model = Agencia
        fields = [
            'nome_contato',
            'nome_fantasia',
            'email1',
            'email2',
            'email3',
            'telefone1',
            'telefone2',
            'telefone3',
            'contato_ano',
            'cnpj',
            'cep',
            'municipio',
            'uf',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'observacao',
        ]


    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")
        validar_cnpj(cnpj)
        if Agencia.objects.filter(cnpj=cnpj).exists():
            raise ValidationError("Este CNPJ já está registrado.")
        return cnpj

    def clean_contato_ano(self):
        contato_ano = self.cleaned_data.get("contato_ano")
        if contato_ano and not re.match(r"^\d{2}/\d{2}/\d{4}$", contato_ano):
            raise ValidationError("O ano de contato deve estar no formato DD/MM/YYYY.")
        return contato_ano
    
class AtualizarForm(forms.ModelForm):
    telefone1 = forms.CharField(
        label="Telefone 1",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone2 = forms.CharField(
        label="Telefone 2",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone3 = forms.CharField(
        label="Telefone 3",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    contato_ano = forms.CharField(
        label="Contato Ano",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cnpj = forms.CharField(
        label="CNPJ",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cep = forms.CharField(
        label="CEP",required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )

    class Meta:
        model = Agencia
        fields = [
            'nome_contato',
            'nome_fantasia',
            'email1',
            'email2',
            'email3',
            'telefone1',
            'telefone2',
            'telefone3',
            'contato_ano',
            'cnpj',
            'cep',
            'municipio',
            'uf',
            'logradouro',
            'numero',
            'complemento',
            'bairro',
            'observacao',
        ]
        def clean_cnpj(self):
            cnpj = self.cleaned_data.get("cnpj")
            validar_cnpj(cnpj)
            if Agencia.objects.filter(cnpj=cnpj).exclude(pk=self.instance.pk).exists():
                raise ValidationError("Este CNPJ já está registrado.")
            return cnpj