from django.contrib import admin
from django.urls import path, include

#
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.worker.urls")),
    path("agencia/", include("apps.agency.urls")),
    path("cliente/", include("apps.client.urls")),
    path("venda/", include("apps.service.urls")),
]
