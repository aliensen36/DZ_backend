from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from .serializers import UserSerializer
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


# Временная стартовая страница
def home(request):
    return render(request, 'home.html', {})


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'tg_id'

    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        tg_id = data.get('tg_id')

        user, created = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={
                'first_name': data.get('first_name', 'Unknown'),
                'last_name': data.get('last_name'),
                'username': data.get('username'),
                'is_bot': data.get('is_bot', False),
            }
        )

        if not created:
            changed = False
            for field in ['first_name', 'last_name', 'username']:
                if getattr(user, field) != data.get(field):
                    setattr(user, field, data.get(field))
                    changed = True
            if changed:
                user.save()

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, tg_id=None):
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, tg_id=None):
        try:
            user = User.objects.get(tg_id=tg_id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)