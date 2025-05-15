from django.contrib import admin
from .models import Agencia


class AgenciaAdmin(admin.ModelAdmin):
    list_display = ("nome_contato", "nome_fantasia", "email1", "telefone1", "cnpj")
    search_fields = ("nome_contato", "nome_fantasia", "email1", "cnpj")
    list_filter = ("nome_contato", "contato_ano")
    ordering = ("id",)
    fieldsets = (
        (
            "Informações Da Agência",
            {"fields": ("nome_contato", "nome_fantasia", "email1", "telefone1")},
        ),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas Importantes", {"fields": ("contato_ano",)}),
    )


admin.site.register(Agencia, AgenciaAdmin)
