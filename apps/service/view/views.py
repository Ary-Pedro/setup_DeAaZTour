# INFO: Para uso do Auth e funções nativas de validação
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# INFO: funções uso geral
from django.db.models import Q, Sum
from apps.service.models import OPC_SERVICES, Venda, Anexo
from apps.client.models import Cliente
from apps.worker.models import Funcionario
from django.views.generic import TemplateView
from datetime import date, timedelta

# INFO: funções de endereçamento
from django.http import Http404, HttpResponseRedirect, HttpResponseRedirect
from django.urls import reverse_lazy, reverse

# INFO: funções de direcionar e configurar
from django.shortcuts import get_object_or_404

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View
from django import forms
from django.shortcuts import redirect, get_object_or_404

# INFO: Data
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta  # Usando relativedelta para manipulação de meses
from django.db.models import Count

from django.shortcuts import render

from .forms import VendaAtualizar, VendaForm


def excluir_anexo(request, anexo_id):
    anexo = get_object_or_404(Anexo, id=anexo_id)
    anexo.delete()
    return redirect(request.META.get("HTTP_REFERER", "ListagemVenda"))

# INFO: Venda  --------------------------------------------------------------------------------------------------------

# INFO: Venda - Cadastar
class CadVendas(LoginRequiredMixin, CreateView):
    login_url = "log"
    model = Venda
    form_class = VendaForm
    template_name = "service/Vendas_form.html"
    success_url = reverse_lazy("home")

    def get_initial(self):
        initial = super().get_initial()
        initial["vendedor"] = self.request.user
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["clientes"] = Cliente.objects.all()
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
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
            cliente = Cliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (
                    not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                form.instance.vendedor = self.request.user

                tipo_servico = self.request.POST.get("tipo_servico")
                form.instance.tipo_servico = tipo_servico

                # Verifica se o tipo de serviço está na lista OPC_SERVICES
                # Utilizamos strip() para evitar problemas com espaços em branco
                if tipo_servico and tipo_servico.strip() in [item.strip() for item in OPC_SERVICES]:
                    form.instance.status_executivo = True
                # Se desejar, pode definir False caso não esteja
                else:
                    form.instance.status_executivo = False

                if tipo_servico == "Outros":
                    form.instance.tipo_servico_outros = self.request.POST.get("tipo_servico_outros")
                else:
                    form.instance.tipo_servico_outros = None

                if tipo_servico == "Passaporte":
                    form.instance.nacionalidade = self.request.POST.get("nacionalidade")
                    if form.instance.nacionalidade == "Outros":
                        form.instance.nacionalidade_outros = self.request.POST.get("nacionalidade_outros")
                    else:
                        form.instance.nacionalidade_outros = None

                elif tipo_servico == "Cidadania":
                    form.instance.tipo_cidadania = self.request.POST.get("tipo_cidadania")
                    if form.instance.tipo_cidadania == "Outros":
                        form.instance.tipo_cidadania_outros = self.request.POST.get("tipo_cidadania_outros")
                    else:
                        form.instance.tipo_cidadania_outros = None

                response = super().form_valid(form)
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do Cliente inválidos.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Informe o nome do Cliente.')
            return self.form_invalid(form)


# INFO: Venda - Listar
class ListVenda(LoginRequiredMixin, ListView):
    login_url = "log"
    model = Venda
    paginate_by = 20
    template_name = "service/Venda_list.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        if self.request.user.departamento == 'Adm':
            queryset = Venda.objects.all()
        else:
            queryset = Venda.objects.filter(vendedor=self.request.user)
        
        order = self.request.GET.get('order', 'desc')
        if order == 'asc':
            return queryset.order_by('id')
        return queryset.order_by('-id')



# INFO: Venda - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    form_class = VendaAtualizar  
    template_name = "service/Vendas_form.html"
    success_url = reverse_lazy("ListagemVenda")

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
        context["clientes"] = Cliente.objects.all()
        context.update(self.get_initial())
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Desabilita os campos 'vendedor' e 'situacaoMensal'
        form.fields['vendedor'].initial = self.object.vendedor
        if 'vendedor' in form.fields:
            form.fields['vendedor'].widget.attrs.pop('disabled', None)
        return form

    def form_valid(self, form):
        cliente_input = self.request.POST.get("cliente")
        cpf_input = self.request.POST.get("cpf_cliente")
        id_input = self.request.POST.get("pk_cliente")

        if cliente_input:
            cliente_nome = cliente_input.strip()
            cliente = Cliente.objects.filter(
                nome__iexact=cliente_nome, cpf=cpf_input
            ).first()

            if cliente and (not cpf_input or cliente.cpf == cpf_input) and (
                    not id_input or cliente.pk == int(id_input)):
                form.instance.cliente = cliente
                if 'vendedor' in form.cleaned_data and form.cleaned_data['vendedor']:
                    form.instance.vendedor = form.cleaned_data['vendedor']
                else:
                    form.instance.vendedor = self.object.vendedor


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
               
                return response
            else:
                messages.error(self.request, 'Cliente não encontrado ou dados do Cliente inválidos.')
                return self.form_invalid(form)
        else:
            messages.error(self.request, 'Informe o nome do Cliente.')
            return self.form_invalid(form)
    
    ''' Caso deseje que apenas o vendedor possa ser associado a uma venda usar a função abaixo
    def clean_vendedor(self):
        vendedor = self.cleaned_data.get('vendedor')
        if not vendedor:
            return self.instance.vendedor  # Mantém o original se não for fornecido
        return vendedor
'''

# INFO: Venda - Deletar
class DeleteView(LoginRequiredMixin, DeleteView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "service/Venda_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('ListagemVenda')}?page={numero_pagina}"



# INFO: Procurar -------------------------------------------------------------------------------------------------------
# INFO: Procurar - Venda
class Procurar(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "buncasVendas/procurarVenda.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        inicio_mes = date.today().replace(day=1)
        proximo_mes = (inicio_mes + timedelta(days=31)).replace(day=1)
        return Venda.objects.filter(
            data_venda__gte=inicio_mes,
            data_venda__lt=proximo_mes
        ).filter(
            Q(cliente__cidade__istartswith=procurar_termo) | Q(cliente__nome__istartswith=procurar_termo)
            | Q(tipo_servico__icontains=procurar_termo) | Q(tipo_servico_outros__istartswith=procurar_termo)
            | Q(tipo_pagamento__istartswith=procurar_termo)
        ).order_by("-id")


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = (f'Procurar por "{procurar_termo}" |',)
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        total_geral = Venda.objects.count()
        context["total_geral"] = total_geral
        return context


# INFO: Dados - Venda
class DadosCadastros(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Venda
    template_name = "buncasVendas/dadosVenda.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Venda.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        
        # Abordagem 1: Verificar parâmetro GET explícito
        fluxo_id = self.request.GET.get('from_fluxo')
        if fluxo_id:
            context["from_fluxo"] = fluxo_id
            return context
        
        # Abordagem 2: Verificar referer (backup)
        referer = self.request.META.get("HTTP_REFERER", "")
        context["from_fluxo_completo"] = any(
            keyword in referer 
            for keyword in ["fluxo-completo", "detalhes-fluxo"]
        )
        
        # Se veio do fluxo, tentar extrair o ID
        if context["from_fluxo_completo"]:
            try:
                path = urlparse(referer).path
                parts = [p for p in path.split('/') if p]
                # Supondo que a URL seja algo como /fluxo-completo/123/
                if len(parts) >= 2 and parts[-2].isdigit():
                    context["fluxo_id"] = parts[-2]
                elif parts[-1].isdigit():
                    context["fluxo_id"] = parts[-1]
            except Exception as e:
                print(f"Erro ao extrair fluxo_id do referer: {e}")
        
        return context





# INFO: Venda - Validar
class Validar(LoginRequiredMixin, View):
    login_url = "log"  # URL para redirecionar para login

    @staticmethod
    def get(request, pk):
        finalizar = get_object_or_404(Venda, pk=pk)
        finalizar.mark_as_complete()


        numero_pagina = request.GET.get("page", 1)

        url = reverse("ListagemVenda")
        return HttpResponseRedirect(f"{url}?page={numero_pagina}")



# INFO: Rank -----------------------------------------------------------------------------------------------------------
# INFO: Chamar e definir rank
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


