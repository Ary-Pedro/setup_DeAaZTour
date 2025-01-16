'''
from django.db import models

# INFO: funções uso geral
from math import floor
from datetime import date

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from worker.models import CustomUser_Funcionario
from client.models import CadCliente


# WARNING -- ---- --- --- -----
# INFO: Dados de Venda (funcionário - Cliente)
class Venda(models.Model):
    SITUACAO_CHOICES = [
        ("Mensal", "Mensal"),
        ("Finalizada", "Finalizada"),
        ("Cancelada", "Cancelada"),
    ]

    cliente = models.ForeignKey(CadCliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(
        CustomUser_Funcionario, on_delete=models.CASCADE, null=True, blank=True
    )
    situacaoMensal = models.CharField(
        max_length=10,
        choices=SITUACAO_CHOICES,
        default="Mensal",
        null=True,
        blank=True,
        verbose_name="Situação da venda",
    )
    situacaoMensal_dataApoio = models.DateTimeField(
        auto_now_add=True
    )  # Registra quando foi atualizada a última vez
    data_venda = models.DateField(auto_now_add=True)
    valor = models.FloatField()
    finished_at = models.DateField(null=True, verbose_name="Data finalizado")

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
            self.situacaoMensal = "Finalizada"
            self.save()

    @classmethod
    def rank_vendedores(cls):
        """Retorna os vendedores rankeados por número de vendas."""
        vendas = (
            cls.objects.values(
                "vendedor__first_name",
                "vendedor__last_name",
                "vendedor__telefone",
                "vendedor__email",
            )
            .annotate(total_vendas=models.Count("id"))
            .order_by("-total_vendas")
        )
        return vendas

    @classmethod
    def reset_rank(cls):
        """Atualiza a situação de todas as vendas de 'Mensal' para 'Finalizada'."""
        cls.objects.filter(situacaoMensal="Mensal").update(situacaoMensal="Finalizada")



# WARNING -- ---- --- --- -----
# Sinal para redefinir a quantidade de vendas ao final do mês
@receiver(post_save, sender=Venda)
def calcular_comissao_automaticamente(sender, instance, created, **kwargs):
    """Calcula automaticamente a comissão após uma venda ser salva ou editada."""
    if created:
        vendedor = instance.vendedor
        vendedor.calcular_comissao()

@receiver(post_delete, sender=Venda)
def recalcular_comissao_apos_exclusao(sender, instance, **kwargs):
    """Recalcula a comissão ao excluir uma venda."""
    vendedor = instance.vendedor
    vendedor.calcular_comissao()
'''