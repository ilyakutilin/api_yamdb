from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # TODO: ILYA
    # Чтобы было удобно работать с ролями пользователя, необходимо реализовать
    # в модели User свойства, который будут выполнять данные проверки.
    # Например:
    # @property
    # def is_<роль_пользователя>(self):
    #     return self.role == User.<роль_пользователя>
    # Далее в любом месте работая с объектом модели User можно будет выполнить
    # проверку вызовом данного свойства.
    """Кастомная модель пользователя."""
    ROLE_CHOICES = [
        ('user', 'user'),
        ('moderator', 'moderator'),
        ('admin', 'admin'),
    ]
    email = models.EmailField(unique=True)
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=9,
        # TODO: ILYA
        # А если добавится роль длиннее слова moderator?
        # Давай сделаем здесь небольшой запас в длине.
        choices=ROLE_CHOICES,
        default='user'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='users_user_unique_relationships',
                fields=['email', 'username'],
            ),
        ]
        ordering = ['id']
