from django.urls import path
from .view import cadCliente, CadListView, ValidarCliente, ClienteUpdateView, ClienteDeleteView, ProcurarCliente, DadosCadastrosCliente, cliente_detail_api
from .view import views

urlpatterns = [

    # CLIENTE
    path("cadCliente", cadCliente.as_view(), name="cadCliente"),
    path(f"AdminListagemCliente/", CadListView.as_view(), name="AdminListagemCliente"),
    path(f"btn-complete/Cliente/-<int:pk>", ValidarCliente.as_view(), name="cliente_complete"),
    path(f"Cliente/Atualizar/-<int:pk>", ClienteUpdateView.as_view(), name="cliente_atualizar"),
    path(f"Admin/cliente_deletar/-<int:pk>", ClienteDeleteView.as_view(), name="cliente_deletar"),
    path(f"Admin/buscar-Cliente/", ProcurarCliente.as_view(), name="procurarCliente"),
    path(f"Admin/buscar-Cliente/dados/-<int:dados_id>", DadosCadastrosCliente.as_view(), name="dadosCliente"),
    path('api/cliente/<int:pk>/', views.cliente_detail_api, name='cliente_detail_api'),

    # -------------------------------------------------------------------------------------------------------------------
]
