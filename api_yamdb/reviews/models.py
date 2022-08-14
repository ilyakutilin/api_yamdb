from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Жанр',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        unique=True
    )


class Category(models.Model):
    name = models.CharField(
        verbose_name='Категория',
        max_length=128
    )
    slug = models.SlugField(
        verbose_name='Слаг категории',
        unique=True
    )


class Title(models.Model):
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256
    )
    year = models.IntegerField(verbose_name='Год производства')
    rating = models.FloatField(verbose_name='Рейтинг', null=True)
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

    # Уточнить с группой!
    genre = models.ManyToManyField(
        Genre,
        through='GenresTitles'
    )

    def update_rating(self):
        reviews = Review.objects.filter(title=self.pk)
        rating = reviews.aggregate(Avg('score'))
        self.rating = round(rating['score__avg'], 2)
        self.save()


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
    GRADE = [
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
        verbose_name='Оценка',
        choices=GRADE,
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    def __str__(self):
        return f'Отзыв {self.author} на {self.title.name}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='review_author_title_is_unique',
                fields=['author', 'title']
            )
        ]
        ordering = ['pub_date']


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


@receiver(post_save, sender=Review)
def update_rating(sender, instance, created, **kwargs):
    instance.title.update_rating()
