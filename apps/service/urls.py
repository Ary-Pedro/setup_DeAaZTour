from django.urls import path
from .view import views

urlpatterns = [

    # VENDAS

    path(f"cadVendas/", views.cadVendas.as_view(), name="cadVendas"),
    path(f"AdminListagemVenda/", views.CadListViewVenda.as_view(), name="AdminListagemVenda"),
    path(f"venda/Atualizar/-<int:pk>", views.VendaUpdateView.as_view(), name="venda_atualizar"),
    path(f"Admin/venda_deletar/-<int:pk>", views.VendaDeleteView.as_view(), name="venda_deletar"),
    path(f"Admin/buscar-venda/", views.ProcurarVenda.as_view(), name="procurarVenda"),
    path('Admin/buscar-Venda/dados/<int:dados_id>/', views.DadosCadastrosVenda.as_view(), name='dadosVenda'),
    path(f"btn-complete/venda/-<int:pk>", views.ValidarVendas.as_view(), name="venda_complete"),

    # -------------------------------------------------------------------------------------------------------------------

]

