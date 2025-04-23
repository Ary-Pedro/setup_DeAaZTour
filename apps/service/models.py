from django.db import models
from django.db.models import Sum

# INFO: funções uso geral
from datetime import date

from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.worker.models import Funcionario
from apps.client.models import Cliente


# WARNING -- ---- --- Mudar campos de executivo com 40% --- -----
OPC_SERVICES = [
    "Representação",
    "Retirada de Documento",
    "Atendimento Domiciliar",
    "Serviços para brasileiros residentes no exterior",
]

# INFO: Dados de Venda (funcionário - Cliente)
class Venda(models.Model):
    tipo_mensal = [
        ("Mensal", "Mensal"),
        ("Finalizada", "Finalizada"),
        ("Cancelada", "Cancelada"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    vendedor = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=True, blank=True)
    executivo = models.ForeignKey(Funcionario, on_delete=models.CASCADE, null=True, blank=True, related_name="executivo_vendas")
    status_executivo = models.BooleanField(default=False, null=True, blank=True, verbose_name="Status do Executivo", help_text="Marque se o executivo estiver ativo.")
    situacaoMensal = models.CharField(
        max_length=10,
        choices=tipo_mensal,
        default="Mensal",
        null=True,
        blank=True
    )

    situacaoMensal_dataApoio = models.DateField(auto_now_add=True)
    Agencia_recomendada = models.CharField(null=True, blank=True, verbose_name="Agencia Recomendada",help_text="Digite o nome da agência que recomendou.",max_length=1000)
    recomendação_da_Venda = models.CharField(null=True,blank=True, verbose_name="recomendação de Venda", help_text="Digite o nome da pessoa que recomendou.",max_length=1000)
    data_venda = models.CharField(default=date.today().strftime('%d/%m/%Y'), editable=True, max_length=15)#temporario  deve ser 
    finished_at = models.CharField(null=True, verbose_name="Data finalizado",editable=True, max_length=15)
    duracao_venda = models.CharField(null=True, max_length=20, verbose_name="Duração da venda em dias")
   
    custo_padrao_venda = models.FloatField(null=True, blank=True, help_text="Digite o Valor padrão da venda.", verbose_name="Custo da Venda")
    valor = models.FloatField(null=True, blank=True)
    desconto = models.FloatField(null=True, blank=True,help_text="Digite o valor do desconto para a venda.")
    custo_sobre_venda = models.FloatField(null=True, blank=True, help_text="Digite o custo sobre a venda.",verbose_name="Custo sobre Venda")
    
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
            ("Serviços para brasileiros residentes no exterior", "Serviços para brasileiros residentes no exterior"),
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
    @property
    def pode_editar_exec(self):
        # só permite quando status_executivo é True/1 e existe um executivo associado
        if self.status_executivo is True and self.executivo is not None:
            return False
        else: return True
        
    
    #TODO NA HORA VER A ORDEM DE VALOR RESULTANTE
    def save(self, *args, **kwargs):
        if self.custo_padrao_venda:
            self.valor = self.custo_padrao_venda

        if self.valor and self.custo_sobre_venda:
            self.valor -= self.custo_sobre_venda

        """Aplica o desconto ao valor da venda antes de salvar."""
        if self.valor and self.desconto:
            self.valor *= (1 - self.desconto / 100)
        
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venda {self.id} - {self.cliente.nome} para {self.vendedor.username if self.vendedor else 'Sem vendedor'}"

    
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
    

    #TODO: comissão do vendedor executivo e administrador
    @staticmethod
    def calcular_comissao_vendedor(vendedor):
        """Calcula a comissão do vendedor baseada em cada venda individualmente."""
        comissao = 0.00
        vendas = Venda.objects.filter(vendedor=vendedor)
        
        if vendedor.departamento != "Vend" or vendedor.especializacao_funcao != "Despachante":
            return comissao
        
        for venda in vendas:
            valor_venda = venda.valor or 0
        
            # Verifica serviços OPC com executivo
            if venda.tipo_servico in OPC_SERVICES:
                continue  # Vendedor não recebe

            if venda.executivo != "" and venda.tipo_servico not in OPC_SERVICES:
                #caso houve venda com executivo, para alteração futura
                comissao += valor_venda * 0.15
            else:
                comissao += valor_venda * 0.15
        
        return comissao


    @staticmethod
    def calcular_comissao_executivo(executivo):
        """Calcula a comissão do executivo baseada em cada venda individualmente."""
        comissao = 0.00
        vendas = Venda.objects.filter(executivo=executivo)
        
        if executivo.departamento != "Exec":
            return comissao
        #TODO: ver se são as porcentagens corretas
        for venda in vendas:
            valor_venda = venda.valor or 0
        
            if venda.tipo_servico in OPC_SERVICES:
                comissao += valor_venda * 0.40
            
            if venda.Agencia_recomendada or venda.recomendação_da_Venda:
                comissao += (valor_venda * 0.85) * 0.02  # 2% do valor após 15% do vendedor
        
        return comissao


    @staticmethod
    def calcular_comissao_administrador():
        """Calcula a comissão dos administradores baseada no total de vendas mensais."""
        comissao = 0.0  
        
        return comissao


@receiver(post_save, sender=Venda)
def atualizar_comissao_acumulada(sender, instance, **kwargs):
    """Atualiza as comissões de forma otimizada após cada venda."""
    # Atualiza vendedor
    if instance.vendedor:
        instance.vendedor.comissao_acumulada = Venda.calcular_comissao_vendedor(instance.vendedor)
        instance.vendedor.save()
    
    # Atualiza executivo
    if instance.executivo:
        instance.executivo.comissao_acumulada = Venda.calcular_comissao_executivo(instance.executivo)
        instance.executivo.save()
    
    # Atualiza administradores
    comissao_adm = Venda.calcular_comissao_administrador()
    Funcionario.objects.filter(departamento="Adm").update(comissao_acumulada=comissao_adm)
    

class Anexo(models.Model):
    arquivo = models.FileField(upload_to='anexos/')
    venda = models.ForeignKey('Venda', related_name='anexos', on_delete=models.CASCADE)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.arquivo.name