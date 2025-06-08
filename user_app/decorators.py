from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

def require_roles(roles):
    """
    Декоратор для проверки роли пользователя по JWT.
    Принимает список ролей, одной из которых должен обладать пользователь.
    
    Пример использования:
    @require_roles([User.Role.DESIGN_ADMIN, User.Role.RESIDENT])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(view, request, *args, **kwargs):
            from .views import verify_jwt
            
            payload = verify_jwt(request)
            if not payload:
                return Response({"error": "Invalid or missing token"}, 
                               status=status.HTTP_403_FORBIDDEN)
            
            user_role = payload.get('role')
            if user_role not in roles:
                return Response(
                    {"error": "Access denied. Insufficient permissions."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            return view_func(view, request, *args, **kwargs)
        return wrapped_view
    return decorator
