from django import forms
from django.core.exceptions import ValidationError
import re
from .models import CadAgencia

class CadAgenciaForm(forms.ModelForm):
    class Meta:
        model = CadAgencia
        fields = [
            "nome",
            "email",
            "telefone1",
            "telefone2",
            "telefone3",
            "ano",
            "cnpj",
            "bairro",
            "cidade",
            "estado",
            "cep",
        ]

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        if any(char.isdigit() for char in nome):
            raise ValidationError("O nome não pode conter números.")
        return nome

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValidationError("Insira um endereço de email válido.")
        return email

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get("cnpj")
        if len(cnpj) != 14 or not cnpj.isdigit():
            raise ValidationError("O CNPJ deve conter exatamente 14 dígitos numéricos.")
        # Aqui você pode implementar uma validação adicional para verificar a validade do CNPJ.
        return cnpj

    def clean_telefone1(self):
        telefone = self.cleaned_data.get("telefone1")
        if not re.match(r"^\d{10,11}$", telefone):
            raise ValidationError("O telefone deve conter 10 ou 11 dígitos numéricos.")
        return telefone

    def clean_ano(self):
        ano = self.cleaned_data.get("ano")
        if ano and (ano < 1900 or ano > 2100):
            raise ValidationError("O ano deve estar entre 1900 e 2100.")
        return ano
