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
from .forms import ClienteForm, AtualizarForm

# INFO: Cliente --------------------------------------------------------------------------------------------------------
# INFO: Cliente - Cadastrar
class CadCliente(LoginRequiredMixin, CreateView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    form_class = ClienteForm  # Defina a classe do formulário aqui
    template_name = "client/Cliente_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
       
        return response


# INFO: Cliente - listar
class ListCliente(LoginRequiredMixin, ListView):
    model = Cliente
    paginate_by = 20
    template_name = "client/Cliente_list.html"
    context_object_name = "cadastro_list"
    login_url = "log"  # URL para redirecionar para login



# INFO: Cliente - Validar
class Validar(View):
    login_url = "log"  # URL para redirecionar para login

    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(Cliente, pk=pk)
        finalizar.mark_has_complete()

        numero_pagina = request.GET.get("page", 1)

        url = reverse("ListagemCliente")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")



# INFO: Cliente - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    form_class = AtualizarForm
    template_name = "client/Cliente_form.html"
    success_url = reverse_lazy("ListagemCliente")


# INFO: Cliente - Deletar
class DeleteView(LoginRequiredMixin, DeleteView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    template_name = "client/Cliente_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('ListagemCliente')}?page={numero_pagina}"


# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Cliente
class Procurar(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login

    model = Cliente
    template_name = "buscasCliente/procurarCliente.html"
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
class DadosCadastros(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    template_name = "buscasCliente/dadosCliente.html"

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
        "num_passaporte": cliente.num_passaporte,
        "data_nascimento": cliente.data_nascimento,
        "endereco": cliente.endereco,
        "cep": cliente.cep,
        "bairro": cliente.bairro,
        "estado": cliente.estado,
    }
    return JsonResponse(data)

