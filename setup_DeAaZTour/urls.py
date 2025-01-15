from django.contrib import admin
from django.urls import path, include
from django.apps import *
#
urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("apps.worker.urls.py")),

]
