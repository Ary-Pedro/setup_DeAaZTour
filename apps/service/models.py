from django.db import models
from django.db.models import Sum

# INFO: funções uso geral
from math import floor
from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.worker.models import Funcionario
from apps.client.models import Cliente


# WARNING -- ---- --- --- -----
# INFO: Dados de Venda (funcionário - Cliente)
class Venda(models.Model):
    tipo_mensal = [
        ("Mensal", "Mensal"),
        ("Finalizada", "Finalizada"),
        ("Cancelada", "Cancelada"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(
        Funcionario, on_delete=models.CASCADE, null=True, blank=True)
    situacaoMensal = models.CharField(
        max_length=10,
        choices=tipo_mensal,
        default="Mensal",
        null=True,
        blank=True,
    )
    
    situacaoMensal_dataApoio = models.DateField(auto_now_add=True)
    data_venda = models.DateField(auto_now_add=True)
    finished_at = models.DateField(null=True, verbose_name="Data finalizado")
    duracao_venda = models.CharField(null=True, max_length=20, verbose_name="Duração da venda em dias")
    valor = models.FloatField()
    nacionalidade = models.CharField(
        max_length=20,
        choices=[
            ("Americano", "Americano"),
            ("Canadense", "Canadense"),
            ("Mexicano", "Mexicano"),
            ("Outros", "Outros"),
        ],
        blank=True,
        null=True,
    )
    nacionalidade_outros = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Especifique se você escolheu "Outros".',
    )

    tipo_cidadania = models.CharField(
        max_length=50,
        choices=[
            ("Pai para filho", "Pai para filho"),
            ("Cônjuge", "Cônjuge"),
            ("Avô para neto", "Avô para neto"),
            ("Outros", "Outros"),
        ],
        blank=True,
        null=True,
    )
    tipo_cidadania_outros = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Especifique se você escolheu "Outros".',
    )

    tipo_servico = models.CharField(
        max_length=50,
        choices=[
            ("Vistos", "Vistos"),
            ("Cidadania", "Cidadania"),
            ("PID", "PID"),
            ("Autorizações Eletrônicas", "Autorizações Eletrônicas"),
            ("Transcrição de Casamento", "Transcrição de Casamento"),
            ("Pesquisa de Assento", "Pesquisa de Assento"),
            ("Passaporte", "Passaporte"),
            ("Cartão Cidadão ", "Cartão Cidadão "),
            ("Representação ", "Representação "),
            ("Retirada de Documento", "Retirada de Documento"),
            ("Agendamento de Urgencia", "Agendamento de Urgencia"),
            ("Agendamento de Emergência", "Agendamento de Emergência"),
            ("Identidade", "Identidade"),
            ("Global Visa", "Global Visa"),
            ("Atendimento Domiciliar", "Atendimento Domiciliar"),
        ],
        blank=True,
        null=True,
    )

    tipo_servico_outros = models.CharField(
        max_length=5000,
        blank=True,
        null=True,
        verbose_name="Tipo de venda",
        help_text="Digite o tido de serviço aqui.",
    )

    tipo_pagamento = models.CharField(
        max_length=50,
        choices=[
            ("Dinheiro", "Dinheiro"),
            ("Crédito", "Crédito"),
            ("Débito", "Débito"),
            ("Pix", "Pix"),
        ],
        default="Dinheiro",
        blank=True,
        null=True,
        verbose_name="Forma de pagamento:",

    )

    def _str_(self):
        return f"Venda {self.id} - {self.cliente.nome} para {self.vendedor.username}"

    
    def mark_as_complete(self):
        if not self.finished_at:
            self.finished_at = date.today()

        if self.situacaoMensal_dataApoio and self.finished_at:
            # Garantir que ambos são instâncias de date
            situacaoMensal_dataApoio_date = self.situacaoMensal_dataApoio
            finished_at_date = self.finished_at

            # Converter para tipo correto, se não for None
            if isinstance(situacaoMensal_dataApoio_date, str):
                situacaoMensal_dataApoio_date = date.fromisoformat(situacaoMensal_dataApoio_date)

            if isinstance(finished_at_date, str):
                finished_at_date = date.fromisoformat(finished_at_date)

            delta = finished_at_date - situacaoMensal_dataApoio_date
            self.duracao_venda = f"{delta.days} Dias"
            self.save()
                
    def calcular_comissao_vendedor(vendedor):
        """Calcula a comissão acumulada para um vendedor específico."""
        total_vendas = Venda.objects.filter(vendedor=vendedor).aggregate(Sum("valor"))["valor__sum"]
        comissao = 0
        if vendedor.departamento == "Vend":
            if vendedor.especializacao_funcao == "Despachante":
                comissao = total_vendas * 0.15
            elif vendedor.especializacao_funcao == "Despachante externo":
                comissao = total_vendas * 0.40
            elif vendedor.especializacao_funcao == "Suporte Whatsapp":
                comissao = 0  # Sem comissão
        return comissao

    @staticmethod
    def calcular_comissao_administrador():
        """Calcula a comissão acumulada para todos os administradores."""
        total_vendas_mensal = Venda.objects.filter(situacaoMensal="Mensal").aggregate(Sum("valor"))["valor__sum"]
        comissao = total_vendas_mensal * 0.30
        return comissao

@receiver(post_save, sender=Venda)
def atualizar_comissao_acumulada(sender, instance, **kwargs):
    """Atualiza a comissão acumulada do vendedor e dos administradores sempre que uma venda for salva."""
    if instance.vendedor:
        # Atualiza a comissão do vendedor
        vendedor = instance.vendedor
        vendedor.comissao_acumulada = Venda.calcular_comissao_vendedor(vendedor)
        vendedor.save()

        # Atualiza a comissão dos administradores
        administradores = Funcionario.objects.filter(departamento="Adm")
        comissao_adm = Venda.calcular_comissao_administrador()
        for adm in administradores:
            adm.comissao_acumulada = comissao_adm
            adm.save()