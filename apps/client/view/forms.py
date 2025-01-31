from django import forms
from apps.client.models import Cliente
from django.core.exceptions import ValidationError
import re

def validar_cpf(cpf):
    if not cpf:
        raise ValidationError("O CPF não pode ser nulo!")
    if len(cpf) != 14:
        raise ValidationError("O CPF deve ter 14 caracteres!")
    for i, char in enumerate(cpf):
        if i in [3, 7] and char != ".":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '.'")
        elif i == 11 and char != "-":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '-'")
        elif i not in [3, 7, 11] and not char.isdigit():
            raise ValidationError(f"O caracter na posição {i + 1} deve ser um dígito.")


class ClienteForm(forms.ModelForm):
    telefone1 = forms.CharField(
    label="Telefone 1",
    widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone2 = forms.CharField(
    label="Telefone 2",
    widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
   
    data_nascimento = forms.CharField(
    label="data_nascimento",
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cpf = forms.CharField(
    label="cpf",
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cep = forms.CharField(
    label="CEP",
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )

    class Meta:
        model = Cliente
        fields = [
            "nome",
            "telefone1",
            "telefone2",
            "celular",
            "email1",
            "email2",
            "sexo",
            "data_nascimento",
            "endereco",
            "cidade",
            "bairro",
            "estado",
            "cep",
            "rg",
            "cpf",
            "num_passaporte",
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
            validar_cpf(cpf)
            return cpf

    def clean_email1(self):
            email1 = self.cleaned_data.get("email1")
            if Cliente.objects.filter(email1=email1).exists() or \
            Cliente.objects.filter(email2=email1).exists():
                raise ValidationError("e-mail 1: Este e-mail já está registrado.")
            return email1

    def clean_email2(self):
        email2 = self.cleaned_data.get("email2")
        if Cliente.objects.filter(email1=email2).exists() or \
        Cliente.objects.filter(email2=email2).exists():
            raise ValidationError("e-mail 2: Este e-mail já está registrado.")
        return email2