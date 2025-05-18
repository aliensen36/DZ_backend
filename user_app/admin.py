from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('tg_id', 'username', 'first_name', 'is_superuser')
    search_fields = ('tg_id', 'username')
    ordering = ('tg_id',)

    fieldsets = None
    add_fieldsets = None

    fields = (
        'tg_id', 'username', 'first_name', 'last_name',
        'is_bot', 'last_activity', 'date_joined',
        'is_staff', 'is_active', 'is_superuser',
        'groups', 'user_permissions', 'password',
    )

    readonly_fields = ('last_activity', 'date_joined')