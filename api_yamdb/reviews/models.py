from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from .validators import year_validator

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Наименование жанра',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Жанр'


class Category(models.Model):
    name = models.CharField(
        verbose_name='Наименование категория',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Категория'


class Title(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256
    )
    year = models.PositiveSmallIntegerField(
        verbose_name='Год производства',
        validators=(year_validator,)
    )
    description = models.CharField(
        verbose_name='Описание',
        max_length=2048
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='categories',
        verbose_name='Категория',
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenresTitles',
        through_fields=('title', 'genre'),
        null=True,
        verbose_name='Жанр',
    )

    class Meta:
        ordering = ['-year']
        verbose_name = 'Произведение'


class GenresTitles(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='genres',
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Жанры произведений'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.CharField(
        verbose_name='Текст отзыва',
        max_length=2048
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше единицы (1)'),
            MaxValueValidator(10, 'Оценка не может быть больше десяти (10)')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='review_author_title_is_unique',
                fields=('author', 'title')
            )
        ]
        ordering = ['pub_date']
        verbose_name = 'Обзор'

    def __str__(self):
        return f'Отзыв {self.author} на {self.title.name}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.CharField(
        verbose_name='Комментарий',
        max_length=2048
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['pub_date']
