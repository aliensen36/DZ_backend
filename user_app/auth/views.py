import json
import logging
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .permissions import IsAdmin, IsResident
from .serializers import CustomTokenObtainPairSerializer
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

from django.contrib.auth import get_user_model
User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="init_data",
                type=str,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Telegram initData for authentication",
            )
        ],
        responses={200: CustomTokenObtainPairSerializer},
        description="Obtain JWT access and refresh tokens using Telegram initData",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



class CustomTokenRefreshView(TokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        description="Refresh JWT access token using refresh token",
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

# Для тестирования эндпоинта
class ProtectedView(APIView):
    # Наследуется CustomJWTAuthentication и IsAuthenticated из settings.py

    @extend_schema(
        description="Access protected endpoint for authenticated users",
    )
    def get(self, request):
        return Response({
            'message': 'This is a protected endpoint',
            'user_id': request.user.tg_id,
            'role': request.user.role
        })


# Для пользователей с ролью `design_admin`
class AdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(
        description="Access admin-only endpoint for design_admin role",
    )
    def get(self, request):
        return Response({
            'message': 'This is a design_admin-only endpoint',
            'user_id': request.user.tg_id
        })


# Для пользователей с ролью `resident`
class ResidentView(APIView):
    permission_classes = [IsAuthenticated, IsResident]

    @extend_schema(
        description="Access resident-only endpoint",
    )
    def get(self, request):
        return Response({
            'message': 'This is a resident-only endpoint',
            'user_id': request.user.tg_id
        })
