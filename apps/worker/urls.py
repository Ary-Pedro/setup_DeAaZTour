from django.urls import path
from .view import views

from django.conf import settings
from django.conf.urls.static import static

#Waring alterar nomes e maiusculo no começo
urlpatterns = [
    #register
    path("acesso", views.log, name="log"),
    path("registro/", views.RegisterView.as_view(), name="registro"),
    path(f"redefinirSenha/",  views.RedefinirSenha, name="redefinirSenha"),
    path("", views.Home.as_view(), name="home"),

    path("sair/",  views.LogoutView.as_view(), name="logout"),    
# ----------------------------------------------------------------------------------------------------
    #user views
    path(f"funcionario/atualizar/<int:pk>", views.UpdateView.as_view(), name="funcionario_atualizar"),
    path(f"funcionario/<int:pk>", views.Desligar.as_view(), name="desligar_funcionario"),
    path(f"funcionario/atualizar-Perfil/<int:pk>/", views.AtualizarPerfil.as_view(), name="atualizar_perfil"),
    path(f"funcionario/listagem/", views.ListFuncionario.as_view(), name="ListagemFuncionario"),

     #Buscas
    path(f"funcionario/buscar/", views.Procurar.as_view(), name="procurarFuncionario"),
    path(f"funcionario/buscar/dados/-<int:dados_id>", views.Dados.as_view(),
         name="dadosFuncionario"),



    path('adm/ranking/', views.Rank.as_view(), name='rank'),
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


    path('exportar-fluxo-concluido/<int:fluxo_id>/', views.salvar_csvFluxoConcluido, name='exportarFluxoConcluido'),

    path(f"fluxoMensal/", views.contas.as_view() , name="contas"),
    path('resetar-contas/', views.resetar_contas, name='resetar_contas'),
    path("concluir_fluxo/", views.concluir_fluxo_mensal, name="concluir_fluxo"),
    path("fluxos/", views.ListarFluxosMensais.as_view(), name="listagemFluxoMensal"),
    path('fluxo-completo/<int:pk>/', views.DetalhesFluxoMensalCompleto.as_view(), name='fluxo_completo'),  
    path('fluxo/deletar-conta/<int:pk>/', views.deletar_conta_mensal, name='deletar_conta_mensal'),   

  
  



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# as_vier() é um método que converte uma classe em uma view generica da Class-Based Views (CBVs),
'''
 path(f"ListagemFuncionario/", CadListViewFunc.as_view(), name="ListagemFuncionario"),
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