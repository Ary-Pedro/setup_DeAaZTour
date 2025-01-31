from datetime import date
from math import floor
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import Group, Permission, AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from apps.agency.models import Agencia


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


class Funcionario(AbstractUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50, verbose_name="primeiro nome")
    last_name = models.CharField(max_length=50, verbose_name="último nome")
    nome = models.CharField(max_length=101, editable=False, null=True)
    idade = models.IntegerField(null=True, editable=False)
    username = models.CharField(max_length=255, unique=True, verbose_name="apelido")
    email = models.EmailField(unique=True, verbose_name="e-mail",max_length=255)
    Sub_salario_fixo = models.FloatField(default=0, verbose_name="salário fixo",help_text="Um valor fixo pago ao funcionario", null=True, blank=True)
    salario = models.FloatField(default=0, verbose_name="salário total",editable=False)
    comissao_acumulada = models.FloatField(default=0, verbose_name="comissão acumulada")
    telefone = models.CharField(max_length=20, null=True, blank=True,help_text="Apenas digite os números; este campo possui autoformatação")
    endereço = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=255, null=True, blank=True)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    data_nascimento = models.DateField(verbose_name="Data de nascimento", null=True, blank=True,help_text="Apenas digite os números; este campo possui autoformatação")
    token = models.CharField(null=True, unique=True, max_length=8)
    is_staff = models.BooleanField(default=True)
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF", null=True, blank=True,help_text="Apenas digite os números; este campo possui autoformatação")
    area_departamento = (
        ("Adm", "Administrativo"),
        ("Vend", "Vendedor"),
        ("Exec", "Executivo"),
    )
    departamento = models.CharField(
        max_length=15,
        default="Adm",
        choices=area_departamento,
        null=True, 
        blank=True
    )
    xpto = (("Ativo", "Ativo "), ("Inativo", "Inativo"))
    atividade = models.CharField(
        null=True, 
        blank=True,
        max_length=15,
        default="Ativo",
        choices=xpto,
        help_text="Defini se o funcionario tá ativo na empresa, ou foi desligado."
    )
    situacao_especializada = (
        ("Financeiro", "Financeiro"),
        ("Despachante", "Despachante "),
        ("Despachante externo", "Despachante externo "),
        ("Suporte Whatsapp", "Suporte Whatsapp"),
        ("Executivo contas", "Executivo contas"),
    )
    especializacao_funcao = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="especialização, área de atuação",
        default="Financeiro",
        help_text="A função a qual o empregado exerce.",
        choices=situacao_especializada,
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

    def verificar_email(self):
        func = Funcionario.objects.filter(email=self.email).first()
        if func:
            return func.senha
        else:
            raise ValidationError("E-mail não encontrado.")

    def save(self, *args, **kwargs):
        # Validações de exceções
        #validate_custom_user_funcionario(self) FROM EXEPTIONS

        # Atualização do nome completo
        self.nome = f"{self.first_name} {self.last_name}"

        # Cálculo da idade
        if self.data_nascimento:
            self.idade = self.calcular_idade()

        # Manipulação do campo is_active de acordo com a atividade
        self.is_active = self.atividade != "Inativo"

        super().save(*args, **kwargs)
    def __str__(self):
        return self.nome

    objects = CustomUserManager()

    
    def calcular_idade(self):
        if self.data_nascimento:
            hoje = date.today()
            resto = hoje.month - self.data_nascimento.month
            idade = ((hoje.year - self.data_nascimento.year) * 12 + resto) / 12
            idade = floor(idade)
            return idade
        else:
            return None
        
    def AlterarAtividade(self):
        try:
            if self.atividade == "Ativo":
                self.atividade = "Inativo"
            else:
                self.atividade = "Ativo"
            self.save()
        except Funcionario.DoesNotExist:
            raise ValidationError("erro inesperado")
      
    
        

class Executivo_registros(models.Model):
    id = models.AutoField(primary_key=True)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='vendas')
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE, related_name='vendas')
    data_venda = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venda {self.id} - {self.funcionario.nome} - {self.agencia.nome_fantasia}"
    

@receiver(pre_save, sender=Funcionario)
def update_nome(sender, instance, **kwargs):
    instance.nome = f"{instance.first_name} {instance.last_name}"

