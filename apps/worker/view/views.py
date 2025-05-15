from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.views.generic import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core.mail import send_mail
import uuid
from django.urls import reverse, reverse_lazy
from .forms import RegisterForm
from apps.worker.models import Funcionario, ContasMensal, FluxoMensal
from setup_DeAaZTour import settings
from apps.client.models import Cliente
from apps.service.models import OPC_SERVICES, Venda
from datetime import date, timedelta
from django.db.models.functions import datetime
from django.http import HttpResponse
import csv
import os
from django.db.models import Q, Sum
from .forms import AtualizarForm, CompletarCadastro
from io import BytesIO

# INFO: Data
from django.utils.timezone import now
from dateutil.relativedelta import (
    relativedelta,
)  # Usando relativedelta para manipulação de meses
from django.db.models import Count
from .forms import ContasForm
from django.utils import timezone

User = get_user_model()


def vendasDoFunc(request, pk):
    funcionario = Funcionario.objects.get(pk=pk)
    vendas = Venda.objects.filter(vendedor=funcionario)
    vendas = Venda.objects.filter(executivo=funcionario)
    vendas = Venda.objects.filter(Q(vendedor=funcionario) | Q(executivo=funcionario))

    fluxo_mensal = FluxoMensal.objects.first()
    if fluxo_mensal:
        mes_referencia = fluxo_mensal.mes_referencia
    else:
        mes_referencia = None

    if mes_referencia:
        vendas = vendas.filter(
            situacaoMensal_dataApoio__month=mes_referencia.month,
            situacaoMensal_dataApoio__year=mes_referencia.year,
        )
    return render(
        request,
        "contas/detalhes_fluxo_completo.html",
        {
            "funcionario": funcionario,
            "vendas": vendas,
            "mes_referencia": mes_referencia,
        },
    )


def salvar_csvFluxoConcluido(request, fluxo_id):
    fluxo = get_object_or_404(FluxoMensal, id=fluxo_id)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f"attachment; filename=fluxo_concluido_{fluxo.mes_referencia.strftime('%Y%m')}.csv"
    )

    response.write("\ufeff")

    writer = csv.writer(response)

    writer.writerow(["Data", "Observação", "Entrada (R$)", "Saída (R$)"])

    contas = fluxo.contas.all()
    total_entrada = 0.0
    total_saida = 0.0

    for conta in contas:
        writer.writerow(
            [
                (
                    conta.created_at.strftime("%d/%m/%Y")
                    if conta.created_at
                    else "Sem Data"
                ),
                conta.observacao if conta.observacao else "Sem observação",
                f"{conta.entrada:.2f}".replace(".", ","),
                f"{conta.saida:.2f}".replace(".", ","),
            ]
        )
        total_entrada += conta.entrada
        total_saida += conta.saida

    saldo_total = total_entrada - total_saida

    writer.writerow([])
    writer.writerow(["Total Entrada", f"{total_entrada:.2f}".replace(".", ",")])
    writer.writerow(["Total Saída", f"{total_saida:.2f}".replace(".", ",")])
    writer.writerow(["Saldo Final", f"{saldo_total:.2f}".replace(".", ",")])

    return response


class contas(LoginRequiredMixin, CreateView):
    model = ContasMensal
    form_class = ContasForm
    template_name = "contas/contas.html"
    success_url = reverse_lazy("contas")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contas"] = ContasMensal.objects.filter(fluxo_mensal__isnull=True)
        context["saldo_total"] = ContasMensal.calcular_saldo()
        return context


def resetar_contas(request):
    ContasMensal.objects.filter(fluxo_mensal__isnull=True).delete()
    return redirect("contas")


def concluir_fluxo_mensal(request):
    # Define o mês de referência como o primeiro dia do mês atual
    current_date = timezone.now().date()
    mes_referencia = date(current_date.year, current_date.month, 1)

    # Obtém ou cria o FluxoMensal para o mês atual
    fluxo, created = FluxoMensal.objects.get_or_create(
        mes_referencia=mes_referencia,
        defaults={
            "saldo_total": 0,
            "total_entrada": 0,
            "total_saida": 0,
        },
    )

    # Atualiza os registros não vinculados e recalcula totais
    registros_fluxo_atual = ContasMensal.objects.filter(fluxo_mensal__isnull=True)
    registros_fluxo_atual.update(fluxo_mensal=fluxo)

    # Recalcula totais baseado em todas as contas vinculadas
    contas_do_fluxo = ContasMensal.objects.filter(fluxo_mensal=fluxo)
    total_entrada = contas_do_fluxo.aggregate(Sum("entrada"))["entrada__sum"] or 0
    total_saida = contas_do_fluxo.aggregate(Sum("saida"))["saida__sum"] or 0

    fluxo.total_entrada = total_entrada
    fluxo.total_saida = total_saida
    fluxo.saldo_total = total_entrada - total_saida
    fluxo.save()

    return redirect("listagemFluxoMensal")


def deletar_conta_mensal(request, pk):
    conta = get_object_or_404(ContasMensal, pk=pk)
    fluxo = conta.fluxo_mensal
    fluxo_id = fluxo.id

    conta.delete()

    contas_do_fluxo = ContasMensal.objects.filter(fluxo_mensal=fluxo)

    fluxo.total_entrada = contas_do_fluxo.aggregate(Sum("entrada"))["entrada__sum"] or 0
    fluxo.total_saida = contas_do_fluxo.aggregate(Sum("saida"))["saida__sum"] or 0
    fluxo.saldo_total = fluxo.total_entrada - fluxo.total_saida
    fluxo.save()

    return redirect("fluxo_completo", pk=fluxo_id)


class FluxoUpdateView(LoginRequiredMixin, UpdateView):
    model = ContasMensal
    form_class = ContasForm
    template_name = "contas/detalhes_fluxo_form.html"
    login_url = "log"

    def form_valid(self, form):
        # instância antes de alterar
        conta_antiga = self.get_object()
        fluxo_antigo = conta_antiga.fluxo_mensal

        # salva sem commit para podermos ajustar fluxo_mensal
        conta = form.save(commit=False)

        # determina o mês de referência a partir de created_at editado
        mes = conta.created_at
        mes_referencia = date(mes.year, mes.month, 1)

        # obtém ou cria o fluxo para esse mês
        fluxo_novo, _ = FluxoMensal.objects.get_or_create(
            mes_referencia=mes_referencia,
            defaults={
                "saldo_total": 0,
                "total_entrada": 0,
                "total_saida": 0,
            },
        )

        # reatribui e salva a conta
        conta.fluxo_mensal = fluxo_novo
        conta.save()

        # função auxiliar para recálculo de um fluxo
        def recalcular(fluxo):
            contas = ContasMensal.objects.filter(fluxo_mensal=fluxo)
            entrada = contas.aggregate(Sum("entrada"))["entrada__sum"] or 0
            saida = contas.aggregate(Sum("saida"))["saida__sum"] or 0
            fluxo.total_entrada = entrada
            fluxo.total_saida = saida
            fluxo.saldo_total = entrada - saida
            fluxo.save()

        # recalcula tanto o fluxo antigo (se existir) quanto o novo
        if fluxo_antigo:
            recalcular(fluxo_antigo)
        recalcular(fluxo_novo)

        # redireciona para o fluxo_completo do fluxo novo
        return HttpResponseRedirect(
            reverse("fluxo_completo", kwargs={"pk": fluxo_novo.pk})
        )


class ListarFluxosMensais(LoginRequiredMixin, ListView):
    model = FluxoMensal
    template_name = "contas/listagemFluxo.html"
    paginate_by = 12
    context_object_name = "fluxos"
    ordering = ["-mes_referencia"]  # <-- ordem decrescente


class DetalhesFluxoMensalCompleto(LoginRequiredMixin, DetailView):
    model = FluxoMensal
    template_name = "contas/detalhes_fluxo_completo.html"
    context_object_name = "fluxo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fluxo = self.object

        # Filtrar vendas do mês
        mes_ref = fluxo.mes_referencia
        month_year_str = f"/{mes_ref.month:02d}/{mes_ref.year}"
        vendas_mes = Venda.objects.filter(data_venda__endswith=month_year_str)

        # Processar dados dos funcionários
        funcionarios_data = []
        total_vendas_brutas = 0
        total_comissoes = 0

        # Salários fixos de funcionários ativos
        total_salarios_fixos = (
            Funcionario.objects.filter(is_active=True).aggregate(
                total=Sum("Sub_salario_fixo")
            )["total"]
            or 0
        )

        for funcionario in Funcionario.objects.all():
            # Ignorar comissão de ADMs
            if funcionario.departamento == "Adm":
                comissao = 0
            else:
                comissao = funcionario.comissao_acumulada or 0
                total_comissoes += comissao

            vendas_vendedor = vendas_mes.filter(vendedor=funcionario).exclude(
                tipo_servico__in=OPC_SERVICES
            )
            vendas_executivo = vendas_mes.filter(
                executivo=funcionario, tipo_servico__in=OPC_SERVICES
            )
            vendas_funcionario = list(vendas_vendedor) + list(vendas_executivo)
            total_funcionario = sum(v.valor for v in vendas_funcionario if v.valor)

            funcionarios_data.append(
                {
                    "funcionario": funcionario,
                    "vendas": vendas_funcionario,
                    "total_vendas": total_funcionario,
                    "comissao": comissao,
                }
            )
            total_vendas_brutas += total_funcionario

        # Cálculos financeiros
        subliquido = (fluxo.total_entrada + total_vendas_brutas) - (
            fluxo.total_saida + total_comissoes
        )
        liquido_real = subliquido - total_salarios_fixos

        # Salvar valores no modelo
        fluxo.subtotal_liquido = subliquido
        fluxo.total_liquido = liquido_real
        fluxo.save()

        context.update(
            {
                "contas": fluxo.contas.all(),
                "funcionarios_data": funcionarios_data,
                "total_vendas_brutas": total_vendas_brutas,
                "total_comissoes": total_comissoes,
                "total_salarios_fixos": total_salarios_fixos,
                "subliquido": subliquido,
                "liquido_real": liquido_real,
                "OPC_SERVICES": OPC_SERVICES,
            }
        )
        return context


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
                            request,
                            "register/login.html",
                            {"error_message": error_message},
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
                    user.token = str(uuid.uuid4())[
                        :8
                    ]  # Apenas os 8 primeiros caracteres
                    user.save()  # Salva o token no banco de dados

                    send_mail(
                        subject="Relembrar senha",
                        message=f"Link de redefinição de senha: {url_redefinir_senha} \n\n Use o Token {user.token} para alterar seu acesso! \n\n Caso perca faça um novo pedido.",
                        from_email="recuperarsenhadeaaztur@gmail.com",
                        recipient_list=[email],
                    )
                    return JsonResponse(
                        {
                            "message": "Um email com sua senha foi enviado para o endereço fornecido."
                        },
                        status=200,
                    )
                except Funcionario.DoesNotExist:
                    return JsonResponse(
                        {"message": "E-mail não encontrado."}, status=404
                    )
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
            # Verificar se o CPF foi fornecido
            cpf = form.cleaned_data["cpf"]
            if not cpf:
                cpf = None

            # Criar o usuário
            user = Funcionario.objects.create_user(
                username=form.cleaned_data["log"],
                password=form.cleaned_data["logpass"],
                email=form.cleaned_data["email"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                telefone=form.cleaned_data["telefone"],
                cpf=cpf,
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
            return redirect(
                "home"
            )  # Redireciona para a página de login ou onde preferir

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

        context["usuario_logado"] = usuario_logado
        return context


# INFO: Sair da conta
class LogoutView(LogoutView):
    next_page = "log"


# IDEIA: Dados Cadastrais - Alterar, Completar, Atualizar----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------# INFO: Funcionário - Listar
class ListFuncionario(LoginRequiredMixin, ListView):
    model = Funcionario
    paginate_by = 20
    login_url = "log"  # URL para redirecionar para login

    def get_queryset(self):
        queryset = super().get_queryset()
        for funcionario in queryset:
            if funcionario.departamento == "Vend":
                # Atualiza a comissão do vendedor
                funcionario.comissao_acumulada = Venda.calcular_comissao_vendedor(
                    funcionario
                )

            if funcionario.departamento == "Exec":
                # Atualiza a comissão do executivo
                funcionario.comissao_acumulada = Venda.calcular_comissao_executivo(
                    funcionario
                )
            if (
                funcionario.departamento == "Adm"
                and funcionario.especializacao_funcao == "Financeiro"
            ):
                funcionario.comissao_acumulada = (
                    Funcionario.calcular_comissao_administrador(funcionario)
                )
            funcionario.save()
        return queryset


# INFO: Funcionário - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Funcionario
    form_class = AtualizarForm
    template_name = "worker/Funcionario_form.html"
    success_url = reverse_lazy("ListagemFuncionario")


class AtualizarPerfil(UpdateView, LoginRequiredMixin):
    login_url = "log"  # URL para redirecionar para login
    model = Funcionario
    form_class = CompletarCadastro
    template_name = "worker/Atualizar.html"
    success_url = reverse_lazy("home")

    def get_object(self, queryset=None):
        return self.request.user


class Desligar(View):
    def get(self, request, pk):

        funcionario = get_object_or_404(Funcionario, pk=pk)
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


class Rank(LoginRequiredMixin, TemplateView):
    template_name = "ranking/rank.html"
    login_url = "log"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario_logado = self.request.user

        self.atualizar_situacao()

        context["ranked_vendedores"] = (
            Venda.objects.filter(Q(situacaoMensal="Mensal"))
            .values(
                "vendedor__username",
                "vendedor__first_name",
                "vendedor__last_name",
                "vendedor__telefone",
                "vendedor__email",
            )
            .annotate(total_vendas=Count("id"))
            .order_by("-total_vendas")
        )

        context["total_vendas"] = Venda.objects.count()
        context["usuario_logado"] = usuario_logado

        return context

    def atualizar_situacao(self):
        try:

            vendas = Venda.objects.all()
            for venda in vendas:

                if venda.situacaoMensal_dataApoio:

                    if (
                        venda.situacaoMensal == "Mensal"
                        and now()
                        >= venda.situacaoMensal_dataApoio + relativedelta(months=1)
                    ):
                        venda.situacaoMensal = "Finalizada"
                    elif (
                        venda.situacaoMensal == "Finalizada"
                        and now()
                        <= venda.situacaoMensal_dataApoio + relativedelta(months=1)
                    ):
                        venda.situacaoMensal = "Mensal"

                    venda.save()
        except Exception as e:

            print(f"Erro ao atualizar situação da venda: {e}")


def salvar_csvVenda(request, periodo=None, forma_pagamento=None):
    from django.utils import timezone
    from datetime import date, timedelta
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response.write("\ufeff")  #
    filename = f"Vendas_{timezone.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    response["Content-Disposition"] = f"attachment; filename={filename}"

    writer = csv.writer(response)

    cabecalho = [
        "ID",
        "Cliente",
        "Vendedor",
        "Executivo",
        "Agência Recomendada",
        "Recomendação da Venda",
        "Data da Venda",
        "Data Finalizado",
        "Custo Padrão",
        "Valor",
        "Desconto",
        "Custo sobre Venda",
        "Tipo de Serviço",
        "Forma de pagamento",
        "Nacionalidade",
        "Tipo de Cidadania",
    ]

    cabecalho.extend([f"Anexo {i}" for i in range(1, 11)])
    writer.writerow(cabecalho)

    vendas = Venda.objects.all().order_by("-id")

    if periodo and periodo != "todos":
        hoje_str = date.today().strftime("%d/%m/%Y")

        if periodo == "hoje":
            vendas = vendas.filter(data_venda=hoje_str)

        elif periodo == "semana":
            hoje = date.today()
            dias_para_domingo = (hoje.weekday() + 1) % 7
            inicio_semana = hoje - timedelta(days=dias_para_domingo)
            fim_semana = inicio_semana + timedelta(days=6)
            datas_semana = [
                (inicio_semana + timedelta(days=i)).strftime("%d/%m/%Y")
                for i in range(7)
            ]
            vendas = vendas.filter(data_venda__in=datas_semana)

        elif periodo == "mes":
            hoje = date.today()
            inicio_mes = hoje.replace(day=1)
            fim_mes = (
                inicio_mes.replace(month=inicio_mes.month + 1)
                if inicio_mes.month < 12
                else inicio_mes.replace(year=inicio_mes.year + 1, month=1)
            ) - timedelta(days=1)
            inicio_mes_str = inicio_mes.strftime("%d/%m/%Y")
            fim_mes_str = fim_mes.strftime("%d/%m/%Y")
            vendas = vendas.filter(
                data_venda__gte=inicio_mes_str, data_venda__lte=fim_mes_str
            )

    if forma_pagamento and forma_pagamento.lower() != "todos":
        vendas = vendas.filter(tipo_pagamento__iexact=forma_pagamento.strip())

    for venda in vendas:
        linha = [
            venda.id,
            venda.cliente.nome if venda.cliente else "S/D",
            (
                f"{venda.vendedor.first_name} {venda.vendedor.last_name}".strip()
                if venda.vendedor
                else "S/D"
            ),
            (
                f"{venda.executivo.first_name} {venda.executivo.last_name}".strip()
                if venda.executivo
                else "S/D"
            ),
            venda.Agencia_recomendada if venda.Agencia_recomendada else "S/D",
            venda.recomendação_da_Venda if venda.recomendação_da_Venda else "S/D",
            venda.data_venda,
            venda.finished_at if venda.finished_at else "S/D",
            venda.custo_padrao_venda if venda.custo_padrao_venda is not None else "S/D",
            venda.valor if venda.valor is not None else "S/D",
            f"{venda.desconto}%" if venda.desconto is not None else "S/D",
            venda.custo_sobre_venda if venda.custo_sobre_venda is not None else "S/D",
            (
                venda.tipo_servico_outros
                if venda.tipo_servico == "Outros"
                else venda.tipo_servico
            ),
            venda.tipo_pagamento,
            (
                venda.nacionalidade_outros
                if venda.nacionalidade == "Outros"
                else (venda.nacionalidade or "S/D")
            ),
            (
                venda.tipo_cidadania_outros
                if venda.tipo_cidadania == "Outros"
                else (venda.tipo_cidadania or "S/D")
            ),
        ]

        anexos = venda.anexos.all()
        anexos_links = []

        for anexo in anexos[:10]:
            try:
                if anexo.arquivo and hasattr(anexo.arquivo, "url"):
                    url = request.build_absolute_uri(anexo.arquivo.url)
                    nome_arquivo = anexo.arquivo.name.split("/")[-1]
                    link = f'=HYPERLINK("{url}", "{nome_arquivo}")'
                    anexos_links.append(link)
            except Exception as e:
                anexos_links.append(f"Erro: {str(e)}")

        while len(anexos_links) < 10:
            anexos_links.append("Sem Anexo")

        linha.extend(anexos_links)

        writer.writerow(linha)

    return response


def salvar_csvClientes(request, periodo):
    response = HttpResponse(content_type="text/csv")
    response.write("\ufeff")
    response["Content-Disposition"] = (
        "attachment; filename=dadosClientes_"
        + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        + ".csv"
    )

    writer = csv.writer(response)

    MAX_ANEXOS = 10

    headers = [
        "Nome",
        "Telefone 1",
        "Telefone 2",
        "Email 1",
        "Email 2",
        "Sexo",
        "Sexo Outros",
        "Data de Nascimento",
        "Idade",
        "Endereço",
        "Bairro",
        "Cidade",
        "Estado",
        "CEP",
        "RG",
        "CPF",
        "Número de Passaporte",
    ]

    headers += [f"Anexo {i+1}" for i in range(MAX_ANEXOS)]
    writer.writerow(headers)

    filters = {
        "hoje": {"created_at__date": date.today()},
        "semana": {
            "created_at__date__gte": date.today()
            - timedelta(days=date.today().weekday())
        },
        "mes": {"created_at__date__gte": date.today().replace(day=1)},
    }
    filter_kwargs = filters.get(periodo, {})
    clientes = (
        Cliente.objects.filter(**filter_kwargs)
        if filter_kwargs
        else Cliente.objects.all()
    )

    for cliente in clientes:
        try:
            anexos = cliente.anexos.all() if hasattr(cliente, "anexos") else []

            lista_anexos = []
            for anexo in anexos[:MAX_ANEXOS]:
                try:
                    if anexo.arquivo and hasattr(anexo.arquivo, "url"):
                        url = request.build_absolute_uri(anexo.arquivo.url)
                        nome_arquivo = anexo.arquivo.name.split("/")[-1]
                        lista_anexos.append(f'=HYPERLINK("{url}", "{nome_arquivo}")')
                except Exception as e:
                    lista_anexos.append(f"Erro: {str(e)}")

            while len(lista_anexos) < MAX_ANEXOS:
                lista_anexos.append("S/D")

            row = [
                cliente.nome or "S/D",
                cliente.telefone1 or "S/D",
                cliente.telefone2 or "S/D",
                cliente.email1 or "S/D",
                cliente.email2 or "S/D",
                cliente.get_sexo_display() if cliente.sexo else "S/D",
                cliente.sexo_outros or "S/D",
                cliente.data_nascimento or "S/D",
                cliente.idade or "S/D",
                cliente.endereco or "S/D",
                cliente.bairro or "S/D",
                cliente.cidade or "S/D",
                cliente.estado or "S/D",
                cliente.cep or "S/D",
                cliente.rg or "S/D",
                cliente.cpf or "S/D",
                cliente.num_passaporte or "S/D",
            ] + lista_anexos

            writer.writerow(row)
        except Exception as e:
            import logging

            logging.error(f"Erro ao processar cliente {cliente.id}: {str(e)}")
            continue
    return response
