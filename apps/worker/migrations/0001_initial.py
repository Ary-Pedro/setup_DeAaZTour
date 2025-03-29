# Generated by Django 5.1.5 on 2025-03-29 02:43

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="FluxoMensal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mes_referencia",
                    models.DateField(
                        default=django.utils.timezone.now,
                        verbose_name="Mês de Referência",
                    ),
                ),
                ("saldo_total", models.FloatField(verbose_name="Saldo Total")),
                ("total_entrada", models.FloatField(verbose_name="Total de Entradas")),
                ("total_saida", models.FloatField(verbose_name="Total de Saídas")),
            ],
        ),
        migrations.CreateModel(
            name="Funcionario",
            fields=[
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "first_name",
                    models.CharField(max_length=50, verbose_name="primeiro nome"),
                ),
                (
                    "last_name",
                    models.CharField(max_length=50, verbose_name="último nome"),
                ),
                ("nome", models.CharField(editable=False, max_length=101, null=True)),
                ("idade", models.IntegerField(editable=False, null=True)),
                (
                    "username",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="apelido"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=255, unique=True, verbose_name="e-mail"
                    ),
                ),
                (
                    "Sub_salario_fixo",
                    models.FloatField(
                        blank=True,
                        default=0,
                        help_text="Um valor fixo pago ao funcionario",
                        null=True,
                        verbose_name="salário fixo",
                    ),
                ),
                (
                    "salario",
                    models.FloatField(
                        default=0, editable=False, verbose_name="salário total"
                    ),
                ),
                (
                    "comissao_acumulada",
                    models.FloatField(default=0, verbose_name="comissão acumulada"),
                ),
                (
                    "telefone",
                    models.CharField(
                        blank=True,
                        help_text="Apenas digite os números; este campo possui autoformatação",
                        max_length=20,
                        null=True,
                    ),
                ),
                (
                    "endereco",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Endereço"
                    ),
                ),
                ("cidade", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "complemento",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "data_nascimento",
                    models.DateField(
                        blank=True,
                        help_text="Apenas digite os números; este campo possui autoformatação",
                        null=True,
                        verbose_name="Data de nascimento",
                    ),
                ),
                ("token", models.CharField(max_length=8, null=True, unique=True)),
                ("is_staff", models.BooleanField(default=True)),
                (
                    "cpf",
                    models.CharField(
                        blank=True,
                        help_text="Apenas digite os números; este campo possui autoformatação",
                        max_length=14,
                        null=True,
                        unique=True,
                        verbose_name="CPF",
                    ),
                ),
                (
                    "pix",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Pix"
                    ),
                ),
                (
                    "departamento",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Adm", "Administrativo"),
                            ("Vend", "Vendedor"),
                            ("Exec", "Executivo"),
                        ],
                        default="Adm",
                        max_length=15,
                        null=True,
                    ),
                ),
                (
                    "atividade",
                    models.CharField(
                        blank=True,
                        choices=[("Ativo", "Ativo "), ("Inativo", "Inativo")],
                        default="Ativo",
                        help_text="Defini se o funcionario tá ativo na empresa, ou foi desligado.",
                        max_length=15,
                        null=True,
                    ),
                ),
                (
                    "especializacao_funcao",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Financeiro", "Financeiro"),
                            ("Despachante", "Despachante "),
                            ("Despachante externo", "Despachante externo "),
                            ("Suporte Whatsapp", "Suporte Whatsapp"),
                            ("Executivo contas", "Executivo contas"),
                            ("Diretor(a)", "Diretor(a)"),
                        ],
                        default="Financeiro",
                        help_text="A função a qual o empregado exerce.",
                        max_length=100,
                        null=True,
                        verbose_name="especialização, área de atuação",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to.",
                        related_name="customuser_set",
                        related_query_name="customuser",
                        to="auth.group",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="customuser_set",
                        related_query_name="customuser",
                        to="auth.permission",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="ContasMensal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "observacao",
                    models.CharField(
                        blank=True, max_length=500, null=True, verbose_name="Descrição"
                    ),
                ),
                ("entrada", models.FloatField(blank=True, default=0, null=True)),
                ("saida", models.FloatField(blank=True, default=0, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "fluxo_mensal",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="contas",
                        to="worker.fluxomensal",
                    ),
                ),
            ],
        ),
    ]
