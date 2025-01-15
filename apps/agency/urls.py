'''
from django.urls import path
from .view import cadAgencia, CadListViewAgencia, AgenciaUpdateView, AgenciaDeleteView, DadosCadastrosAgencia, ProcurarAgencia, pesquisar_rota
 

urlpatterns = [

   # AGENCIA
    path(f"cadAgencia/", cadAgencia.as_view(), name="cadAgencia"),
    path(f"ListagemAgencia/", CadListViewAgencia.as_view(), name="ListagemAgencia"),
    path(f"agencia_deletar/-<int:pk>", AgenciaDeleteView.as_view(), name="agencia_deletar"),
    path(f"agencia/Atualizar/-<int:pk>", AgenciaUpdateView.as_view(), name="agencia_atualizar"),

    # login
    path('Agencia/dados/<int:dados_id>/', DadosCadastrosAgencia.as_view(), name='dadosAgencia'),
    path(f"buscar-agencia/", ProcurarAgencia.as_view(), name="procurarAgencia"),
    path(f"pesquisar-rota/", pesquisar_rota, name="pesquisarRota"),

    # -------------------------------------------------------------------------------------------------------------------

]
'''