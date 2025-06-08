from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('tg_id', 'username', 'first_name', 'last_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('tg_id', 'username', 'first_name', 'last_name')
    ordering = ('tg_id',)

    # Определяем fieldsets для страницы редактирования
    fieldsets = (
        (None, {'fields': ('tg_id', 'username', 'first_name', 'last_name', 'role')}),
        ('Персональная информация', {'fields': ('user_first_name', 'user_last_name', 
                                               'birth_date', 'email', 'phone_number')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_activity', 'date_joined')}),
        ('Прочее', {'fields': ('is_bot', 'password')}),
    )
    
    # Определяем add_fieldsets для страницы создания
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('tg_id', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('last_activity', 'date_joined')