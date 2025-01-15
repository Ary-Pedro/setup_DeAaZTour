from django.urls import path
from .view import views

urlpatterns = [
    path("", views.log, name="log"),
    path('register/', views.RegisterView.as_view(), name="registro"),

    # csv
    path("export-csv-vendas/<str:periodo>/", views.salvar_csvVenda, name="salvarVenda"),
    path("export-csv-vendas/<str:periodo>/<str:forma_pagamento>/", views.salvar_csvVenda, name="salvarVendaPagamento"),
    path('export-csv-Cliente/<str:periodo>/', views.salvar_csvClientes, name='salvarCliente'),

]