from django.urls import path
from .view import views

from django.conf import settings
from django.conf.urls.static import static

#Waring alterar nomes e maiusculo no começo
urlpatterns = [
    #register
    path("login", views.log, name="log"),
    path("register/", views.RegisterView.as_view(), name="registro"),
    path(f"redefinirSenha/",  views.RedefinirSenha, name="redefinirSenha"),
    path("", views.Home.as_view(), name="home"),

    path("logout/",  views.LogoutView.as_view(), name="logout"),    
# ----------------------------------------------------------------------------------------------------
    #user views
    path(f"funcionario/Atualizar-Campos/-<int:pk>", views.UpdateView.as_view(), name="funcionario_atualizar"),
    #update views funcionario
    path(f"ListagemFuncionario/", views.ListFuncionario.as_view(), name="AdminListagemFuncionario"),

     #Buscas
    path(f"buscar-funcionario/", views.ProcurarFuncionario.as_view(), name="procurarFuncionario"),
    path(f"buscar-funcionario/dados/-<int:dados_id>", views.DadosFuncionario.as_view(),
         name="dadosFuncionario"),



             path('ranking/', views.Rank.as_view(), name='rank'),
 path("export-csv-vendas/<str:periodo>/", views.salvar_csvVenda, name="salvarVenda"),
    path(
        "export-csv-vendas/<str:periodo>/<str:forma_pagamento>/",
        views.salvar_csvVenda,
        name="salvarVendaPagamento",
    ),
    path(
        "export-csv-Cliente/<str:periodo>/",
        views.salvar_csvClientes,
        name="salvarCliente",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# as_vier() é um método que converte uma classe em uma view generica da Class-Based Views (CBVs),
'''
 path(f"AdminListagemFuncionario/", CadListViewFunc.as_view(), name="AdminListagemFuncionario"),
    path(f"funcionario/Atualizar/-<int:pk>", FuncionarioUpdateView.as_view(), name="funcionario_atualizar"),
    path(f"Admin/buscar-funcionario/", ProcurarFuncionario.as_view(), name="procurarFuncionario"),
    path(f"Admin/buscar-Funcionario/dados/-<int:dados_id>", DadosCadastrosFuncionario.as_view(),
         name="dadosFuncionario"),




          # csv
    path("export-csv-vendas/<str:periodo>/", views.salvar_csvVenda, name="salvarVenda"),
    path(
        "export-csv-vendas/<str:periodo>/<str:forma_pagamento>/",
        views.salvar_csvVenda,
        name="salvarVendaPagamento",
    ),
    path(
        "export-csv-Cliente/<str:periodo>/",
        views.salvar_csvClientes,
        name="salvarCliente",
    ),
'''