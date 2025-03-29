from datetime import datetime
from apps.service.models import Venda, Anexo
from apps.service.widgets import MultipleFileField
from django import forms
from django.db.models import Q

from apps.worker.models import Funcionario



class VendaForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
    Agencia_recomendada = forms.CharField(
        required=False,
        label="Agência Recomendada",
        help_text="Digite o nome da agência que recomendou."
    )
    recomendação_da_Venda = forms.CharField(
        required=False,
        label="Recomendação da Venda",
        help_text="Digite o nome da pessoa que recomendou."
    )
    valor = forms.FloatField(
        required=False,
        label="Valor",
        widget=forms.TextInput(attrs={"placeholder": "Digite o Valor padrão da venda."})
    )
    desconto = forms.FloatField(
        required=False,
        label="Desconto",
        widget=forms.TextInput(attrs={"placeholder": "Digite o desconto, será considerada em porcentagem (%)."})
    )

    class Meta:
        model = Venda
        fields = [
            "vendedor", "situacaoMensal", "valor", "desconto", "tipo_pagamento", 
            "Agencia_recomendada", "recomendação_da_Venda", "arquivos"
        ]

    def clean(self):
        """Validação personalizada para o status executivo"""
        cleaned_data = super().clean()
        agencia = cleaned_data.get("Agencia_recomendada")
        recomendacao = cleaned_data.get("recomendação_da_Venda")

        # Se algum dos campos estiver preenchido, define status_executivo como True
        if agencia or recomendacao:
            self.instance.status_executivo = True
        else:
            self.instance.status_executivo = False
        
        return cleaned_data

    def save(self, commit=True):
        """Salva a venda e os anexos"""
        venda = super().save(commit=commit)

        # Atualizar arquivos anexados
        arquivos = self.files.getlist("arquivos")
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
    desconto = forms.FloatField(
    required=False,
    label="Desconto",
    widget=forms.TextInput(attrs={"placeholder": "Digite o desconto, será considerada em porcentagem (%)."}),
    )
    class Meta:
        model = Venda
        fields = [
            "vendedor","executivo", "situacaoMensal", "data_venda" ,"finished_at", "valor", "desconto", "tipo_pagamento", "Agencia_recomendada", "recomendação_da_Venda", "arquivos"
        ]
    def clean(self):
        """Validação personalizada para o status executivo"""
        cleaned_data = super().clean()
        agencia = cleaned_data.get("Agencia_recomendada")
        recomendacao = cleaned_data.get("recomendação_da_Venda")
        
        if agencia or recomendacao:
            self.instance.status_executivo = True
        else:
            self.instance.status_executivo = False
            # Define o campo executivo como None no cleaned_data
            cleaned_data['executivo'] = None
        
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Verificar o valor de status_executivo, se for False, desabilitar o campo executivo
        if not self.instance.status_executivo:
            self.fields['executivo'].queryset = Funcionario.objects.none()  # Isso limpa a queryset, deixando o campo sem opções
        else:
            # Se o status_executivo for True, permite a seleção dos executivos
            self.fields['executivo'].queryset = Funcionario.objects.filter(departamento='Exec')
        
        self.fields['vendedor'].queryset = Funcionario.objects.filter(
            Q(departamento='Vend') | Q(departamento='Adm')
        )

    def save(self, commit=True):
     venda = super().save(commit=commit)

 # Atualizar arquivos anexados
     arquivos = self.files.getlist('arquivos')
     for arquivo in arquivos:
         if not Anexo.objects.filter(venda=venda, arquivo=arquivo.name).exists():
            Anexo.objects.create(arquivo=arquivo, venda=venda)
     return venda
   
   