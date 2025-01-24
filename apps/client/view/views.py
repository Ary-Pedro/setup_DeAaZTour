# INFO: Para uso do Auth e funções nativas de validação
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# INFO: funções uso geral
from django.db.models import Q
from apps.client.models import Cliente

# INFO: funções de endereçamento
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# INFO: funções de direcionar e configurar
from django.shortcuts import get_object_or_404

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django import forms

from django.shortcuts import render

# INFO: Cliente --------------------------------------------------------------------------------------------------------
# INFO: Cliente - Cadastrar
class cadCliente(LoginRequiredMixin, CreateView):
    login_url = "log"  # URL para redirecionar para login

    model = Cliente
    fields = [
        "nome",
        "celular",
        "cpf",
        "sexo",
        "data_nascimento",
        "num_passaporte",
        "endereco",
        "cidade",
        "bairro",
        "estado",
        "cep",
        'anexo1',
        'anexo2',
        'anexo3',
    ]
    template_name = "client/formsCliente/cadastroCliente_form.html"
    success_url = reverse_lazy("homeAdmin")

    def form_valid(self, form):
        response = super().form_valid(form)
       
        return response


# INFO: Cliente - listar
class CadListView(LoginRequiredMixin, ListView):
    model = Cliente
    paginate_by = 20
    template_name = "client/formsCliente/cadastroCliente_list.html"
    context_object_name = "cadastro_list"
    login_url = "log"  # URL para redirecionar para login



# INFO: Cliente - Validar
class ValidarCliente(View):
    login_url = "log"  # URL para redirecionar para login

    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(Cliente, pk=pk)
        finalizar.mark_has_complete()

        numero_pagina = request.GET.get("page", 1)

        url = reverse("AdminListagemCliente")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")



# INFO: Cliente - Atualizar
class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login

    model = Cliente
    fields = [
        "nome",
        "celular",
        "cpf",
        "rg",
        "sexo",
        "data_nascimento",
        "num_passaporte",
        "endereco",
        "cidade",
        "bairro",
        "estado",
        "cep",
        'anexo1',
        'anexo2',
        'anexo3',
    ]
    template_name = "client/formsCliente/cadastroCliente_form.html"
    success_url = reverse_lazy("AdminListagemCliente")


# INFO: Cliente - Deletar
class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    login_url = "log"  # URL para redirecionar para login

    model = Cliente
    template_name = "client/formsCliente/cadastroCliente_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('AdminListagemCliente')}?page={numero_pagina}"


# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Cliente
class ProcurarCliente(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login

    model = Cliente
    template_name = "client/buscasCliente/procurarCliente.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return Cliente.objects.filter(
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
class DadosCadastrosCliente(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    template_name = "client/buscasCliente/dadosCliente.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Cliente.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context
    


# NOTE: função para puxar informaçoes de clientes em nova venda pelo id
def cliente_detail_api(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
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

