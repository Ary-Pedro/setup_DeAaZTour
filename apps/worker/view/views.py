from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.mail import send_mail
import uuid
from django.urls import reverse_lazy
from .forms import RegisterForm
from apps.worker.models import Funcionario
from setup_DeAaZTour import settings
from apps.client.models import Cliente
from apps.service.models import Venda
from datetime import date, timedelta
from django.db.models.functions import datetime
from django.http import HttpResponse  
import csv  
import os 
from django.db.models import Q, Sum
from .forms import AtualizarForm

# INFO: Data
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta  # Usando relativedelta para manipulação de meses
from django.db.models import Count

User = get_user_model()


# IDEA: Dados Cadastrais ----------------------------------------------------------------------------------------------------
# INFO: Campo de login da conta

def log(request):
    url_redefinir_senha = (
        settings.BASE_URL + "/redefinirSenha/"
    )  # WARNING mudar lógica (em caso de deploy)

    if request.method == "POST":
        try:
            # Se o campo 'log' estiver presente, é uma tentativa de login
            if "log" in request.POST:
                log = request.POST.get("log")
                logpass = request.POST.get("logpass")
                user = authenticate(request, username=log, password=logpass)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect("home")
                    else:
                        error_message = "Funcionário inativo"
                        return render(
                            request, "register/login.html", {"error_message": error_message}
                        )
                else:
                    error_message = "Apelido ou senha incorretos. Tente novamente."
                    return render(
                        request, "register/login.html", {"error_message": error_message}
                    )

            # Se o campo 'email' estiver presente, é uma solicitação de recuperação de senha
            elif "email" in request.POST:
                email = request.POST.get("email")
                try:
                    user = Funcionario.objects.get(email=email)
                    user.token = str(uuid.uuid4())[:8]  # Apenas os 8 primeiros caracteres
                    user.save()  # Salva o token no banco de dados

                    send_mail(
                        subject="Relembrar senha",
                        message=f"Link de redefinição de senha: {url_redefinir_senha} \n\n Use o Token {user.token} para alterar seu acesso! \n\n Caso perca faça um novo pedido.",
                        from_email="projeto.abaprj@gmail.com",
                        recipient_list=[email],
                    )
                    return JsonResponse(
                        {
                            "message": "Um email com sua senha foi enviado para o endereço fornecido."
                        },
                        status=200,
                    )
                except Funcionario.DoesNotExist:
                    return JsonResponse({"message": "E-mail não encontrado."}, status=404)
                except Exception as e:
                    return JsonResponse(
                        {
                            "message": "Ocorreu um erro ao enviar o e-mail. Por favor, tente novamente."
                        },
                        status=500,
                    )
        except Exception as e:
            error_message = "Ocorreu um erro. Por favor, tente novamente."
            return render(
                request, "register/login.html", {"error_message": error_message}
            )

    return render(request, "register/login.html")


# INFO: Campo de registro da conta
class RegisterView(TemplateView):
    template_name = "register/registro.html"

    def get(self, request, **kwargs):
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Criar o usuário
            user = Funcionario.objects.create_user(
                username=form.cleaned_data["log"],
                password=form.cleaned_data["logpass"],
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telefone=form.cleaned_data["telefone"],
                cpf=form.cleaned_data["cpf"],
            )
            user.save()
            return redirect("log")
        else:
            # Mensagem de erro se o formulário for inválido
            return render(request, self.template_name, {"form": form})


# INFO: Redefinir senha da conta
def RedefinirSenha(request):
    if request.method == "POST":
        novolog = request.POST.get("log")
        novologpass = request.POST.get("logpass")
        novotoken = request.POST.get("token")

        # Verifica se todos os campos foram preenchidos
        if not all([novolog, novologpass, novotoken]):
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "register/redefinirSenha.html")

        try:
            # Tenta recuperar o usuário com o token fornecido
            user = Funcionario.objects.get(token=novotoken)

            if user.username == novolog:
                # Se o novo nome de usuário for igual ao atual, apenas redefine a senha
                user.set_password(novologpass)
            else:
                # Verifica se o novo nome de usuário já está em uso
                if Funcionario.objects.filter(username=novolog).exists():
                    messages.error(
                        request, "Esse nome de usuário já está em uso. Escolha outro."
                    )
                    return render(request, "register/redefinirSenha.html")

                # Redefine a senha e o nome de usuário
                user.set_password(novologpass)
                user.username = novolog

            user.token = None  # Remove o token após o uso
            user.save()

            messages.success(request, "Sua senha foi redefinida com sucesso.")
            return redirect("home")  # Redireciona para a página de login ou onde preferir

        except Funcionario.DoesNotExist:
            messages.error(
                request, "Token inválido. Verifique o token enviado para o seu e-mail."
            )
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {str(e)}")

    # Se não for uma requisição POST, ou se a requisição POST não passar pelas verificações
    return render(request, "register/redefinirSenha.html")



class Home(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    login_url = "log"  # URL para redirecionar para login
    model = User
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_logado = self.request.user

        # Checa se o usuário logado é um Funcionario e se está na situação "Adm."
        if isinstance(usuario_logado, Funcionario) and usuario_logado.departamento == "Adm":
           pass
            # Chama a função calcular_comissao para o administrador logado
            #usuario_logado.calcular_comissao()

        context["usuario_logado"] = usuario_logado
        return context

# INFO: Sair da conta
class LogoutView(LogoutView):
    next_page = "log"



# IDEIA: Dados Cadastrais - Alterar, Completar, Atualizar----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------



"""
Funcão
+ADM Editar + AlterarCargo() manual✅
+ADM Editar + Desligar() manual ✅
+Determinar Comissão() Automático **

Paginas 
+Cadastrar / login / refazer senha ✅
+Editar() UpdateView *
+Visualizar() DadosCadastrosFuncionario ✅
listar() ListFuncionario ✅
+Filtrar(nome,cpf...) ProcurarFuncionario *
+Editar atualizar cargo()✅
"""

# INFO: Funcionário - Listar
class ListFuncionario(LoginRequiredMixin, ListView):
    model = Funcionario
    paginate_by = 20
    login_url = "log"  # URL para redirecionar para login

# INFO: Funcionário - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Funcionario
    form_class = AtualizarForm
    template_name = "worker/Funcionario_form.html"
    success_url = reverse_lazy("ListagemFuncionario")


class Desligar(View):
    def get(self, request, pk):
        
        funcionario =  get_object_or_404(Funcionario, pk=pk)
        funcionario.AlterarAtividade()
        return redirect("ListagemFuncionario")
        
            
# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Funcionário
class Procurar(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Funcionario
    template_name = "buscasFuncionario/procurarFuncionario.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return Funcionario.objects.filter(
            Q(Q(first_name__istartswith=procurar_termo))
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = (f'Procurar por "{procurar_termo}" |',)
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context


# INFO: Dados - Funcionário
class Dados(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Funcionario
    template_name = "buscasFuncionario/dadosFuncionario.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Funcionario.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


### rever e corrigir!!!
def salvar_csvVenda(request, periodo, forma_pagamento=None):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=Vendas_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    cabecalho = [
        "ID",
        "Cliente",
        "Vendedor",
        "Data da Venda",
        "Valor",
        "Situação",
        "Data Finalizado",
        "Tipo de Servico",
        "Forma de pagamento",
    ]

    # Variáveis para controle de inclusão das colunas de cidadania e nacionalidade
    incluir_cidadania = False
    incluir_nacionalidade = False

    if periodo == "hoje":
        vendas = Venda.objects.filter(data_venda=date.today())
    elif periodo == "semana":
        inicio_semana = date.today() - timedelta(days=date.today().weekday())
        fim_semana = inicio_semana + timedelta(days=6)
        vendas = Venda.objects.filter(
            data_venda__gte=inicio_semana, data_venda__lte=fim_semana
        )
    elif periodo == "mes":
        inicio_mes = date.today().replace(day=1)
        proximo_mes = (inicio_mes + timedelta(days=31)).replace(day=1)
        vendas = Venda.objects.filter(
            data_venda__gte=inicio_mes, data_venda__lt=proximo_mes
        )
    else:
        vendas = Venda.objects.all()

    if forma_pagamento == "Pix":
        vendas = vendas.filter(tipo_pagamento="Pix")
    elif forma_pagamento == "Dinheiro":
        vendas = vendas.filter(tipo_pagamento="Dinheiro")
    elif forma_pagamento == "Crédito":
        vendas = vendas.filter(tipo_pagamento="Crédito")
    elif forma_pagamento == "Débito":
        vendas = vendas.filter(tipo_pagamento="Débito") 

    # Verificar se algum tipo de cidadania ou nacionalidade foi preenchido
    for venda in vendas:
        if venda.tipo_cidadania and venda.tipo_cidadania != "S/D":
            incluir_cidadania = True
        if venda.nacionalidade and venda.nacionalidade != "S/D":
            incluir_nacionalidade = True

    # Adiciona as colunas de cidadania e nacionalidade ao cabeçalho, se necessário
    if incluir_cidadania:
        cabecalho.append("Tipo de Cidadania")
    if incluir_nacionalidade:
        cabecalho.append("Nacionalidade")

    writer.writerow(cabecalho)

    # Escrever os dados das vendas
    for venda in vendas:
        if venda.tipo_servico == "Outros":
            tipo_servico = venda.tipo_servico_outros
        else:
            tipo_servico = venda.tipo_servico

        if venda.tipo_cidadania == "Outros":
            tipo_cidadania = (
                venda.tipo_cidadania_outros if venda.tipo_cidadania_outros else "S/D"
            )
        else:
            tipo_cidadania = venda.tipo_cidadania if venda.tipo_cidadania else "S/D"

        if venda.nacionalidade == "Outros":
            nacionalidade = (
                venda.nacionalidade_outros if venda.nacionalidade_outros else "S/D"
            )
        else:
            nacionalidade = venda.nacionalidade if venda.nacionalidade else "S/D"

        linha = [
            venda.id,
            venda.cliente.nome,
            (
                f"{venda.vendedor.first_name} {venda.vendedor.last_name}"
                if venda.vendedor
                else "S/D"
            ),
            venda.data_venda.strftime("%d/%m/%Y"),
            venda.valor,
            venda.situacaoMensal,
            venda.finished_at.strftime("%d/%m/%Y") if venda.finished_at else "S/D",
            tipo_servico,
            venda.tipo_pagamento,
        ]

        # Adiciona os valores de cidadania e nacionalidade, se forem incluídos no cabeçalho
        if incluir_cidadania:
            linha.append(tipo_cidadania)
        if incluir_nacionalidade:
            linha.append(nacionalidade)

        writer.writerow(linha)

    return response


def salvar_csvClientes(request, periodo):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=dadosClientes_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "Nome",
            "Celular",
            "Sexo",
            "Data de Nascimento",
            "Endereço",
            "Bairro",
            "Estado",
            "CEP",
            "RG",
            "CPF",
            "Número de Passaporte",
            "Idade",
            "Anexo 1",
            "Anexo 2",
            "Anexo 3",
        ]
    )  # Cabeçalho do CSV

    if periodo == "hoje":
        clientes = Cliente.objects.filter(created_at__date=date.today())
    elif periodo == "semana":
        inicio_semana = date.today() - timedelta(days=date.today().weekday())
        clientes = Cliente.objects.filter(created_at__date__gte=inicio_semana)
    elif periodo == "mes":
        inicio_mes = date.today().replace(day=1)
        clientes = Cliente.objects.filter(created_at__date__gte=inicio_mes)
    else:
        clientes = Cliente.objects.all()

    for cliente in clientes:
        anexo1_url = (
            request.build_absolute_uri(cliente.anexo1.url) if cliente.anexo1 else "S/D"
        )
        anexo2_url = (
            request.build_absolute_uri(cliente.anexo2.url) if cliente.anexo2 else "S/D"
        )
        anexo3_url = (
            request.build_absolute_uri(cliente.anexo3.url) if cliente.anexo3 else "S/D"
        )

        writer.writerow(
            [
                cliente.nome,
                cliente.celular,
                cliente.get_sexo_display(),  # Obtém o texto legível para a escolha do sexo
                cliente.data_nascimento.strftime("%d/%m/%Y"),
                cliente.endereco,
                cliente.bairro,
                cliente.estado,
                cliente.cep,
                cliente.rg,
                cliente.cpf,
                cliente.num_passaporte,
                cliente.idade() if cliente.idade() else "S/D",
                (
                    f'=HYPERLINK("{anexo1_url}", "{os.path.basename(cliente.anexo1.name)}")'
                    if anexo1_url != "S/D"
                    else "S/D"
                ),
                (
                    f'=HYPERLINK("{anexo2_url}", "{os.path.basename(cliente.anexo2.name)}")'
                    if anexo2_url != "S/D"
                    else "S/D"
                ),
                (
                    f'=HYPERLINK("{anexo3_url}", "{os.path.basename(cliente.anexo3.name)}")'
                    if anexo3_url != "S/D"
                    else "S/D"
                ),
            ]
        )
    return response


class Rank(LoginRequiredMixin, TemplateView):
    template_name = "ranking/rank.html"
    login_url = "log"  # URL para redirecionar para login

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_logado = self.request.user

        # Verificação de situação com base no tempo exato de um mês
        self.atualizar_situacao()

        # Carregar vendedores rankeados apenas com vendas mensais
        context["ranked_vendedores"] = Venda.objects.filter(
            Q(situacaoMensal="Mensal") | Q(situacaoMensal="Finalizada")).values(
            "vendedor__username",
            "vendedor__first_name",
            "vendedor__last_name",
            "vendedor__telefone",
            "vendedor__email",
        ).annotate(total_vendas=Count("id")).order_by("-total_vendas")

        # Contagem total de todas as vendas, incluindo as finalizadas
        context["total_vendas"] = Venda.objects.count()

        # Checa se o usuário logado é um Funcionario e se está na situação "Adm."
        if isinstance(usuario_logado, Funcionario) and usuario_logado.departamento == "Adm":
            # Chama a função calcular_comissao para o administrador logado
            usuario_logado.calcular_comissao()

        # Adiciona o usuário logado ao contexto
        context["usuario_logado"] = usuario_logado

        return context

    def atualizar_situacao(self):
        # Verificar se a última atualização foi há mais de 1 mês exato
        vendas = Venda.objects.filter(situacaoMensal="Mensal")
        for venda in vendas:
            # Comparar a data atual com a data de "situacaoMensal_dataApoio"
            if now() >= venda.situacaoMensal_dataApoio + relativedelta(months=1):
                venda.situacaoMensal = "Finalizada"
                venda.save()