from django.urls import path
from .view import views

urlpatterns = [
    path("", views.log, name="log"),
    path('register/', views.RegisterView.as_view(), name="registro"),

    
]