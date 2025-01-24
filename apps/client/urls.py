from django.urls import path
from .view import views

urlpatterns = [

    # CLIENTE
    path("cadCliente", views.cadCliente.as_view(), name="cadCliente"),
    path(f"AdminListagemCliente/", views.CadListView.as_view(), name="AdminListagemCliente"),
    path(f"btn-complete/Cliente/-<int:pk>", views.ValidarCliente.as_view(), name="cliente_complete"),
    path(f"Cliente/Atualizar/-<int:pk>", views.ClienteUpdateView.as_view(), name="cliente_atualizar"),
    path(f"Admin/cliente_deletar/-<int:pk>", views.ClienteDeleteView.as_view(), name="cliente_deletar"),
    path(f"Admin/buscar-Cliente/", views.ProcurarCliente.as_view(), name="procurarCliente"),
    path(f"Admin/buscar-Cliente/dados/-<int:dados_id>", views.DadosCadastrosCliente.as_view(), name="dadosCliente"),
    path('api/cliente/<int:pk>/', views.cliente_detail_api, name='cliente_detail_api'),

    # -------------------------------------------------------------------------------------------------------------------
]
