from django.db import models

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


