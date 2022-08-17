from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        # TODO: ARTEM
        # Будет уместно также добавить и verbose_name для всех моделей.
        verbose_name='Жанр',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        unique=True
    )

    class Meta:
        ordering = ['id']


class Category(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        unique=True
    )

    class Meta:
        ordering = ['id']


class Title(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256
    )
    year = models.IntegerField(verbose_name='Год производства')
    # TODO: ARTEM
    # Стоит добавить валидацию. А может ли год быть больше текущего?
    # Также здесь будет уместнее использовать PositiveSmallIntegerField
    # для небольших чисел.
    # https://django.fun/docs/django/ru/4.0/ref/models/fields/#positivesmallintegerfield
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
        # TODO: ARTEM
        # Здесь уместно будет добавить атрибут through_fields.
        # В которым мы укажем поля сквозной модели, т.е title и genre.
        # https://www.django-rest-framework.org/api-guide/relations/#manytomanyfields-with-a-through-model
        Genre,
        through='GenresTitles'
    )

    class Meta:
        ordering = ['-year']


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
                fields=['author', 'title']
            )
        ]
        ordering = ['pub_date']

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
