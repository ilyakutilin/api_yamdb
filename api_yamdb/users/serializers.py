from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator

from .models import User
from .utils import check_confimation_code, get_jwt_token


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор данных для регистрации."""

    class Meta:
        model = User
        fields = ['email', 'username']

    validators = [
        UniqueTogetherValidator(
            message='Пользователь с таким email уже существует',
            queryset=User.objects.all(),
            fields=['email', 'username']
        )
    ]

    def validate_username(self, value):
        """Валидация имени пользователя."""
        if value == 'me':
            raise serializers.ValidationError(
                'Пожалуйста, не пытайтесь зарегистрировать пользователя '
                'с именем "me".')
        return value


class ObtainJWTTokenSerializer(serializers.Serializer):
    """Сериализатор данных для получения JWT токена."""
    username = serializers.CharField()
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        """Проверка кода подтверждения и получение JWT токена."""
        # В obj приходит OrderedDict с отправленным пользователем username.
        # Достаем его по ключу 'username'.
        username = obj['username']
        # Если пользователя с таким username не существует,
        # выбрасываем исключение со статусом 404.
        user_queryset = User.objects.filter(username=username)
        if not user_queryset.exists():
            raise NotFound(
                detail=f'Пользователя с именем {username} не существует'
            )
        # Получаем объект пользователя и код подтверждения.
        user = User.objects.get(username=username)
        confirmation_code = self.initial_data.get('confirmation_code')
        # Передаем их в функцию проверки кода подтверждения.
        # Если код неверный - вызываем ошибку валидации.
        if not check_confimation_code(
                user=user,
                confirmation_code=confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')
        # Передаем объект пользователя в функцию генерации JWT токена,
        # генерируем и возвращаем токен.
        return get_jwt_token(user=user)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для админских операций с пользователями."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio',
                  'role']
        lookup_field = 'username'


class ProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для операций со своим профилем.

    Поле "роль" доступно только для чтения.
    """

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'bio',
                  'role']
        read_only_fields = ['role']
