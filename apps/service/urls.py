from django.urls import path
from .view import views

urlpatterns = [
    # VENDAS
    path(f"cadastrar/", views.CadVendas.as_view(), name="cadVendas"),
    path(f"Listagem/", views.ListVenda.as_view(), name="ListagemVenda"),
    path(f"atualizar/-<int:pk>", views.UpdateView.as_view(), name="venda_atualizar"),
    path(f"deletar/-<int:pk>", views.DeleteView.as_view(), name="venda_deletar"),
    path(f"buscar/", views.Procurar.as_view(), name="procurarVenda"),
    path(
        "buscar/dados/<int:dados_id>/",
        views.DadosCadastros.as_view(),
        name="dadosVenda",
    ),
    path(
        f"btn-complete/venda/-<int:pk>", views.Validar.as_view(), name="venda_complete"
    ),
    path("excluir-anexo/<int:anexo_id>/", views.excluir_anexo, name="excluir_anexo"),
    # -------------------------------------------------------------------------------------------------------------------
]
