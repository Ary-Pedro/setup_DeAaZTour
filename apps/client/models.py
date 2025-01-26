from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from math import floor
from django.dispatch import receiver
from apps.worker.models import idade_Func
from django.db.models.signals import pre_save

# INFO: Dados de clientes
class Cliente(models.Model):
    nome = models.CharField(
        max_length=101,
        verbose_name="nome",
    )

    telefone1 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="telefone 1",
    )
    telefone2 = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="telefone 2",
    )
    celular = models.CharField(
        max_length=15,
        null=True,
        verbose_name="celular",
    )
    email1 = models.EmailField(unique=True,null=True, blank=True, verbose_name="e-mail 1", max_length=255)
    email2 = models.EmailField(unique=True, null=True, blank=True, verbose_name="e-mail 2", max_length=255)
    
    sexo_tipo = (("M", "Masculino"), ("F", "Feminino"))
    sexo = models.CharField(max_length=1, choices=sexo_tipo, verbose_name="Sexo")
    data_nascimento = models.DateField(verbose_name="Data de nascimento", null=True)
    idade = models.IntegerField(null=True, editable=False)

    endereco = models.CharField(
        max_length=200,
        null=True,
        verbose_name="endereço",
        blank=True
    )

    cidade = models.CharField(
        max_length=100,
        null=True,
        verbose_name="cidade",
        blank=True
    )
    bairro = models.CharField(
        max_length=100,
        null=True,
        verbose_name="bairro",
        blank=True
    )
    estado = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Estado",
        blank=True
    )
    cep = models.CharField(
        max_length=14,
        null=True,
        blank=True,
        verbose_name="CEP",
    )


    rg = models.CharField(max_length=20, verbose_name="RG", null=False)

    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        verbose_name="CPF",
    )

    num_passaporte = models.CharField(
        max_length=20, verbose_name="número de passaporte", null=True, unique=True, blank=True
    )
    #remover
    finished_at = models.DateField(null=True, verbose_name="Data finalizado")

    created_at = models.DateTimeField(auto_now_add=True)

    anexo1 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao Cliente."
    )

    anexo2 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao Cliente."
    )

    anexo3 = models.FileField(
        upload_to='anexos/',  # Define o diretório onde os arquivos serão armazenados
        null=True,
        blank=True,
        verbose_name="Anexo",
        help_text="Envie um arquivo relacionado ao Cliente."
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
    
    #mudar ou remover
    def mark_has_complete(self):
        if not self.finished_at:
            self.finished_at = date.today()
            self.save()

    def __str__(self):
        return self.nome
    
     
    def save(self, *args, **kwargs):
        if self.data_nascimento:
            self.idade = calcular_idade(self.data_nascimento)
        super().save(*args, **kwargs)


def calcular_idade(data_nascimento):
    hoje = date.today()
    resto = hoje.month - data_nascimento.month
    idade = ((hoje.year - data_nascimento.year) * 12 + resto) / 12
    idade = floor(idade)
    return idade


@receiver(pre_save, sender=Cliente)
def pre_save_cliente(sender, instance, **kwargs):
    if instance.data_nascimento:
        instance.idade = calcular_idade(instance.data_nascimento)
    else:
        instance.idade = None





