from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
#
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.worker.urls")),
    path("agencia/", include("apps.agency.urls")),
    path("cliente/", include("apps.client.urls")),
    path("venda/", include("apps.service.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)