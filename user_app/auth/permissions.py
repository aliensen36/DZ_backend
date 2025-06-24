from rest_framework.permissions import BasePermission
from django.conf import settings

from django.contrib.auth import get_user_model
User = get_user_model()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.DESIGN_ADMIN)

class IsResident(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.RESIDENT)

class IsBotAuthenticated(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get('X-Bot-Api-Key')
        print(f"Received X-Bot-Api-Key: {token}, Expected: {settings.BOT_API_KEY}")
        return token == settings.BOT_API_KEY