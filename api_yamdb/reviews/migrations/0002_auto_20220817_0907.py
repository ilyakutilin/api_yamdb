# Generated by Django 2.2.16 on 2022-08-17 09:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['id'], 'verbose_name': 'Категория'},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ['id'], 'verbose_name': 'Жанр'},
        ),
        migrations.AlterModelOptions(
            name='genrestitles',
            options={'verbose_name': 'Жанры произведений'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['pub_date'], 'verbose_name': 'Обзор'},
        ),
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ['-year'], 'verbose_name': 'Произведение'},
        ),
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Наименование категория'),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=128, verbose_name='Наименование жанра'),
        ),
        migrations.AlterField(
            model_name='review',
            name='score',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, 'Оценка не может быть меньше единицы (1)'), django.core.validators.MaxValueValidator(10, 'Оценка не может быть больше десяти (10)')], verbose_name='Оценка'),
        ),
        migrations.AlterField(
            model_name='title',
            name='genre',
            field=models.ManyToManyField(null=True, through='reviews.GenresTitles', to='reviews.Genre', verbose_name='Жанр'),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(2022)], verbose_name='Год производства'),
        ),
    ]
