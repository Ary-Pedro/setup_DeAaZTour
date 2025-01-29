from django.shortcuts import render

# INFO: Para uso do Auth e funções nativas de validação
from django.contrib.auth.mixins import LoginRequiredMixin


# INFO: funções uso geral
from django.db.models import Q
from apps.agency.models import Agencia


# INFO: funções de endereçamento
from django.http import Http404
from django.urls import reverse_lazy, reverse

# INFO: funções de direcionar e configurar
from django.shortcuts import get_object_or_404

# INFO: funções uso geral
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

import requests
import pandas as pd
import heapq
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .forms import AgenciaForm

# INFO: Agencia ----------------------------------------------------------------------------------------------------
# INFO: Agencia - cadastrar
class CadAgencia(CreateView):
    login_url = "log"  # URL para redirecionar para login
    model = Agencia
    form_class = AgenciaForm  # Defina a classe do formulário aqui
    template_name = "agency/Agencia_form.html"
    success_url = reverse_lazy("home")


# INFO: Agencia - listar
class ListAgencia(LoginRequiredMixin, ListView):
    model = Agencia
    paginate_by = 20
    template_name = "agency/cadastroAgencia_list.html"
    context_object_name = "cadastro_list"
    login_url = "log"  # URL para redirecionar para login


# INFO: Agencia - Deletar
class DeleteView(LoginRequiredMixin, DeleteView):
    login_url = "log"  # URL para redirecionar para login
    model = Agencia
    template_name = "agency/cadastroAgencia_confirm_delete.html"

    def get_success_url(self):
        numero_pagina = self.request.GET.get("page", 1)
        return f"{reverse_lazy('ListagemAgencia')}?page={numero_pagina}"


# INFO: Agencia - Atualizar
class UpdateView(LoginRequiredMixin, UpdateView):
    login_url = "log"  # URL para redirecionar para login
    model = Agencia 
    form_class = AgenciaForm
    template_name = "agency/Agencia_form.html"
    success_url = reverse_lazy("ListagemAgencia")


# INFO: Dados - Agencia
class DadosCadastros(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Agencia
    template_name = "buscasAgencia/dadosAgencia.html"

    def get_queryset(self):
        dados_id = self.kwargs.get("dados_id")
        return Agencia.objects.filter(id=dados_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Detalhes do Cadastro"
        return context


# INFO: Procurar - Agencia
class Procurar(LoginRequiredMixin, ListView):
    login_url = "log"  # URL para redirecionar para login
    model = Agencia
    template_name = "buscasAgencia/procurarAgencia.html"
    context_object_name = "cadastro_list"

    def get_queryset(self):
        procurar_termo = self.request.GET.get("q", "").strip()
        if not procurar_termo:
            raise Http404()

        return Agencia.objects.filter(
            Q(
                Q(nome_fantasia__istartswith=procurar_termo) | Q(cnpj__icontains=procurar_termo),
            )
        ).order_by("-id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        procurar_termo = self.request.GET.get("q", "").strip()
        context["page_title"] = (f'Procurar por "{procurar_termo}" |',)
        context["procurar_termo"] = procurar_termo
        context["total_resultados"] = self.get_queryset().count()
        return context



def calcular_proximidade(cep1, cep2):
    """
    Calcula a proximidade entre dois CEPs com base na diferença numérica total.
    """
    numero1 = int(cep1.replace('-', ''))
    numero2 = int(cep2.replace('-', ''))
    return abs(numero1 - numero2)


def dijkstra(ceps, distancias, origem):
    """
    Implementação do algoritmo de Dijkstra para calcular as menores distâncias.
    :param ceps: Lista de CEPs (nós).
    :param distancias: Dicionário com os pesos (arestas) entre os nós.
    :param origem: CEP de origem.
    :return: Dicionário com as menores distâncias de 'origem' para cada nó.
    """
    menor_distancia = {cep: float('inf') for cep in ceps}
    menor_distancia[origem] = 0
    visitados = set()

    # Fila de prioridade
    fila = [(0, origem)]  # (distância acumulada, nó atual)

    while fila:
        distancia_atual, cep_atual = heapq.heappop(fila)

        if cep_atual in visitados:
            continue

        visitados.add(cep_atual)

        # Atualizar distâncias para os vizinhos
        for vizinho, peso in distancias.get(cep_atual, {}).items():
            nova_distancia = distancia_atual + peso
            if nova_distancia < menor_distancia[vizinho]:
                menor_distancia[vizinho] = nova_distancia
                heapq.heappush(fila, (nova_distancia, vizinho))

    return menor_distancia


@csrf_exempt
def Pesquisar_rota(request):
    """
    View para processar a busca de rotas com base no CEP do usuário e listar as agências mais próximas.
    """
    agencias_com_distancia = []  # Lista que armazenará os resultados

    if request.method == "POST":
        cep_usuario = request.POST.get('cep')  # Obtém o CEP enviado pelo formulário

        if cep_usuario:
            # Obter todas as agências cadastradas no banco
            agencias = Agencia.objects.all()

            # Extrair os dados necessários das agências cadastradas
            ceps_agencias = [
                {
                    "nome do contato": agencia.nome_contato,
                    "nome da agência": agencia.nome_fantasia,
                    "cep": agencia.cep,
                    "bairro": agencia.bairro,
                    "cidade": agencia.municipio
                }
                for agencia in agencias if agencia.cep
            ]

            # Construir o grafo de distâncias entre CEPs
            ceps = [item["cep"] for item in ceps_agencias] + [cep_usuario]
            distancias = {cep: {} for cep in ceps}

            # Preencher as distâncias entre todos os pares de CEPs
            for i, cep1 in enumerate(ceps):
                for j, cep2 in enumerate(ceps):
                    if cep1 != cep2:
                        distancias[cep1][cep2] = calcular_proximidade(cep1, cep2)

            # Executar o algoritmo de Dijkstra a partir do CEP do usuário
            try:
                menores_distancias = dijkstra(ceps, distancias, cep_usuario)

                # Montar a lista com as informações das agências e distância
                agencias_com_distancia = [
                    {
                        "agencia": {
                            "nome": item["nome"],
                            "cep": item["cep"],
                            "bairro": item["bairro"],
                            "cidade": item["cidade"]
                        },
                        "distancia": menores_distancias[item["cep"]]
                    }
                    for item in ceps_agencias
                ]

                # Ordenar a lista pelas menores distâncias
                agencias_com_distancia = sorted(agencias_com_distancia, key=lambda x: x["distancia"])
            except Exception as e:
                print(f"Erro ao processar os dados: {e}")

    return render(request, 'pesquisarRota.html', {'agencias_com_distancia': agencias_com_distancia})


def obter_bairro_por_cep(cep):
    """
    Consulta a API ViaCEP para obter o nome do bairro associado a um CEP.
    Retorna 'Desconhecido' se a consulta falhar.
    """
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep.replace('-', '')}/json/")
        if response.status_code == 200:
            data = response.json()
            return data.get("bairro", "Desconhecido")  # Retorna 'Desconhecido' se o bairro não estiver disponível
        else:
            return "Desconhecido"
    except Exception as e:
        print(f"Erro ao consultar o CEP {cep}: {e}")
        return "Desconhecido"


def classificar_ceps_com_bairros(ceps, cep_referencia):
    """
    Classifica uma lista de CEPs com base na proximidade de um CEP de referência.
    Exibe os nomes dos bairros associados no lugar dos CEPs.
    """

    def calcular_proximidade(cep1, cep2):
        """
        Calcula a proximidade entre dois CEPs com base na distância numérica total.
        """
        numero1 = int(cep1.replace('-', ''))
        numero2 = int(cep2.replace('-', ''))
        return abs(numero1 - numero2)

    # Obter os bairros para cada CEP
    bairros = {cep: obter_bairro_por_cep(cep) for cep in ceps}
    bairro_referencia = obter_bairro_por_cep(cep_referencia)

    # Criar DataFrame para manipulação
    df_ceps = pd.DataFrame({'cep': ceps, 'bairro': [bairros[cep] for cep in ceps]})
    df_ceps['proximidade'] = df_ceps['cep'].apply(lambda cep: calcular_proximidade(cep, cep_referencia))

    # Ordenar os CEPs pela proximidade
    df_ceps = df_ceps.sort_values(by='proximidade')

    # Substituir o CEP pelo nome do bairro no DataFrame
    df_ceps['cep'] = df_ceps['bairro']
    df_ceps.drop(columns=['bairro'], inplace=True)

    return df_ceps[['cep', 'proximidade']]
