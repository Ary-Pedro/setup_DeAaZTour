from datetime import datetime
from django import forms
from apps.client.widgets import MultipleFileField
from apps.client.models import Cliente, Anexo
from django.core.exceptions import ValidationError

def validar_cpf(cpf):
    if not cpf:
        raise ValidationError("O CPF não pode ficar vazio!")
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
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
    telefone1 = forms.CharField(
        label="Telefone 1",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone2 = forms.CharField(
        label="Telefone 2",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    data_nascimento = forms.CharField(
    label="Data nascimento",
    required=False,
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cpf = forms.CharField(
        label="CPF",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"}),
        help_text="Para evitar erros, esse campo não pode ser vazio."
    )
    cep = forms.CharField(
        label="CEP",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    nome = forms.CharField(
        label="Nome",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite o nome completo"}))
    class Meta:
        model = Cliente
        fields = [
            "nome",
            "telefone1",
            "telefone2",
            "email1",
            "email2",
            "data_nascimento",
            "endereco",
            "cidade",
            "bairro",
            "estado",
            "cep",
            "cpf",
            "num_passaporte",
            "cep",
            'arquivos'
        ]

    def clean_nome(self):
        nome = self.cleaned_data.get("nome")
        if any(char.isdigit() for char in nome):
            raise ValidationError("O nome não pode conter números.")
        return nome.upper()

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf")
        validar_cpf(cpf)
        return cpf



   
class AtualizarForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
    telefone1 = forms.CharField(
        label="Telefone 1",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    telefone2 = forms.CharField(
        label="Telefone 2",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Para customizar use '+' no início"})
    )
    data_nascimento = forms.CharField(
        label="Data nascimento",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    cpf = forms.CharField(
        label="CPF",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"}),
        help_text="Para evitar erros, esse campo não pode ser vazio."
    )
    cep = forms.CharField(
        label="CEP",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    nome = forms.CharField(
        label="Nome",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Digite o nome completo"})
    )
    sexo = forms.ChoiceField(
        label="Sexo",
        choices=[("", "---------"), ("F", "Feminino"), ("M", "Masculino"), ("O", "Outro")],
        required=False,
        widget=forms.Select(attrs={'onchange': 'toggleFields()'})
    )
    sexo_outros = forms.CharField(
        label="Especifique o sexo",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Digite o sexo'}),
        help_text="Preencha apenas quando selecionar 'Outro'"
    )

    class Meta:
        model = Cliente
        fields = [
            "nome",
            "telefone1",
            "telefone2",
            "email1",
            "email2",
            "sexo",
            "sexo_outros",
            "data_nascimento",
            "endereco",
            "cidade",
            "bairro",
            "estado",
            "cep",
            "rg",
            "cpf",
            "num_passaporte",
            "arquivos"
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Garante que o valor do sexo_outros está disponível para o template
            if self.instance.sexo_outros:
                self.fields['sexo_outros'].initial = self.instance.sexo_outros
            # Configura o valor inicial do campo sexo
            self.fields['sexo'].initial = self.instance.sexo

    def save(self, commit=True):
        cliente = super().save(commit=False)
        
        # Tratamento específico para o campo sexo
        sexo = self.cleaned_data.get('sexo')
        sexo_outros = self.cleaned_data.get('sexo_outros')
        
        if sexo == 'O':
            if sexo_outros:
                cliente.sexo_outros = sexo_outros
            else:
                # Se selecionou "Outro" mas não preencheu, mantém o valor anterior ou define como vazio
                cliente.sexo_outros = cliente.sexo_outros or ""
        else:
            cliente.sexo_outros = None
        
        if commit:
            cliente.save()
            # Processamento dos arquivos (mantido igual)
            arquivos = self.files.getlist('arquivos')
            for arquivo in arquivos:
                if not Anexo.objects.filter(cliente=cliente, arquivo=arquivo.name).exists():
                    Anexo.objects.create(arquivo=arquivo, cliente=cliente)
        
        return cliente