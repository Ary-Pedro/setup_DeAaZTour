"""
# INFO: Para uso do Auth e funções nativas de validação
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# INFO: funções uso geral
from django.db.models import Q
from service.models import Venda
from client.models import CadCliente
from worker.models import Funcionario
from django.views.generic import TemplateView

# INFO: funções de endereçamento
from django.http import Http404, HttpResponseRedirect, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# INFO: funções de direcionar e configurar
from django.shortcuts import get_object_or_404

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django import forms

# INFO: Data
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta  # Usando relativedelta para manipulação de meses
from django.db.models import Count

from django.shortcuts import render


# INFO: Venda  --------------------------------------------------------------------------------------------------------

# INFO: Venda - Cadastar
class cadVendas(LoginRequiredMixin, CreateView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    fields = ["vendedor", "valor", "tipo_pagamento", "situacaoMensal"]
    template_name = "templates/service/formsVenda/cadastroVendas_form.html"
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

        print(f"Cliente Input: {cliente_input}")
        print(f"CPF Input: {cpf_input}")
        print(f"ID Input: {id_input}")

        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadCliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (
                    not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                form.instance.vendedor = self.request.user

                tipo_servico = self.request.POST.get("tipo_servico")
                form.instance.tipo_servico = tipo_servico

                if tipo_servico == "Outros":
                    form.instance.tipo_servico_outros = self.request.POST.get("tipo_servico_outros")
                else:
                    form.instance.tipo_servico_outros = None

                # Lógica condicional para "Passaporte"
                if tipo_servico == "Passaporte":
                    form.instance.nacionalidade = self.request.POST.get("nacionalidade")
                    if form.instance.nacionalidade == "Outros":
                        form.instance.nacionalidade_outros = self.request.POST.get("nacionalidade_outros")
                    else:
                        form.instance.nacionalidade_outros = None

                # Lógica condicional para "Cidadania"
                elif tipo_servico == "Cidadania":
                    form.instance.tipo_cidadania = self.request.POST.get("tipo_cidadania")
                    if form.instance.tipo_cidadania == "Outros":
                        form.instance.tipo_cidadania_outros = self.request.POST.get("tipo_cidadania_outros")
                    else:
                        form.instance.tipo_cidadania_outros = None

                response = super().form_valid(form)
                messages.success(
                    self.request,
                    f'Venda registrada com sucesso! Cliente de ID {self.object.id} cadastrado com sucesso.'
                )
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do Cliente inválidos.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Informe o nome do Cliente.')
            return self.form_invalid(form)


# INFO: Venda - Listar
class CadListViewVenda(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    paginate_by = 20
    template_name = "templates/service/formsVenda/cadastroVenda_list.html"
    context_object_name = "cadastro_list"


# INFO: Venda - Atualizar
class VendaUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    fields = ["vendedor", "valor", "tipo_pagamento", "situacaoMensal"]
    template_name = "templates/service/formsVenda/cadastroVendas_form.html"
    success_url = reverse_lazy("AdminListagemVenda")

    def get_initial(self):
        initial = super().get_initial()
        venda = self.get_object()

        initial["valor"] = venda.valor
        initial["situacaoMensal"] = venda.situacaoMensal
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
        if venda.tipo_servico:
            initial["tipo_servico"] = venda.tipo_servico
            if venda.tipo_servico == "Outros":
                initial["tipo_servico_outros"] = venda.tipo_servico_outros

            # Dependendo do tipo de serviço, preencher campos relacionados
            if venda.tipo_servico == "Passaporte":
                if venda.nacionalidade:
                    initial["nacionalidade"] = venda.nacionalidade
                    if venda.nacionalidade == "Outros":
                        initial["nacionalidade_outros"] = venda.nacionalidade_outros

            if venda.tipo_servico == "Cidadania":
                if venda.tipo_cidadania:
                    initial["tipo_cidadania"] = venda.tipo_cidadania
                    if venda.tipo_cidadania == "Outros":
                        initial["tipo_cidadania_outros"] = venda.tipo_cidadania_outros
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

        print(f"Cliente Input: {cliente_input}")
        print(f"CPF Input: {cpf_input}")
        print(f"ID Input: {id_input}")

        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadCliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (
                    not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                form.instance.vendedor = self.request.user

                tipo_servico = self.request.POST.get("tipo_servico")
                form.instance.tipo_servico = tipo_servico

                # Lógica condicional para "Passaporte"
                if tipo_servico == "Passaporte":
                    form.instance.nacionalidade = self.request.POST.get("nacionalidade")
                    if form.instance.nacionalidade == "Outros":
                        form.instance.nacionalidade_outros = self.request.POST.get("nacionalidade_outros")
                    else:
                        form.instance.nacionalidade_outros = None

                    form.instance.tipo_cidadania = None
                    form.instance.tipo_cidadania_outros = None


                # Lógica condicional para "Cidadania"
                elif tipo_servico == "Cidadania":
                    form.instance.tipo_cidadania = self.request.POST.get("tipo_cidadania")
                    if form.instance.tipo_cidadania == "Outros":
                        form.instance.tipo_cidadania_outros = self.request.POST.get("tipo_cidadania_outros")
                    else:
                        form.instance.tipo_cidadania_outros = None

                    form.instance.nacionalidade = None
                    form.instance.nacionalidade_outros = None

                else:
                    form.instance.nacionalidade = None
                    form.instance.nacionalidade_outros = None
                    form.instance.tipo_cidadania = None
                    form.instance.tipo_cidadania_outros = None

                response = super().form_valid(form)
                messages.success(
                    self.request,
                    f'Venda registrada com sucesso! Cliente de ID {self.object.id} cadastrado com sucesso.'
                )
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do Cliente inválidos.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Informe o nome do Cliente.')
            return self.form_invalid(form)


# INFO: Venda - Deletar
class VendaDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "templates/service/formsVenda/cadastroVenda_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('AdminListagemVenda')}?page={numero_pagina}"



# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Venda
class ProcurarVenda(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "templates/service/buncasVendas/procurarVenda.html"
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
class DadosCadastrosVenda(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "templates/service/buncasVendas/dadosVenda.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Venda.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


# INFO: Venda - Validar
class ValidarVendas(LoginRequiredMixin, View):
    login_url = "log"  # URL para redirecionar para login

    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(Venda, pk=pk)
        finalizar.mark_as_complete()

        numero_pagina = request.GET.get("page", 1)

        url = reverse("AdminListagemVenda")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")



# INFO: Rank -----------------------------------------------------------------------------------------------------------
# INFO: Chamar e definir rank
class Rank(LoginRequiredMixin, TemplateView):
    template_name = "templates/ranking/rank.html"
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
        if isinstance(usuario_logado, Funcionario) and usuario_logado.departamento == "Adm.":
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
"""
