from django.contrib import admin
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from homeAdmin import views
from homeAdmin.views import (AdminHome, cadCliente, CadListView, ValidarCliente, ClienteUpdateView,
                             ClienteDeleteView, ProcurarCliente, DadosCadastrosCliente, CadListViewFunc,
                             FuncionarioUpdateView, ProcurarFuncionario,Rank,
                             DadosCadastrosFuncionario, cadVendas, CadListViewVenda, VendaUpdateView, VendaDeleteView,
                             ProcurarVenda, DadosCadastrosVenda, log, LogoutView, ValidarVendas, RegisterView,
                             RedefinirSenha)

from homeFuncionario.views import (FuncionarioHome, cadClienteFuncionario, FuncionarioCadListView,
                                   ValidarClienteFuncionario, ClienteUpdateViewFuncionario,
                                   ClienteDeleteViewFuncionario,
                                   ProcurarClienteFuncionario, DadosCadastrosClienteFuncionario, cadVendasFuncionario,
                                   CadListViewVendaFuncionario, VendaUpdateViewFuncionario, VendaDeleteViewFuncionario,
                                   ValidarVendasFuncionario, ProcurarVendaFuncionario, DadosCadastrosVendaFuncionario)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", AdminHome.as_view(), name="homeAdmin"),

    # CLIENTE

    path("cadCliente", cadCliente.as_view(), name="cadCliente"),
    path(f"AdminListagemCliente/", CadListView.as_view(), name="AdminListagemCliente"),
    path(f"btn-complete/cliente/-<int:pk>", ValidarCliente.as_view(), name="cliente_complete"),
    path(f"cliente/Atualizar/-<int:pk>", ClienteUpdateView.as_view(), name="cliente_atualizar"),
    path(f"Admin/cliente_deletar/-<int:pk>", ClienteDeleteView.as_view(), name="cliente_deletar"),
    path(f"Admin/buscar-cliente/", ProcurarCliente.as_view(), name="procurarCliente"),
    path(f"Admin/buscar-cliente/dados/-<int:dados_id>", DadosCadastrosCliente.as_view(), name="dadosCliente"),

    # -------------------------------------------------------------------------------------------------------------------

    # FUNCIONARIO

    path(f"AdminListagemFuncionario/", CadListViewFunc.as_view(), name="AdminListagemFuncionario"),
    path(f"funcionario/Atualizar/-<int:pk>", FuncionarioUpdateView.as_view(), name="funcionario_atualizar"),
    path(f"Admin/buscar-funcionario/", ProcurarFuncionario.as_view(), name="procurarFuncionario"),
    path(f"Admin/buscar-Funcionario/dados/-<int:dados_id>", DadosCadastrosFuncionario.as_view(),
         name="dadosFuncionario"),

    # -------------------------------------------------------------------------------------------------------------------

    # VENDAS

    path(f"cadVendas/", cadVendas.as_view(), name="cadVendas"),
    path(f"AdminListagemVenda/", CadListViewVenda.as_view(), name="AdminListagemVenda"),
    path(f"venda/Atualizar/-<int:pk>", VendaUpdateView.as_view(), name="venda_atualizar"),
    path(f"Admin/venda_deletar/-<int:pk>", VendaDeleteView.as_view(), name="venda_deletar"),
    path(f"Admin/buscar-venda/", ProcurarVenda.as_view(), name="procurarVenda"),
    path('Admin/buscar-Venda/dados/<int:dados_id>/', DadosCadastrosVenda.as_view(), name='dadosVenda'),
    path(f"btn-complete/venda/-<int:pk>", ValidarVendas.as_view(), name="venda_complete"),

    # login

    path('login/', log, name="log"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="registro"),
    path(f"redefinirSenha/", RedefinirSenha, name="redefinirSenha"),

    # csv

    path('export-csv-vendas/', views.salvar_csvVenda, name='salvarVenda'),

    path('export-csv-cliente/', views.salvar_csvClientes, name='salvarCliente'),

    # rank
    path('ranking/', Rank.as_view(), name='rank'),

    # homeFuncionario---------------------------------------------------

    # CLIENTE
    path("homeFuncionario", FuncionarioHome.as_view(), name="homeFuncionario"),
    path("cadClienteFuncionario", cadClienteFuncionario.as_view(), name="cadClienteFuncionario"),
    path(f"FuncionarioListagemCliente/", FuncionarioCadListView.as_view(), name="FuncionarioListagemCliente"),
    path(f"btn-complete/clienteFuncionario/-<int:pk>", ValidarClienteFuncionario.as_view(),
         name="cliente_completeFuncionario"),
    path(f"cliente/AtualizarFuncionario/-<int:pk>", ClienteUpdateViewFuncionario.as_view(),
         name="cliente_atualizarFuncionario"),
    path(f"Funcionario/cliente_deletar/-<int:pk>", ClienteDeleteViewFuncionario.as_view(),
         name="cliente_deletarFuncionario"),
    path(f"Funcionario/buscar-cliente/", ProcurarClienteFuncionario.as_view(), name="procurarClienteFuncionario"),
    path(f"Funcionario/buscar-cliente/dados/-<int:dados_id>", DadosCadastrosClienteFuncionario.as_view(),
         name="dadosClienteFuncionario"),

    # VENDAS

    path(f"cadVendasFuncionario/", cadVendasFuncionario.as_view(), name="cadVendasFuncionario"),
    path(f"FuncionarioListagemVenda/", CadListViewVendaFuncionario.as_view(), name="FuncionarioListagemVenda"),
    path(f"venda/AtualizarFuncionario/-<int:pk>", VendaUpdateViewFuncionario.as_view(),
         name="venda_atualizarFuncionario"),
    path(f"Funcionario/venda_deletar/-<int:pk>", VendaDeleteViewFuncionario.as_view(), name="venda_deletarFuncionario"),
    path(f"btn-complete/vendaFuncionario/-<int:pk>", ValidarVendasFuncionario.as_view(),
         name="venda_completeFuncionario"),
    path(f"Funcionario/buscar-venda/", ProcurarVendaFuncionario.as_view(), name="procurarVendaFuncionario"),
    path('Funcionario/buscar-Venda/dados/<int:dados_id>/', DadosCadastrosVendaFuncionario.as_view(),
         name='dadosVendaFuncionario'),

    path('api/cliente/<int:pk>/', views.cliente_detail_api, name='cliente_detail_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
