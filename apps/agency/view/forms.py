from django import forms
from django.core.exceptions import ValidationError
from apps.agency.models import Agencia
import re
# WARING adicionar deixar campo vazio, e arrumar digitações em geral como cnpj e cep ...
def validar_cnpj(cnpj):
    if len(cnpj) != 18 :
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

    def clean_telefone1(self):
        telefone1 = self.cleaned_data.get("telefone1")
        telefone2 = self.cleaned_data.get("telefone2")
        telefone3 = self.cleaned_data.get("telefone3")

        if telefone1 and (telefone1 == telefone2 or telefone1 == telefone3):
            raise ValidationError("O telefone1 não pode ser igual aos outros telefones.")
        return telefone1

    def clean_telefone2(self):
        telefone2 = self.cleaned_data.get("telefone2")
        telefone1 = self.cleaned_data.get("telefone1")
        telefone3 = self.cleaned_data.get("telefone3")

        if telefone2 and (telefone2 == telefone1 or telefone2 == telefone3):
            raise ValidationError("O telefone2 não pode ser igual aos outros telefones.")
        return telefone2

    def clean_telefone3(self):
        telefone3 = self.cleaned_data.get("telefone3")
        telefone1 = self.cleaned_data.get("telefone1")
        telefone2 = self.cleaned_data.get("telefone2")

        if telefone3 and (telefone3 == telefone1 or telefone3 == telefone2):
            raise ValidationError("O telefone3 não pode ser igual aos outros telefones.")
        return telefone3
        

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

        

    