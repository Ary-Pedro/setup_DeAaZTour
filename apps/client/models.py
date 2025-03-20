from django.db import models
from datetime import date, datetime
from django.core.exceptions import ValidationError
from math import floor
from django.dispatch import receiver
from django.db.models.signals import pre_save

# INFO: Dados de clientes
class Cliente(models.Model):
    nome = models.CharField(
        max_length=101,
        verbose_name="nome",
        null=True,
        blank=True,
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
        blank=True, 
        verbose_name="telefone 3",
    )
    email1 = models.EmailField(null=True, blank=True, verbose_name="e-mail 1", max_length=255)
    email2 = models.EmailField(null=True, blank=True, verbose_name="e-mail 2", max_length=255)
    

    sexo = models.CharField(
        max_length=50,
        choices=[
            ("M", "Masculino"), ("F", "Feminino"),("O", "Outro")
        ],
        blank=True,
        null=True,
    )

    sexo_outros = models.CharField(
        max_length=5000,
        blank=True,
        null=True,
        verbose_name="Tipo sexo",
        help_text="Digite o sexo aqui.",
    )


    data_nascimento = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Data de nascimento",
        help_text="Digite no formato dd/mm/aaaa")
    
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


    rg = models.CharField(max_length=20, verbose_name="RG",  null=True, blank=True)

    cpf = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        verbose_name="CPF",
    )

    num_passaporte = models.CharField(
        max_length=20, verbose_name="número de passaporte", null=True, blank=True
    )

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
    


    def __str__(self):
        return self.nome
    
     
    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.upper()
        if self.data_nascimento:
            self.idade = calcular_idade(self.data_nascimento)
        super().save(*args, **kwargs)


def calcular_idade(data_nascimento_str):
    # Converte a string para um objeto date
    data_nascimento_dt = datetime.strptime(data_nascimento_str, "%d/%m/%Y").date()
    hoje = date.today()
    # Calcula a idade considerando se o aniversário já ocorreu neste ano ou não
    idade = hoje.year - data_nascimento_dt.year - ((hoje.month, hoje.day) < (data_nascimento_dt.month, data_nascimento_dt.day))
    return idade


@receiver(pre_save, sender=Cliente)
def pre_save_cliente(sender, instance, **kwargs):
    if instance.data_nascimento:
        instance.idade = calcular_idade(instance.data_nascimento)
    else:
        instance.idade = None


class Anexo(models.Model):
    arquivo = models.FileField(upload_to='anexos/')
    cliente = models.ForeignKey('Cliente', related_name='anexos', on_delete=models.CASCADE)
    data_upload = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.arquivo.name


