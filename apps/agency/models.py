'''
from django.db import models


# INFO: Dados das agencias
class CadAgencia(models.Model):
    nome = models.CharField(
        max_length=100,
        null=False,
        verbose_name="Nome",
        help_text="Digite o nome aqui.",
    )

    email = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="E-mail",
        help_text="Digite seu e-mail aqui",
    )

    telefone1 = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Telefone 1",
        help_text="Digite seu Telefone aqui. como no exemplo: (21) 9xxxx-xxxx",
    )

    telefone2 = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Telefone 2",
        help_text="Digite seu Telefone aqui. como no exemplo: (21) 9xxxx-xxxx",
    )

    telefone3 = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Telefone 3",
        help_text="Digite seu Telefone aqui. como no exemplo: (21) 9xxxx-xxxx",
    )

    ano = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Ano",
        help_text="Digite o ano aqui",
    )

    cnpj = models.CharField(
        max_length=14,
        unique=True,
        null=False,
        verbose_name="CNPJ",
        help_text="Digite o CNPJ aqui modelo: XX. XXX. XXX/0001-XX",
    )
    bairro = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Bairro ",
        help_text="Digite a bairro aqui.",
        blank=True
    )
    cidade = models.CharField(
        max_length=100,
        null=True,
        verbose_name="Cidade ",
        help_text="Digite a cidade aqui.",
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

'''

