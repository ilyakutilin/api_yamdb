from rest_framework import serializers
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
        if not check_confimation_code(
                user=obj,
                confirmation_code=self.initial_data.get('confirmation_code')):
            raise serializers.ValidationError('Неверный код подтверждения')
        return get_jwt_token(user=obj)


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
