from django import forms
from django.core.exceptions import ValidationError
from apps.agency.models import Agencia
import re
# WARING adicionar deixar campo vazio, e arrumar digitações em geral como cnpj e cep ...
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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Agencia.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está registrado.")
        return email

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
    


    """
    nome_contato = forms.CharField(label="Nome do Contato", max_length=101)
    nome_fantasia = forms.CharField(label="Nome Fantasia", max_length=200)
    email = forms.EmailField(label="E-mail")
    telefone1 = forms.CharField(label="Telefone 1", max_length=20, required=False)
    telefone2 = forms.CharField(label="Telefone 2", max_length=20, required=False)
    telefone3 = forms.CharField(label="Telefone 3", max_length=20, required=False)
    contato_ano = forms.CharField(label="Ano de Contato", max_length=15, required=False)
    cnpj = forms.CharField(label="CNPJ", max_length=18)
    cep = forms.CharField(label="CEP", max_length=9, required=False)
    municipio = forms.CharField(label="Município", max_length=100)
    uf = forms.CharField(label="UF", max_length=2)
    logradouro = forms.CharField(label="Logradouro", max_length=255)
    numero = forms.CharField(label="Número", max_length=10)
    complemento = forms.CharField(label="Complemento", max_length=255, required=False)
    bairro = forms.CharField(label="Bairro", max_length=100)
    """