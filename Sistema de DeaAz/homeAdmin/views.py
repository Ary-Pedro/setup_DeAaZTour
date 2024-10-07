# INFO: Para uso do Auth e funções nativas de validação
import uuid

from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password

# INFO: funções uso geral
from django.db.models import Q
from django.db.models.functions import datetime

from homeAdmin.models import CadCliente, CustomUser_Funcionario, Venda
from django.core.mail import send_mail
import csv

# INFO: funções de endereçamento
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# INFO: funções de direcionar e configurar
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.views.generic import TemplateView

# INFO: Data
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta  # Usando relativedelta para manipulação de meses
from django.db.models import Count

User = get_user_model()

#Atualizar
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import CustomUser_Funcionario  # Certifique-se de usar o modelo correto

# INFO: Rank -----------------------------------------------------------------------------------------------------------
# INFO: Chamar e definir rank
class Rank(TemplateView):
    template_name = "ranking/rank.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_logado = self.request.user

        # Verificação de situação com base no tempo exato de um mês
        self.atualizar_situacao()

        # Carregar vendedores rankeados apenas com vendas mensais
        context["ranked_vendedores"] = Venda.objects.filter(situacaoMensal="Mensal").values(
            "vendedor__first_name",
            "vendedor__last_name",
            "vendedor__telefone",
            "vendedor__email",
        ).annotate(total_vendas=Count("id")).order_by("-total_vendas")

        # Contagem total de todas as vendas, incluindo as finalizadas
        context["total_vendas"] = Venda.objects.count()

        # Checa se o usuário logado é um CustomUser_Funcionario e se está na situação "Adm."
        if isinstance(usuario_logado, CustomUser_Funcionario) and usuario_logado.situacao_atual == "Adm.":
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


# INFO: Gerar CSV ------------------------------------------------------------------------------------------------------
# INFO: CSV referente a Venda
def salvar_csvVenda(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        "attachment; filename=Vendas_" + str(datetime.datetime.now()) + ".csv"
    )

    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Cliente",
            "Vendedor",
            "Data da Venda",
            "Valor",
            "Situação",
            "Data Finalizado",
            "Tipo de Venda",
            "Nacionalidade",
        ]
    )

    vendas = Venda.objects.all()  # Obtém todas as vendas

    for venda in vendas:
        if venda.nacionalidade == "outros":
            nacionalidade = venda.nacionalidade_outros
        else:
            nacionalidade = venda.nacionalidade

        writer.writerow(
            [
                venda.id,
                venda.cliente.nome,
                (
                    f"{venda.vendedor.first_name} {venda.vendedor.last_name}"
                    if venda.vendedor
                    else "S/D"
                ),
                venda.data_venda.strftime('%d/%m/%Y'),
                venda.valor,
                venda.situacaoMensal,
                venda.finished_at.strftime('%d/%m/%Y') if venda.finished_at else "S/D",
                venda.tipo_servico,
                nacionalidade,
            ]
        )
    return response


# INFO: CSV referente a Funcionário
def salvar_csvClientes(request):
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

    clientes = CadCliente.objects.all()  # Obtém todos os clientes

    for cliente in clientes:
        anexo1_url = request.build_absolute_uri(cliente.anexo1.url) if cliente.anexo1 else "S/D"
        anexo2_url = request.build_absolute_uri(cliente.anexo2.url) if cliente.anexo2 else "S/D"
        anexo3_url = request.build_absolute_uri(cliente.anexo3.url) if cliente.anexo3 else "S/D"

        writer.writerow(
            [
                cliente.nome,
                cliente.celular,
                cliente.get_sexo_display(),  # Obtém o texto legível para a escolha do sexo
                cliente.data_nascimento.strftime('%d/%m/%Y'),
                cliente.endereco,
                cliente.bairro,
                cliente.estado,
                cliente.cep,
                cliente.rg,
                cliente.cpf,
                cliente.num_passaporte,
                cliente.idade() if cliente.idade() else "S/D",
                f'=HYPERLINK("{anexo1_url}", "Link Anexo 1")' if anexo1_url != "S/D" else "S/D",
                f'=HYPERLINK("{anexo2_url}", "Link Anexo 2")' if anexo2_url != "S/D" else "S/D",
                f'=HYPERLINK("{anexo3_url}", "Link Anexo 3")' if anexo3_url != "S/D" else "S/D",
            ]
        )
    return response


# INFO: Conta ----------------------------------------------------------------------------------------------------
# INFO: Campo de login da conta
def log(request):
    url_redefinir_senha = settings.BASE_URL + "/redefinirSenha/"

    if request.method == "POST":
        # Se o campo 'log' estiver presente, é uma tentativa de login
        if "log" in request.POST:
            log = request.POST.get("log")
            logpass = request.POST.get("logpass")
            user = authenticate(request, username=log, password=logpass)
            if user is not None:
                if (
                    "Adm" in user.situacao_atual
                    and user.situacao_atual_empresa == "Ativo"
                ):
                    login(request, user)
                    return redirect("homeAdmin")

                elif (
                    "Func" in user.situacao_atual
                    and user.situacao_atual_empresa == "Ativo"
                ):
                    login(request, user)
                    return redirect("homeFuncionario")

                elif (
                    "Exec" in user.situacao_atual
                    and user.situacao_atual_empresa == "Ativo"
                ):
                    login(request, user)
                    return redirect("homeFuncionario")
                else:
                    error_message = "Funcionário inativo"
                    return render(
                        request, "registro/login.html", {"error_message": error_message}
                    )
            else:
                error_message = "Apelido ou senha incorretos. Tente novamente."
                return render(
                    request, "registro/login.html", {"error_message": error_message}
                )

        # Se o campo '' estiver presente, é uma solicitação de recuperação de senha
        elif "email" in request.POST:
            email = request.POST.get("email")
            try:
                user = CustomUser_Funcionario.objects.get(email=email)
                user.token = str(uuid.uuid4())[:8]  # Apenas os 8 primeiros caracteres
                user.save()  # Salva o token no banco de dados

                send_mail(
                    subject="Relembrar senha",
                    message=f"Link de redefinição de senha: {url_redefinir_senha} \n\n Use o Token: {user.token} para alterar seu acesso! \n\n caso perca faça um novo pedido ",
                    from_email="projeto.abaprj@gmail.com",
                    recipient_list=[email],
                )
                return JsonResponse(
                    {
                        "message": "Um email com sua senha foi enviado para o endereço fornecido."
                    },
                    status=200,
                )
            except CustomUser_Funcionario.DoesNotExist:
                return JsonResponse({"message": "E-mail não encontrado."}, status=404)
            except Exception as e:
                return JsonResponse(
                    {
                        "message": "Ocorreu um erro ao enviar o e-mail. Por favor, tente novamente."
                    },
                    status=500,
                )

    return render(request, "registro/login.html")

# INFO: Campo de registro da conta
class RegisterView(TemplateView):
    template_name = "registro/registro.html"

    def get(self, request, **kwargs):
        return render(request, self.template_name)

    def post(self, request):
        log = request.POST.get("log")
        logpass = request.POST.get("logpass")
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        cidade = request.POST.get("cidade")
        telefone = request.POST.get("telefone")

        if (
            User.objects.filter(email=email).exists()
            or User.objects.filter(username=log).exists()
        ):
            return render(
                request,
                self.template_name,
                {"error_message": "E-mail ou apelido já foram registrados"},
            )

        user = CustomUser_Funcionario.objects.create_user(
            username=log,
            email=email,
            password=logpass,
            first_name=first_name,
            last_name=last_name,
            cidade=cidade,
            telefone=telefone,
        )
        user.save()
        return redirect("log")

# INFO: Redefinir senha da conta
def RedefinirSenha(request):
    print("oii")

    if request.method == "POST":
        novolog = request.POST.get("log")
        novologpass = request.POST.get("logpass")
        novotoken = request.POST.get("token")

        # Verifica se todos os campos foram preenchidos
        if not all([novolog, novologpass, novotoken]):

            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, "email/email.html")

        try:
            # Tenta recuperar o usuário com o token fornecido
            user = CustomUser_Funcionario.objects.get(token=novotoken)

            # Verifica se o novo nome de usuário já está em uso
            if CustomUser_Funcionario.objects.filter(username=novolog).exists():
                messages.error(request, "Esse nome de usuário já está em uso. Escolha outro.")
                return render(request, "email/email.html")

            # Redefine a senha e o nome de usuário
            user.set_password(novologpass)  # Usa set_password para criptografar a senha corretamente
            user.username = novolog
            user.token = None  # Remove o token após o uso
            user.save()

            messages.success(request, "Sua senha foi redefinida com sucesso.")
            return redirect("homeAdmin")  # Redireciona para a página de login ou onde preferir

        except CustomUser_Funcionario.DoesNotExist:
            messages.error(request, "Token inválido. Verifique o token enviado para o seu e-mail.")
        except Exception as e:
            messages.error(request, f"Ocorreu um erro: {str(e)}")

    # Se não for uma requisição POST, ou se a requisição POST não passar pelas verificações
    return render(request, "email/email.html")


# INFO: Sair da conta
class LogoutView(LogoutView):
    next_page = "log"



# INFO: Admin ----------------------------------------------------------------------------------------------------------
# INFO: Admin - Home
class AdminHome(LoginRequiredMixin, TemplateView):
    template_name = "homeAdmin/homeAdmin.html"
    login_url = "log"  # URL para redirecionar para login
    model = User


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_logado = self.request.user

        # Checa se o usuário logado é um CustomUser_Funcionario e se está na situação "Adm."
        if isinstance(usuario_logado, CustomUser_Funcionario) and usuario_logado.situacao_atual == "Adm.":
            # Chama a função calcular_comissao para o administrador logado
            usuario_logado.calcular_comissao()

        context["usuario_logado"] = usuario_logado
        return context




# INFO: Cliente --------------------------------------------------------------------------------------------------------
# INFO: Cliente - Cadastrar
class cadCliente(LoginRequiredMixin, CreateView):
    model = CadCliente
    fields = [
        "nome",
        "celular",
        "cpf",
        "rg",
        "sexo",
        "data_nascimento",
        "num_passaporte",
        "endereco",
        "bairro",
        "estado",
        "cep",
        'anexo1',
        'anexo2',
        'anexo3',
    ]
    template_name = "cadAdmin/formsCliente/cadastroCliente_form.html"
    success_url = reverse_lazy("homeAdmin")
    login_url = "log"  # URL para redirecionar para login





    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f"Cliente de id {self.object.id} cadastrado com sucesso!"
        )
        return response




# INFO: Cliente - listar
class CadListView(ListView):
    model = CadCliente
    paginate_by = 20
    template_name = "cadAdmin/formsCliente/cadastroCliente_list.html"
    context_object_name = "cadastro_list"

# INFO: Cliente - Validar
class ValidarCliente(View):
    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(CadCliente, pk=pk)
        finalizar.mark_has_complete()

        numero_pagina = request.GET.get("page", 1)

        url = reverse("AdminListagemCliente")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")

# INFO: Cliente - Atualizar
class ClienteUpdateView(UpdateView):
    model = CadCliente
    fields = [
        "nome",
        "celular",
        "cpf",
        "rg",
        "sexo",
        "data_nascimento",
        "num_passaporte",
        "endereco",
        "bairro",
        "estado",
        "cep",
        'anexo1',
        'anexo2',
        'anexo3',
    ]
    template_name = "cadAdmin/formsCliente/cadastroCliente_form.html"
    success_url = reverse_lazy("AdminListagemCliente")

# INFO: Cliente - Deletar
class ClienteDeleteView(DeleteView):
    model = CadCliente
    template_name = "cadAdmin/formsCliente/cadastroCliente_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('AdminListagemCliente')}?page={numero_pagina}"

# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Cliente
class ProcurarCliente(ListView):
    model = CadCliente
    template_name = "cadAdmin/buscasCliente/procurarCliente.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return CadCliente.objects.filter(
            Q(
                Q(nome__istartswith=procurar_termo) | Q(cpf__icontains=procurar_termo),
            )
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = (f'Procurar por "{procurar_termo}" |',)
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context

# INFO: Dados - Cliente
class DadosCadastrosCliente(ListView):
    model = CadCliente
    template_name = "cadAdmin/buscasCliente/dadosCliente.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return CadCliente.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


# INFO: Funcionário ----------------------------------------------------------------------------------------------------

# INFO: Funcionário - cadastrar
class cadFuncionario(CreateView):
    model = CustomUser_Funcionario
    fields = [
        "first_name",
        "last_name",
        "username",
        "email",
        "telefone",
        "cargo_atual",
        "salario",
        "situacao_atual",
        "situacao_atual_empresa",
    ]
    template_name = "cadAdmin/formsFuncionario/cadastroFuncionario_form.html"
    success_url = reverse_lazy("homeAdmin")

# INFO: Funcionário - Listar
class CadListViewFunc(ListView):
    model = CustomUser_Funcionario
    paginate_by = 20
    template_name = "cadAdmin/formsFuncionario/cadastroFuncionario_list.html"
    context_object_name = "cadastro_list"

# INFO: Funcionário - Atualizar
class FuncionarioUpdateView(UpdateView):
    model = CustomUser_Funcionario
    fields = [
        "first_name", "last_name", "username", "email",
        "telefone", "cargo_atual", "salario",
        "situacao_atual", "situacao_atual_empresa"
    ]
    template_name = "cadAdmin/formsFuncionario/cadastroFuncionario_form.html"
    success_url = reverse_lazy("AdminListagemFuncionario")



# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Funcionário
class ProcurarFuncionario(ListView):
    model = CustomUser_Funcionario
    template_name = "cadAdmin/buscasFuncionario/procurarFuncionario.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return CustomUser_Funcionario.objects.filter(
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
class DadosCadastrosFuncionario(ListView):
    model = CustomUser_Funcionario
    template_name = "cadAdmin/buscasFuncionario/dadosFuncionario.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return CustomUser_Funcionario.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


# INFO: Venda  --------------------------------------------------------------------------------------------------------

# INFO: Venda - Cadastar
class cadVendas(CreateView):
    model = Venda
    fields = ["vendedor", "valor", "situacaoMensal"]
    template_name = "cadAdmin/Vendas/formsVenda/cadastroVendas_form.html"
    success_url = reverse_lazy("homeAdmin")

    def get_initial(self):
        initial = super().get_initial()
        initial["vendedor"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clientes"] = CadCliente.objects.all()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Desabilita os campos 'vendedor' e 'situacao'
        form.fields["vendedor"].widget.attrs["disabled"] = True
        form.fields["situacaoMensal"].widget.attrs["disabled"] = True
        return form

    def form_valid(self, form):
        cliente_input = self.request.POST.get("cliente")
        cpf_input = self.request.POST.get("cpf_cliente")
        id_input = self.request.POST.get("pk_cliente")

        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadCliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                form.instance.vendedor = self.request.user

                form.instance.tipo_servico = self.request.POST.get("tipo_servico")
                form.instance.nacionalidade = self.request.POST.get("nacionalidade")
                if form.instance.nacionalidade == "outros":
                    form.instance.nacionalidade_outros = self.request.POST.get("nacionalidade_outros")
                else:
                    form.instance.nacionalidade_outros = None

                response = super().form_valid(form)
                messages.success(self.request,
                                 f'Venda registrada com sucesso! Cliente de ID {self.object.id} cadastrado com sucesso.')
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do cliente inválidos.')
                return self.form_invalid(form)
        else:
                messages.error(self.request, 'Informe o nome do cliente.')
                return self.form_invalid(form)

# INFO: Venda - Listar
class CadListViewVenda(ListView):
    model = Venda
    paginate_by = 20
    template_name = "cadAdmin/Vendas/formsVenda/cadastroVenda_list.html"
    context_object_name = "cadastro_list"

# INFO: Venda - Atualizar
class VendaUpdateView(UpdateView):
    model = Venda
    fields = ["vendedor", "valor", "situacaoMensal"]
    template_name = "cadAdmin/Vendas/formsVenda/cadastroVendas_form.html"
    success_url = reverse_lazy("AdminListagemVenda")

    def get_initial(self):
        initial = super().get_initial()
        venda = self.get_object()


        initial["valor"] = venda.valor
        initial["situacaoMensal"] = venda.situacaoMensal
        initial["tipo_servico"] = venda.tipo_servico
        initial["nacionalidade"] = venda.nacionalidade
        if venda.nacionalidade == "outros":
            initial["nacionalidade_outros"] = venda.nacionalidade_outros
        if venda.cliente:
            initial["cliente"] = venda.cliente.nome
            initial["cpf_cliente"] = venda.cliente.cpf
            initial["pk_cliente"] = venda.cliente.pk
            initial["passaporte_cliente"] = venda.cliente.num_passaporte
            initial["data_nascimento_cliente"] = venda.cliente.data_nascimento
            initial["endereco_cliente"] = venda.cliente.endereco
            initial["cep_cliente"] = venda.cliente.cep
            initial["bairro_cliente"] = venda.cliente.bairro
            initial["estado_cliente"] = venda.cliente.estado
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clientes"] = CadCliente.objects.all()
        context.update(self.get_initial())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Desabilita os campos 'vendedor' e 'situacaoMensal'
        form.fields["vendedor"].widget.attrs["disabled"] = True
        return form

    def form_valid(self, form):
        cliente_input = self.request.POST.get("cliente")
        cpf_input = self.request.POST.get("cpf_cliente")
        id_input = self.request.POST.get("pk_cliente")


        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadCliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (
                    not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                form.instance.vendedor = self.request.user

                form.instance.tipo_servico = self.request.POST.get("tipo_servico")
                form.instance.nacionalidade = self.request.POST.get("nacionalidade")
                if form.instance.nacionalidade == "outros":
                    form.instance.nacionalidade_outros = self.request.POST.get("nacionalidade_outros")
                else:
                    form.instance.nacionalidade_outros = None

                response = super().form_valid(form)
                messages.success(self.request,
                                 f'Venda registrada com sucesso! Cliente de ID {self.object.id} cadastrado com sucesso.')
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do cliente inválidos.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Informe o nome do cliente.')
            return self.form_invalid(form)

# INFO: Venda - Deletar
class VendaDeleteView(DeleteView):
    model = Venda
    template_name = "cadAdmin/Vendas/formsVenda/cadastroVenda_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('AdminListagemVenda')}?page={numero_pagina}"


# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Venda
class ProcurarVenda(ListView):
    model = Venda
    template_name = "cadAdmin/Vendas/buncasVendas/procurarVenda.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return Venda.objects.filter(
            Q(cliente__nome__istartswith=procurar_termo)
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = (f'Procurar por "{procurar_termo}" |',)
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context

# INFO: Dados - Venda
class DadosCadastrosVenda(ListView):
    model = Venda
    template_name = "cadAdmin/Vendas/buncasVendas/dadosVenda.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Venda.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context

# INFO: Venda - Validar
class ValidarVendas(View):
    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(Venda, pk=pk)
        finalizar.mark_as_complete()

        numero_pagina = request.GET.get("page", 1)

        url = reverse("AdminListagemVenda")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")

# NOTE: função para puxar informaçoes de clientes em nova venda pelo id
def cliente_detail_api(request, pk):
    cliente = get_object_or_404(CadCliente, pk=pk)
    data = {
        "nome": cliente.nome,
        "cpf": cliente.cpf,
        "rg": cliente.rg,
        "num_passaporte": cliente.num_passaporte,
        "data_nascimento": cliente.data_nascimento,
        "endereco": cliente.endereco,
        "cep": cliente.cep,
        "bairro": cliente.bairro,
        "estado": cliente.estado,
    }
    return JsonResponse(data)
