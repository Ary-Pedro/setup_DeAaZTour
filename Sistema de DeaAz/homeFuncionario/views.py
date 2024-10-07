from django.core.checks import messages
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from homeAdmin.models import CustomUser_Funcionario
from homeFuncionario.models import CadastroEspelho, VendaEspelho
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


class FuncionarioHome(LoginRequiredMixin, TemplateView):
    template_name = 'homeFuncionario/homeFuncionario.html'
    login_url = 'log'  # URL para redirecionar para login
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_logado'] = self.request.user
        return context


class cadClienteFuncionario(CreateView):
    model = CadastroEspelho
    fields = ["nome", "celular", "cpf", "rg", "sexo", "data_nascimento", "num_passaporte", "endereco", "bairro",
              "estado", "cep", 'anexo1',
              'anexo2',
              'anexo3', ]
    template_name = 'formsClienteFuncionario/cadastroClienteFuncionario_form.html'
    success_url = reverse_lazy("homeFuncionario")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Cliente de id {self.object.id} cadastrado com sucesso!')
        return response


class FuncionarioCadListView(ListView):
    model = CadastroEspelho
    paginate_by = 20
    template_name = 'formsClienteFuncionario/cadastroClienteFuncionario_list.html'
    context_object_name = 'cadastro_list'


class ValidarClienteFuncionario(View):
    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(CadastroEspelho, pk=pk)
        finalizar.mark_has_complete()

        numero_pagina = request.GET.get('page', 1)

        url = reverse('FuncionarioListagemCliente')
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")


class ClienteUpdateViewFuncionario(UpdateView):
    model = CadastroEspelho
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
    template_name = 'formsClienteFuncionario/cadastroClienteFuncionario_form.html'
    success_url = reverse_lazy("FuncionarioListagemCliente")


class ClienteDeleteViewFuncionario(DeleteView):
    model = CadastroEspelho
    template_name = 'formsClienteFuncionario/cadastroClienteFuncionario_confirm_delete.html'

    def get_success_url(self):
        numero_pagina = self.request.GET.get('page', 1)
        return f"{reverse_lazy('FuncionarioListagemCliente')}?page={numero_pagina}"


class ProcurarClienteFuncionario(ListView):
    model = CadastroEspelho
    template_name = "formsClienteFuncionario/buscasCliente/procurarClienteFuncionario.html"
    context_object_name = 'cadastro_list'

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return CadastroEspelho.objects.filter(
            Q(
                Q(nome__istartswith=procurar_termo) | Q(cpf__icontains=procurar_termo),
            )
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = f'Procurar por "{procurar_termo}" |',
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context


class DadosCadastrosClienteFuncionario(ListView):
    model = CadastroEspelho
    template_name = "formsClienteFuncionario/buscasCliente/dadosClienteFuncionario.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return CadastroEspelho.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


# vendas

class cadVendasFuncionario(CreateView):
    model = VendaEspelho
    fields = ["vendedor", "valor", "situacaoMensal"]
    template_name = 'Vendas/formsVenda/cadastroVendaFuncionario_form.html'
    success_url = reverse_lazy("homeFuncionario")

    def get_initial(self):
        initial = super().get_initial()
        initial["vendedor"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clientes"] = CadastroEspelho.objects.all()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Desabilita os campos 'vendedor' e 'situacaoMensal'
        form.fields["vendedor"].widget.attrs["disabled"] = True
        form.fields["situacaoMensal"].widget.attrs["disabled"] = True
        return form

    def form_valid(self, form):
        cliente_input = self.request.POST.get("cliente")
        cpf_input = self.request.POST.get("cpf_cliente")
        id_input = self.request.POST.get("pk_cliente")

        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadastroEspelho.objects.filter(
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



class CadListViewVendaFuncionario(ListView):
    model = VendaEspelho
    paginate_by = 20
    template_name = 'Vendas/formsVenda/cadastroVendaFuncionario_list.html'
    context_object_name = 'cadastro_list'


class VendaUpdateViewFuncionario(UpdateView):
    model = VendaEspelho
    fields = ["vendedor", "valor", "situacaoMensal"]
    template_name = 'Vendas/formsVenda/cadastroVendaFuncionario_form.html'
    success_url = reverse_lazy("FuncionarioListagemVenda")

    def get_initial(self):
        initial = super().get_initial()
        venda = self.get_object()

        initial['valor'] = venda.valor
        initial['situacaoMensal'] = venda.situacaoMensal
        initial['tipo_servico'] = venda.tipo_servico
        initial['nacionalidade'] = venda.nacionalidade
        if venda.nacionalidade == 'outros':
            initial['nacionalidade_outros'] = venda.nacionalidade_outros
        if venda.cliente:
            initial['cliente'] = venda.cliente.nome
            initial['cpf_cliente'] = venda.cliente.cpf
            initial['pk_cliente'] = venda.cliente.pk
            initial['passaporte_cliente'] = venda.cliente.num_passaporte
            initial['data_nascimento_cliente'] = venda.cliente.data_nascimento
            initial['endereco_cliente'] = venda.cliente.endereco
            initial['cep_cliente'] = venda.cliente.cep
            initial['bairro_cliente'] = venda.cliente.bairro
            initial['estado_cliente'] = venda.cliente.estado
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['clientes'] = CadastroEspelho.objects.all()
        context.update(self.get_initial())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Desabilita os campos 'vendedor' e 'situacaoMensal'
        form.fields["vendedor"].widget.attrs["disabled"] = True
        return form

    def form_valid(self, form):
        cliente_input = self.request.POST.get('cliente')
        cpf_input = self.request.POST.get('cpf_cliente')
        id_input = self.request.POST.get('pk_cliente')



        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = CadastroEspelho.objects.filter(
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


class VendaDeleteViewFuncionario(DeleteView):
    model = VendaEspelho
    template_name = 'Vendas/formsVenda/cadastroVendaFuncionario_confirm_delete.html'

    def get_success_url(self):
        numero_pagina = self.request.GET.get('page', 1)
        return f"{reverse_lazy('FuncionarioListagemVenda')}?page={numero_pagina}"


class ProcurarVendaFuncionario(ListView):
    model = VendaEspelho
    template_name = "Vendas/buscasVendas/procurarVendaFuncionario.html"
    context_object_name = 'cadastro_list'

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return VendaEspelho.objects.filter(
            Q(cliente__nome__istartswith=procurar_termo)
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = f'Procurar por "{procurar_termo}" |',
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context


class DadosCadastrosVendaFuncionario(ListView):
    model = VendaEspelho
    template_name = "Vendas/buscasVendas/dadosVendaFuncionario.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return VendaEspelho.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


class ValidarVendasFuncionario(View):
    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(VendaEspelho, pk=pk)
        finalizar.mark_has_complete()

        numero_pagina = request.GET.get('page', 1)

        url = reverse('FuncionarioListagemVenda')
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")


def cliente_detail_api(request, pk):
    cliente = get_object_or_404(CadastroEspelho, pk=pk)
    data = {
        'nome': cliente.nome,
        'cpf': cliente.cpf,
    }
