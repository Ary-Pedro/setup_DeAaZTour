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
    class Meta:
        model = Agencia
        fields = [
            'nome_contato',
            'nome_fantasia',  # Certifique-se de que este campo existe no modelo
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

    def clean_email1(self):
        email1 = self.cleaned_data.get("email1")
        if Agencia.objects.filter(email1=email1).exists() or \
           Agencia.objects.filter(email2=email1).exists() or \
           Agencia.objects.filter(email3=email1).exists():
            raise ValidationError("e-mail 1: Este e-mail já está registrado.")
        return email1

    def clean_email2(self):
        email2 = self.cleaned_data.get("email2")
        if Agencia.objects.filter(email1=email2).exists() or \
           Agencia.objects.filter(email2=email2).exists() or \
           Agencia.objects.filter(email3=email2).exists():
            raise ValidationError("e-mail 2: Este e-mail já está registrado.")
        return email2

    def clean_email3(self):
        email3 = self.cleaned_data.get("email3")
        if Agencia.objects.filter(email1=email3).exists() or \
           Agencia.objects.filter(email2=email3).exists() or \
           Agencia.objects.filter(email3=email3).exists():
            raise ValidationError("e-mail 3: Este e-mail já está registrado.")
        return email3

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")
        validar_cnpj(cnpj)
        if Agencia.objects.filter(cnpj=cnpj).exists():
            raise ValidationError("Este CNPJ já está registrado.")
        return cnpj
    #remover alterar
    def clean_telefone1(self):
        telefone1 = self.cleaned_data.get("telefone1")
        if telefone1 and not re.match(r"^\d{10,11}$", telefone1):
            raise ValidationError("O telefone deve conter 10 ou 11 dígitos numéricos.")
        return telefone1

    def clean_contato_ano(self):
        contato_ano = self.cleaned_data.get("contato_ano")
        if contato_ano and not re.match(r"^\d{2}/\d{2}/\d{4}$", contato_ano):
            raise ValidationError("O ano de contato deve estar no formato DD/MM/YYYY.")
        return contato_ano