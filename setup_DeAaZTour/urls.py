from django.contrib import admin
from django.urls import path, include
from django.apps import *
#
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("apps.worker.urls.py")),
    path("", include("apps.agency.urls.py")),
    path("", include("apps.client.urls.py")),
    path("", include("apps.service.urls.py")),
]
