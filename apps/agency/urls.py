from django.urls import path
from .view import views
 

urlpatterns = [

   # AGENCIA
    path(f"cadastrar/", views.CadAgencia.as_view(), name="Agencia"),
    path(f"listagem/", views.ListAgencia.as_view(), name="ListagemAgencia"),


    path(f"deletar/-<int:pk>", views.DeleteView.as_view(), name="agencia_deletar"),
    path(f"atualizar/-<int:pk>", views.UpdateView.as_view(), name="agencia_atualizar"),
    
    
    path('buscar/dados/<int:dados_id>/', views.DadosCadastros.as_view(), name='dadosAgencia'),
    path(f"buscar/", views.Procurar.as_view(), name="procurarAgencia"),
    path(f"pesquisar-rota/", views.Pesquisar_rota, name="pesquisarRota"),

    # -------------------------------------------------------------------------------------------------------------------

]
