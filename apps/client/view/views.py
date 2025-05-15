# INFO: Para uso do Auth e funções nativas de validação
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# INFO: funções uso geral
from django.db.models import Q
from apps.client.models import Cliente, Anexo

# INFO: funções de endereçamento
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404

# INFO: funções de direcionar e configurar
from django.shortcuts import get_object_or_404

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django import forms

from django.shortcuts import render
from .forms import ClienteForm, AtualizarForm


def excluir_anexo_cliente(request, anexo_id):
    anexo = get_object_or_404(Anexo, id=anexo_id)
    anexo.delete()
    return redirect(request.META.get("HTTP_REFERER", "ListagemCliente"))


# INFO: Cliente --------------------------------------------------------------------------------------------------------
# INFO: Cliente - Cadastrar
class CadCliente(LoginRequiredMixin, CreateView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    form_class = ClienteForm  # Defina a classe do formulário aqui
    template_name = "client/Cliente_form.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        # Salva o cliente primeiro

        # Ajusta o valor do campo sexo antes de salvar o cliente
        sexo = self.request.POST.get("sexo")
        form.instance.sexo = sexo

        if sexo == "O":
            form.instance.sexo_outros = self.request.POST.get("sexo_outros")
        else:
            form.instance.sexo_outros = None

        response = super().form_valid(form)

        # Obtém os arquivos enviados
        arquivos = self.request.FILES.getlist("arquivos")

        # Cria um anexo para cada arquivo enviado e associa ao cliente
        for arquivo in arquivos:
            Anexo.objects.create(arquivo=arquivo, cliente=self.object)

        return response


# INFO: Cliente - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Cliente
    form_class = AtualizarForm
    template_name = "client/Cliente_form.html"
    success_url = reverse_lazy("ListagemCliente")


# INFO: Cliente - listar
class ListCliente(LoginRequiredMixin, ListView):
    model = Cliente
    paginate_by = 20
    template_name = "client/Cliente_list.html"
    context_object_name = "cadastro_list"
    login_url = "log"  # URL para redirecionar para login

    def get_queryset(self):
        queryset = Cliente.objects.all()

        order = self.request.GET.get("order", "desc")
        if order == "asc":
            return queryset.order_by("id")
        return queryset.order_by("-id")


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

from django.http import JsonResponse
from django.views.decorators.http import require_GET
import re

from django.db.models import Q


@require_GET
def cliente_detail_api(request, cpf):
    try:
        # Remove todos os não dígitos
        cpf_limpo = re.sub(r"[^0-9]", "", cpf)

        if len(cpf_limpo) != 11:
            return JsonResponse({"erro": "CPF deve conter 11 dígitos"}, status=400)

        # Tenta encontrar o cliente pelo CPF limpo (sem formatação)
        cliente = Cliente.objects.filter(cpf=cpf_limpo).first()

        if not cliente:
            # Se não encontrar, tenta buscar por um CPF que contenha o CPF limpo
            # (útil se o CPF no banco estiver formatado)
            cliente = Cliente.objects.filter(cpf__contains=cpf_limpo).first()

        if not cliente:
            return JsonResponse({"erro": "Cliente não encontrado"}, status=404)

        return JsonResponse(
            {
                "nome": cliente.nome,
                "cpf": cliente.cpf,
                "num_passaporte": cliente.num_passaporte or "",
                "data_nascimento": cliente.data_nascimento or "",  # Já é string
                "endereco": cliente.endereco or "",
                "cep": cliente.cep or "",
                "bairro": cliente.bairro or "",
                "estado": cliente.estado or "",
            }
        )

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=500)
