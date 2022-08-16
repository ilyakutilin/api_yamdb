from datetime import datetime
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    year = models.IntegerField(
        verbose_name='Год производства',
        validators=[MaxValueValidator(datetime.now().year)],)
    rating = models.FloatField(verbose_name='Рейтинг', null=True)
    # TODO: ARTEM->ALEXEY
    # Нам необходимо рассчитывать рейтинг на момент запроса и самое удачное
    # место для этого view с использованием annotate(). В таком подходе нам
    # не потребуется хранить в БД текущий рейтинг.
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

    def update_rating(self):
        # TODO: ARTEM->ALEXEY
        # См. замечание из view-функции.
        reviews = Review.objects.filter(title=self.pk)
        rating = reviews.aggregate(Avg('score'))
        self.rating = round(rating['score__avg'], 2)
        self.save()

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
    GRADE = [
        # TODO: ALEXEY
        # Правильный ход мысли, но в Django для этого есть более правильный
        # инструмент. Здесь стоит воспользоваться валидаторами на уровне модели
        # Для этого необходимо в поле модели указать атрибут validators
        # и добавить следующее валидаторы:
        # MinValueValidator
        # https://django.fun/docs/django/ru/4.0/ref/validators/#minvaluevalidator
        # MaXValueValidator
        # https://django.fun/docs/django/ru/4.0/ref/validators/#maxvaluevalidator
        # В самих валидаторах первым аргументом указать значение минимальное
        # или максимальное соответственно. Также вторым аргументом валидатор
        # принимает текст, который будет отображен, если значение будет
        # выходить за границы.
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    ]
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
    score = models.IntegerField(
        # TODO: ALEXEY
        # См. замечание про PositiveSmallIntegerField. Стоит проверить и
        # в остальных полях, если им не нужно хранить числа больших размеров,
        # то стоит придерживаться такого подхода.
        verbose_name='Оценка',
        choices=GRADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        # TODO: ALEXEY
        # Нарушен порядок внутренних классов и стандартных методов.
        # https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/#model-style
        return f'Отзыв {self.author} на {self.title.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                # TODO: ALEXEY
                # Зеленый комментарий :)
                # Отлично! Добавили constraints.
                name='review_author_title_is_unique',
                fields=['author', 'title']
            )
        ]
        ordering = ['pub_date']
        verbose_name = 'Обзор'


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
        verbose_name = 'Комментарий'


@receiver(post_save, sender=Review)
def update_rating(sender, instance, created, **kwargs):
    # TODO: ALEXEY
    # # Зеленый комментарий :)
    # За реализацию такого подхода однозначно можно похвалить.
    instance.title.update_rating()
    # TODO: ALEXEY
    # Но в данном методе не будет необходимости, в комментарии модели и
    # view-функции указал более подробно почему.
