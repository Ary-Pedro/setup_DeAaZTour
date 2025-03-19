from datetime import datetime
from apps.service.models import Venda, Anexo
from apps.service.widgets import MultipleFileField
from django import forms


class VendaForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
    Agencia_recomendada = forms.CharField(
        required=False,
        label="Agencia Recomendada",
        help_text="Digite o nome da agência que recomendou."
    )

    recomendação_da_Venda = forms.CharField(
        required=False,
        label="Recomendação da Venda",
        help_text="Digite o nome da pessoa que recomendou."
    )
    desconto = forms.FloatField(
        required=False,
        label="Desconto",
        widget=forms.TextInput(attrs={"placeholder": "Digite o valor do desconto para a venda."}),
    )
    valor = forms.FloatField(
        required=False,
        label="Valor",
        widget=forms.TextInput(attrs={"placeholder": "Digite o Valor padrão da venda."})
        
    )
    
    class Meta:
        model = Venda
        fields = [
            "vendedor", "situacaoMensal", "valor", "desconto", "tipo_pagamento", "Agencia_recomendada", "recomendação_da_Venda", "arquivos"
        ]
   
    def save(self, commit=True):
     venda = super().save(commit=commit)

 # Atualizar arquivos anexados
     arquivos = self.files.getlist('arquivos')
     for arquivo in arquivos:
         if not Anexo.objects.filter(venda=venda, arquivo=arquivo.name).exists():
            Anexo.objects.create(arquivo=arquivo, venda=venda)
     return venda

class VendaAtualizar(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
    Agencia_recomendada = forms.CharField(
        required=False,
        label="Agencia Recomendada",
        help_text="Digite o nome da agência que recomendou."
    )

    recomendação_da_Venda = forms.CharField(
        required=False,
        label="Recomendação da Venda",
        help_text="Digite o nome da pessoa que recomendou."
    )
    desconto = forms.FloatField(
        required=False,
        label="Desconto",
        widget=forms.TextInput(attrs={"placeholder": "Digite o valor do desconto para a venda."}),
    )
    valor = forms.FloatField(
        required=False,
        label="Valor",
        widget=forms.TextInput(attrs={"placeholder": "Digite o Valor padrão da venda."})
        
    )
    data_venda = forms.CharField(
        required=False,
        label="Data da Venda",
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    finished_at = forms.CharField(
        required=False,
        label="Data Finalizado",
    widget=forms.TextInput(attrs={"placeholder": "Preencha apenas com números, a formatação será automática"})
    )
    class Meta:
        model = Venda
        fields = [
            "vendedor", "situacaoMensal", "data_venda" ,"finished_at", "valor", "desconto", "tipo_pagamento", "Agencia_recomendada", "recomendação_da_Venda", "arquivos"
        ]
    
    def save(self, commit=True):
     venda = super().save(commit=commit)

 # Atualizar arquivos anexados
     arquivos = self.files.getlist('arquivos')
     for arquivo in arquivos:
         if not Anexo.objects.filter(venda=venda, arquivo=arquivo.name).exists():
            Anexo.objects.create(arquivo=arquivo, venda=venda)
     return venda
   
   