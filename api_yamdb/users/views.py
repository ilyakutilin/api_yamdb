from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import IsAdmin
from .serializers import (ObtainJWTTokenSerializer, ProfileSerializer,
                          SignUpSerializer, UserSerializer)
from .utils import generate_and_send_confrimation_code


class SignUpAPIView(APIView):
    """Регистрация нового пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        """Создание пользователя и отправка кода подтверждения."""
        serializer = SignUpSerializer(data=self.request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Используем функцию генерации и отправки кода подтверждения.
            # Функции передаем объект пользователя и данные,
            # полученные от сериализатора.
            generate_and_send_confrimation_code(
                user=user,
                data=serializer.data
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTTokenAPIView(APIView):
    """Получение JWT токена для пользователя."""
    permission_classes = (AllowAny,)

    def post(self, request):
        """POST-запрос на получение JWT-токена."""
        serializer = ObtainJWTTokenSerializer(data=self.request.data)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """Операции с пользователями.

    Создание пользователей, обновление информации о пользователях,
    получение информации о конкретном пользователе
    или получение спика пользователей.
    Операции доступны только администраторам.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'

    @action(
        methods=('get', 'patch'),
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request, *args, **kwargs):
        """Доступ пользователя к своему профилю.

        Профиль доступен любому аутентифицированному пользователю.
        Метод запроса GET - получение информации о себе.
        Метод запроса PATCH - обновление полей своего профиля.
        Обновление роли недоступно.
        Роль может быть обновлена администратором через users/<username>.
        """
        self.object = User.objects.get(username=self.request.user.username)
        if request.method == 'PATCH':
            serializer = ProfileSerializer(
                self.object,
                data=self.request.data,
                context={'request_user': self.request.user},
                partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ProfileSerializer(self.object)
        return Response(serializer.data)
