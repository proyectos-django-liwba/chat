from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets =(
        ('Cuenta verificada', {'fields': ('is_verified', 'otp')}),
        ('Informacion Personal', {'fields': ('first_name', 'last_name','email', 'role', 'avatar')}),	
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
