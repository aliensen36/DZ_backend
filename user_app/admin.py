from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('tg_id', 'tg_username', 'first_name', 'last_name', 'is_staff')
    search_fields = ('tg_id', 'tg_username', 'first_name', 'last_name')
    ordering = ('tg_id',)

    fieldsets = (
        (None, {'fields': ('tg_id', 'tg_username', 'first_name', 'last_name', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('tg_id', 'tg_username', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')}
        ),
    )
