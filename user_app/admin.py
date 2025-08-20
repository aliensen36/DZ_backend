from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.http import HttpResponseRedirect

from .models import Referral, ReferralSettings

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('tg_id', 'username', 'role')
    list_display_links = ('tg_id', 'username', 'role')
    list_filter = ('tg_id', 'username', 'role')
    search_fields = ('tg_id', 'username', 'role')
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


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('inviter', 'invitee', 'is_rewarded', 'created_at')
    list_filter = ('is_rewarded',)
    search_fields = ('inviter__username', 'invitee__username', 'referral_code')
    fields = ('inviter', 'invitee', 'referral_code', 'is_rewarded', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(ReferralSettings)
class ReferralSettingsAdmin(admin.ModelAdmin):
    list_display = ('inviter_points', 'invitee_points')
    list_display_links = ('inviter_points', 'invitee_points')
    list_filter = ('inviter_points', 'invitee_points')
    search_fields = ('inviter_points', 'invitee_points')

    def has_add_permission(self, request):
        '''Разрешить добавление только если записи нет'''
        return not ReferralSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        '''Запретить удаление'''
        return False

    def changelist_view(self, request, extra_context=None):
        '''Если запись существует — редирект на редактирование'''
        obj = ReferralSettings.objects.first()
        if obj:
            return HttpResponseRedirect(reverse('admin:user_app_referralsettings_change', args=(obj.id,)))
        return super().changelist_view(request, extra_context)
