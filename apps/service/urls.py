"""
from django.urls import path
from .view import cadVendas, CadListViewVenda, VendaUpdateView, VendaDeleteView, ProcurarVenda, DadosCadastrosVenda, ValidarVendas

urlpatterns = [

    # VENDAS

    path(f"cadVendas/", cadVendas.as_view(), name="cadVendas"),
    path(f"AdminListagemVenda/", CadListViewVenda.as_view(), name="AdminListagemVenda"),
    path(f"venda/Atualizar/-<int:pk>", VendaUpdateView.as_view(), name="venda_atualizar"),
    path(f"Admin/venda_deletar/-<int:pk>", VendaDeleteView.as_view(), name="venda_deletar"),
    path(f"Admin/buscar-venda/", ProcurarVenda.as_view(), name="procurarVenda"),
    path('Admin/buscar-Venda/dados/<int:dados_id>/', DadosCadastrosVenda.as_view(), name='dadosVenda'),
    path(f"btn-complete/venda/-<int:pk>", ValidarVendas.as_view(), name="venda_complete"),

    # -------------------------------------------------------------------------------------------------------------------

]
"""
