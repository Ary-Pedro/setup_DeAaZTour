from apps.service.models import Venda, Anexo
from apps.service.widgets import MultipleFileField
from django import forms


class VendaForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        label="Anexos",
        help_text="Selecione um ou mais arquivos para anexar."
    )
   

    class Meta:
        model = Venda
        fields = [
            "vendedor", "valor", "tipo_pagamento", "situacaoMensal", "arquivos"
        ]
   
    def save(self, commit=True):
     venda = super().save(commit=commit)

 # Atualizar arquivos anexados
     arquivos = self.files.getlist('arquivos')
     for arquivo in arquivos:
         if not Anexo.objects.filter(venda=venda, arquivo=arquivo.name).exists():
            Anexo.objects.create(arquivo=arquivo, venda=venda)
     return venda
   
   
   