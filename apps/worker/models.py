from datetime import date
from math import floor
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import (
    AbstractUser,
    BaseUserManager,
    Group,
    Permission,
    User,
)

from django.core.exceptions import ValidationError



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
    #um supperUser é um usuário que tem todos os privilégios
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        #is_staff, Staff é uma pessoa quem tem acesso a parte administrativa do sistema
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

# NOTE: acrescentar elementos com auxilio do AbstractUser
class CustomUser_Funcionario(AbstractUser):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50,verbose_name="primeiro nome") 
    last_name = models.CharField(max_length=50, verbose_name="último nome")
    nome = models.CharField(max_length=101, editable=False,null=True)
    idade = models.IntegerField(null=True, editable=False)
    username = models.CharField(max_length=255, unique=True, verbose_name="apelido")
    email = models.EmailField(unique=True, verbose_name="e-mail")
    tefone = models.CharField(max_length=15)#formata no Js para (00) 00000-0000 // lembrando que o 9 no começo ainda n é funcional em todo brasil
    salario = models.FloatField(default=0, verbose_name="salário")
    comissao_acumulada = models.FloatField(default=0, verbose_name="comissão acumulada")
    telefone = models.CharField(max_length=15, blank=True)
    cidade = models.CharField(max_length=255, null=True)
    data_nascimento = models.DateField(verbose_name="Data de nascimento", null=True)
    token = models.CharField(null=True, unique=True, max_length=8)    
    area_departamento = (
        ("Adm", "Administrativo"),
        ("Vend", "Vendedor"),
        ("Exec", "Executivo"),
    )
    departamento = models.CharField(
        null=True,
        max_length=15,
        default="Adm", #lembrar de mudar para Funcionario, quando for ativar o sistema.
        choices=area_departamento,
    )

    #usar logica do Djanngo
    xpto = (("Ativo", "Ativo "), ("Inativo", "Inativo"))# Lógica de inativo é alterar o campo is_active para False
    atividade = models.CharField(
        null=True,
        max_length=15,
        default="Ativo",
        verbose_name="",
        choices=xpto,
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
        verbose_name="especialização",
        default="",
        help_text="A função a qual o empregado exerce é:",
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
        func = CustomUser_Funcionario.objects.filter(email=self.email).first()
        if func:
            return func.senha
        else:
            raise ValidationError("E-mail não encontrado.")


    def save(self, *args, **kwargs):
        self.nome = f"{self.first_name} {self.last_name}"
        self.idade = idade_Func(self)
        if self.atividade == "Inativo":
            self.is_active = False
        else:
            self.is_active = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    objects = CustomUserManager()
    
'''
service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='funcionarios')
agencies = models.ManyToManyField(Agency, related_name='funcionarios')
'''

@receiver(pre_save, sender=CustomUser_Funcionario)
def idade_Func(sender, instance, **kwargs):
    if instance.data_nascimento:
        hoje = date.today()
        resto = hoje.month - instance.data_nascimento.month
        idade = ((hoje.year - instance.data_nascimento.year) * 12 + resto) / 12
        idade = floor(idade)
        return idade
    else:
        return None

@receiver(pre_save, sender=CustomUser_Funcionario)
def update_nome(sender, instance, **kwargs):
    instance.nome = f"{instance.first_name} {instance.last_name}"