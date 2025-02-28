from django.urls import path
from .view import views

urlpatterns = [

    # CLIENTE
    path("cadastrar", views.CadCliente.as_view(), name="cadCliente"),
    path(f"Listagem", views.ListCliente.as_view(), name="ListagemCliente"),
    
    path(f"Atualizar/-<int:pk>", views.UpdateView.as_view(), name="cliente_atualizar"),
    path(f"Deletar/-<int:pk>", views.DeleteView.as_view(), name="cliente_deletar"),
    path(f"buscar/", views.Procurar.as_view(), name="procurarCliente"),
    path(f"buscar/dados/-<int:dados_id>", views.DadosCadastros.as_view(), name="dadosCliente"),
    path('api/cliente/<int:pk>/', views.cliente_detail_api, name='cliente_detail_api'),
    #remover

    path(f"btn-complete/cliente/-<int:pk>", views.Validar.as_view(), name="cliente_complete"),

    path('excluir-anexo/<int:anexo_id>/', views.excluir_anexo, name='excluir_anexo'),

    # -------------------------------------------------------------------------------------------------------------------
]
