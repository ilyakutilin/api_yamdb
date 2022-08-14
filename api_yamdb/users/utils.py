from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


def generate_and_send_confrimation_code(user, data):
    """Генерация кода подтверждения и его отправка.

    Используется при регистрации пользователя (signup).
    Генерирует код подтверждения и отправляет на e-mail адрес пользователя.
    """
    token = default_token_generator.make_token(user)
    send_mail(
        subject='Confirmation code',
        message=token,
        from_email=None,
        recipient_list=[data.get('email')]
    )


def check_confimation_code(user, confirmation_code):
    """Проверка кода подтверждения."""
    return default_token_generator.check_token(user, confirmation_code)


def get_jwt_token(user):
    """Получение JWT токена для пользователя."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)
