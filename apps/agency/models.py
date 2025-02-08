from django.db import models
from apps.worker.models import Funcionario
from django.db.models.signals import post_save
from django.dispatch import receiver

# INFO: Dados das agencias
class Agencia(models.Model):
    funcionarios = models.ManyToManyField(Funcionario, through='Executivo_registros')
    id = models.AutoField(primary_key=True)
    nome_contato = models.CharField(max_length=101, verbose_name="nome do contato")
    nome_fantasia = models.CharField(max_length=200, verbose_name="nome fantasia da agência")
    email1 = models.EmailField(null=True, blank=True, verbose_name="e-mail 1", max_length=255)
    email2 = models.EmailField(null=True, blank=True, verbose_name="e-mail 2", max_length=255)
    email3 = models.EmailField(null=True, blank=True, verbose_name="e-mail 3", max_length=255)
    telefone1 = models.CharField(null=True, blank=True, verbose_name="telefone 1", max_length=20)
    telefone2 = models.CharField(null=True, blank=True, verbose_name="telefone 2", max_length=20)
    telefone3 = models.CharField(null=True, blank=True, verbose_name="telefone 3", max_length=20)
    contato_ano = models.CharField(max_length=15, null=True, blank=True, verbose_name="ano de contato", help_text="Formato: DD/MM/YYYY")
    cnpj = models.CharField(max_length=18, unique=True, null=True, verbose_name="CNPJ")
    cep = models.CharField(max_length=9, null=True, blank=True, verbose_name="CEP", help_text="Formato: XXXXX-XXX")
    municipio = models.CharField(null=True, max_length=100, verbose_name="município")
    uf = models.CharField(null=True, max_length=2, verbose_name="UF")
    logradouro = models.CharField(null=True, max_length=255, verbose_name="logradouro", help_text="Rua | Avenida | Alameda | Travessa")
    numero = models.CharField(null=True, max_length=10, verbose_name="número")
    complemento = models.CharField(max_length=255, null=True, blank=True, verbose_name="complemento")
    bairro = models.CharField(null=True, max_length=100, verbose_name="bairro")
    observacao = models.TextField(null=True, blank=True, verbose_name="Observação", max_length=2000)

    def __str__(self):
        return self.nome_fantasia

class Executivo_registros(models.Model):
    id = models.AutoField(primary_key=True)
    agencia = models.ForeignKey(Agencia, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.funcionario.nome} - {self.agencia.nome}"

@receiver(post_save, sender=Agencia)
def criar_executivo_registros(sender, instance, created, **kwargs):
    if created:
        funcionarios = Funcionario.objects.filter(especializacao_funcao="Executivo contas")
        for funcionario in funcionarios:
            Executivo_registros.objects.create(agencia=instance, funcionario=funcionario)