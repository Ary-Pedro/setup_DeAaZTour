# INFO: controle de model
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    Group,
    Permission,
    User,
)
from django.db import models

# INFO: funções uso geral
from django.core.exceptions import ValidationError
from math import floor
from datetime import datetime, timedelta, date

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Count
from django.db.models import Sum


# INFO: Dados de funcionário
#  utilizando o User padrão de Django com auxílio do BaseUserManager e AbstractUser
# NOTE: atribuir superUser com funcionário
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# NOTE: acrescentar elementos com auxilio do AbstractUser
class CustomUser_Funcionario(AbstractUser):
    token = models.CharField(null=True, unique=True, max_length=8)
    situacao = (
        ("Adm.", "Administração "),
        ("Func.", "Funcionário"),
        ("Exec", "Executivo"),
    )
    situacao_atual = models.CharField(
        null=True,
        max_length=15,
        default="Adm.",
        verbose_name="Situacao atual cargo",
        choices=situacao,
    )

    situacao2 = (("Ativo", "Ativo "), ("Inativo", "Inativo"))
    situacao_atual_empresa = models.CharField(
        null=True,
        max_length=15,
        default="Ativo",
        verbose_name="Situação atual na empresa",
        choices=situacao2,
    )

    salario = models.FloatField(default=0)
    comissao_acumulada = models.FloatField(default=0)

    telefone = models.CharField(max_length=15, blank=True)

    especializado = (
        ("Financeiro", "Financeiro"),
        ("Despachante", "Despachante "),
        ("Despachante externo", "Despachante externo "),
        ("Suporte Whatsapp", "Suporte Whatsapp"),
        ("Executivo contas", "Executivo contas"),
    )

    cargo_atual = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Cargo atual",
        default="",
        help_text="A função do empregado é:",
        choices=especializado,
    )

    cidade = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    data_nascimento = models.DateField(
        verbose_name="Data de nascimento", help_text="Data de nascimento", null=True
    )
    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )

    objects = CustomUserManager()

    # NOTE: Revisar quais funções realmente está ou ficara em uso!
    def definir_nome(self):
        nome = f"{self.first_name} {self.last_name}"
        return nome

    def idade_Func(self):
        if self.data_nascimento:
            hoje = date.today()
            resto = hoje.month - self.data_nascimento.month
            idade = ((hoje.year - self.data_nascimento.year) * 12 + resto) / 12
            idade = floor(idade)
            return idade
        else:
            return None

    def verificar_email(self):
        func = CustomUser_Funcionario.objects.filter(email=self.email).first()

        if func:
            return func.senha

        else:
            raise ValidationError("E-mail não encontrado.")

    def calcular_comissao(self):
        """Calcula a comissão com base na situação e cargo do vendedor e acumula."""
        comissao = 0

        # Calcula o total de vendas do mês
        total_vendas_mes = Venda.objects.filter(
            vendedor=self,
            situacaoMensal="Mensal"
        ).aggregate(Sum("valor"))["valor__sum"] or 0

        # Situação: Administração (Adm.) - 3% do total de vendas Mensais
        if self.situacao_atual == "Adm.":
            total_vendas_mes = Venda.objects.filter(

                situacaoMensal="Mensal"
            ).aggregate(Sum("valor"))["valor__sum"] or 0

            comissao = total_vendas_mes * 0.03

        # Comissão para Funcionários
        elif self.situacao_atual == "Func.":
            if self.cargo_atual == "Despachante":
                comissao = total_vendas_mes * 0.15
            elif self.cargo_atual == "Despachante externo":
                comissao = total_vendas_mes * 0.40
            elif self.cargo_atual == "Suporte Whatsapp":
                comissao = 0  # Sem comissão

        # Atualiza a comissão acumulada e salva
        self.comissao_acumulada = comissao
        self.save()


# INFO: Dados de clientes
class CadCliente(models.Model):
    nome = models.CharField(
        max_length=100,
        null=False,
        verbose_name="Nome",
        help_text="Digite o nome aqui.",
    )

    celular = models.CharField(
        max_length=15,
        null=False,
        verbose_name="Celular",
        help_text="Digite seu Telefone aqui. como no exemplo: (21) 9xxxx-xxxx",
    )

    sexo_tipo = (("M", "Masculino"), ("F", "Feminino"))
    sexo = models.CharField(max_length=1, choices=sexo_tipo, verbose_name="Sexo")
    data_nascimento = models.DateField(
        verbose_name="Data de nascimento", help_text="Data de nascimento"
    )
    endereco = models.CharField(
        max_length=200,
        null=True,
        verbose_name="Endereço",
        help_text="Digite a endereço aqui.",
        blank=True
    )
    bairro = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Bairro ",
        help_text="Digite a bairro aqui.",
        blank=True
    )
    estado = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Estado",
        help_text="Digite a estado aqui.",
        blank=True
    )
    cep = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        verbose_name="cep",
        help_text="Digite o cep aqui.",
    )

    # NOTE: campos de função para idade e data
    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            resto = hoje.month - self.data_nascimento.month
            idade = ((hoje.year - self.data_nascimento.year) * 12 + resto) / 12
            idade = floor(idade)
            return idade
        else:
            return None

    rg = models.CharField(max_length=20, verbose_name="RG", null=False)

    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        verbose_name="CPF",
        help_text="Digite o CPF aqui modelo: 000.000.000-00",
    )

    num_passaporte = models.CharField(
        max_length=20, verbose_name="Número de passaporte", null=True, unique=True, blank=True
    )

    finished_at = models.DateField(null=True, verbose_name="Data finalizado")

    def mark_has_complete(self):
        if not self.finished_at:
            self.finished_at = date.today()
            self.save()

    def __str__(self):
        return self.nome

    anexo1 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao cliente."
    )

    anexo2 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao cliente."
    )

    anexo3 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao cliente."
    )

    def get_anexo1_nome(self):
        import os
        return os.path.basename(self.anexo1.name) if self.anexo1 else None

    def get_anexo2_nome(self):
        import os
        return os.path.basename(self.anexo2.name) if self.anexo2 else None

    def get_anexo3_nome(self):
        import os
        return os.path.basename(self.anexo3.name) if self.anexo3 else None


# INFO: Dados de Venda (funcionário - cliente)
# WARNING -- ---- --- --- -----
# INFO: Dados de Venda (funcionário - cliente)
class Venda(models.Model):
    SITUACAO_CHOICES = [
        ("Mensal", "Mensal"),
        ("Finalizada", "Finalizada"),
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

    tipo_servico = models.CharField(
        max_length=5000,
        null=True,
        verbose_name="Tipo de venda",
        help_text="Digite o tipo de serviço aqui.",
    )
    nacionalidade = models.CharField(
        max_length=20,
        choices=[
            ("Americano", "Americano"),
            ("Canadense", "Canadense"),
            ("Mexicano", "Mexicano"),
            ("Outros", "Outros"),
        ],
        default="Americano",
        blank=True,
        null=True,
    )
    nacionalidade_outros = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Especifique se você escolheu "Outros".',
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
