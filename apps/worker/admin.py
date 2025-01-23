from django.contrib import admin
from .models import CustomUser_Funcionario

def deactivate_users(CustomUser_Funcionario, request, queryset):
    queryset.update(is_active=False)

deactivate_users.short_description = "Desativar usuários selecionados"

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = [deactivate_users]#exemplo de um uso 
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('username',)
    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('username', 'password', 'telefone', 'email')
        }),
        ('Permissões', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

admin.site.register(CustomUser_Funcionario, CustomUserAdmin)