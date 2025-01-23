from django import forms
from client.models import CadCliente
from django.core.exceptions import ValidationError
import re


class CadClienteForm(forms.ModelForm):
    class Meta:
        model = CadCliente
        fields = [
            "nome",
            "celular",
            "cpf",
            "rg",
            "sexo",
            "data_nascimento",
            "num_passaporte",
            "endereco",
            "bairro",
            "estado",
            "cep",
            "anexo1",
            "anexo2",
            "anexo3",
        ]

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        if any(char.isdigit() for char in nome):
            raise ValidationError("O nome não pode conter números.")
        return nome

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        if len(cpf) != 11 or not cpf.isdigit():
            raise ValidationError("O CPF deve conter exatamente 11 dígitos numéricos.")
        return cpf

    def clean_celular(self):
        celular = self.cleaned_data.get("celular")
        pattern = r"^\d{10,11}$"
        if not re.match(pattern, celular):
            raise ValidationError(
                "O celular deve conter apenas números com 10 ou 11 dígitos."
            )
        return celular
