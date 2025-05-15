from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError
from apps.worker.models import (
    Funcionario,
    ContasMensal,
)  # Use o modelo de usuário personalizado


def validar_cpf(cpf):
    if not cpf:
        return
    if len(cpf) != 14:
        raise ValidationError("O CPF deve ter 14 caracteres!")
    for i, char in enumerate(cpf):
        if i in [3, 7] and char != ".":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '.'")
        elif i == 11 and char != "-":
            raise ValidationError(f"O caracter na posição {i + 1} deve ser '-'")
        elif i not in [3, 7, 11] and not char.isdigit():
            raise ValidationError(f"O caracter na posição {i + 1} deve ser um dígito.")


class ContasForm(forms.ModelForm):
    class Meta:
        model = ContasMensal
        fields = ["entrada", "saida", "observacao"]

    def save(self, commit=True):
        contas = super().save(commit=commit)

        return contas


# telefone = PhoneNumberField(label="Telefone", region="BR")


class RegisterForm(forms.Form):
    log = forms.CharField(label="Apelido", max_length=50)
    logpass = forms.CharField(label="Senha", widget=forms.PasswordInput)
    first_name = forms.CharField(label="Nome", max_length=50)
    last_name = forms.CharField(label="Sobrenome", max_length=50)
    email = forms.EmailField(label="E-mail")
    telefone = forms.CharField(label="Telefone")
    cpf = forms.CharField(label="CPF", max_length=14, required=False)

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        if cpf:
            validar_cpf(cpf)
            if Funcionario.objects.filter(cpf=cpf).exists():
                raise ValidationError("Este CPF já está registrado.")
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Funcionario.objects.filter(email=email).exists():
            raise ValidationError("Este e-mail já está registrado.")
        return email

    def clean_log(self):
        log = self.cleaned_data.get("log")
        if Funcionario.objects.filter(username=log).exists():
            raise ValidationError("Este apelido já está registrado.")
        return log


class AtualizarForm(forms.ModelForm):
    telefone = forms.CharField(
        label="Telefone",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Para customizar use '+' no início"}
        ),
    )

    class Meta:
        model = Funcionario
        fields = [
            "first_name",
            "last_name",
            "email",
            "telefone",
            "Sub_salario_fixo",
            "telefone",
            "endereco",
            "cidade",
            "complemento",
            "data_nascimento",
            "cpf",
            "pix",
            "departamento",
            "especializacao_funcao",
            "atividade",
        ]

    def clean_especializacao_funcao(self):
        data = self.cleaned_data.get("especializacao_funcao")
        departamento = self.cleaned_data.get("departamento")

        opcoes_permitidas = {
            "Adm": ["Financeiro", "Diretor(a)"],
            "Vend": ["Despachante", "Suporte Whatsapp"],
            "Exec": [
                "Despachante externo",
                "Executivo contas",
                "Despachante externo e Executivo contas",
            ],
        }

        if departamento in opcoes_permitidas:
            choices = opcoes_permitidas[departamento]
            if data not in choices:
                raise ValidationError(
                    f"Escolha uma especialização válida para o departamento '{departamento}'."
                )

        return data

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        validar_cpf(cpf)
        return cpf


class CompletarCadastro(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "telefone",
            "endereco",
            "cidade",
            "complemento",
            "data_nascimento",
            "cpf",
            "pix",
        ]

    username = forms.CharField(
        label="Nome de Usuário",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite seu nome de usuário"}),
    )

    first_name = forms.CharField(
        label="Primeiro Nome",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite seu primeiro nome"}),
    )

    last_name = forms.CharField(
        label="Sobrenome",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite seu sobrenome"}),
    )

    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "Digite seu e-mail"}),
    )

    telefone = forms.CharField(
        label="Telefone",
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Para customizar use '+' no início"}
        ),
    )

    endereco = forms.CharField(
        label="Endereço",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Rua, número, bairro"}),
    )

    cidade = forms.CharField(
        label="Cidade",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite sua cidade"}),
    )

    complemento = forms.CharField(
        label="Complemento",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Complemento do endereço"}),
    )

    data_nascimento = forms.CharField(
        label="Data de Nascimento",
        required=False,
    )

    pix = forms.CharField(
        label="Chave PIX",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite sua chave PIX"}),
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        if cpf:
            validar_cpf(cpf)
            if (
                Funcionario.objects.filter(cpf=cpf)
                .exclude(pk=self.instance.pk)
                .exists()
            ):
                raise ValidationError("Este CPF já está registrado.")
        return cpf
