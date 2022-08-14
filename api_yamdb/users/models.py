from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
