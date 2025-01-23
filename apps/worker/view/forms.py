from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError
from apps.worker.models import (
    CustomUser_Funcionario,
)  # Use o modelo de usuário personalizado


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


class RegisterForm(forms.Form):
    log = forms.CharField(label="Apelido", max_length=50)
    logpass = forms.CharField(label="Senha", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Nome", max_length=50)
    last_name = forms.CharField(label="Sobrenome", max_length=50)
    email = forms.EmailField(label="E-mail")
    telefone = PhoneNumberField(label="Telefone", region="BR")
    cpf = forms.CharField(label="CPF", max_length=14)

    def clean_telefone(self):
        telefone = self.cleaned_data.get("telefone")
        if telefone and len(str(telefone)) < 10:
            raise forms.ValidationError(
                "O número de telefone deve conter pelo menos 10 dígitos."
            )
        return telefone

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        validar_cpf(cpf)
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser_Funcionario.objects.filter(
            email=email
        ).exists():  # Use o modelo de usuário personalizado
            raise ValidationError("Este e-mail já está registrado.")
        return email

    def clean_log(self):
        log = self.cleaned_data.get("log")
        if CustomUser_Funcionario.objects.filter(
            username=log
        ).exists():  # Use o modelo de usuário personalizado
            raise ValidationError("Este apelido já está registrado.")
        return log
