from django.urls import path
from .view import views
 

urlpatterns = [

   # AGENCIA
    path(f"cadastrarAgencia/", views.AgenciaCadview.as_view(), name="Agencia"),
    path(f"agencia/ListagemAgencia/", views.AgenciaListView.as_view(), name="ListagemAgencia"),


    path(f"agenciaDeletar/-<int:pk>", views.AgenciaDeleteView.as_view(), name="agencia_deletar"),
    path(f"Atualizar-Campos/-<int:pk>", views.AgenciaUpdateView.as_view(), name="agencia_atualizar"),
    
    
    path('buscar-agencia/dados/<int:dados_id>/', views.DadosCadastrosAgencia.as_view(), name='dadosAgencia'),
    path(f"buscar-agencia/", views.ProcurarAgencia.as_view(), name="procurarAgencia"),
    path(f"pesquisar-rota/", views.pesquisar_rota, name="pesquisarRota"),

    # -------------------------------------------------------------------------------------------------------------------

]
