from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import (Category, Comment, Genre, GenresTitles, Review,
                            Title)
from rest_framework.validators import UniqueTogetherValidator


class CurrentTitleDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get('view').kwargs.get('title_id')


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=CurrentTitleDefault())

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')

    def validate(self, data):
        title_id = self.context['request'].parser_context['kwargs'].get(
            'title_id')
        get_object_or_404(Title, pk=title_id)
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        # TODO: ARTEM
        # Нам нужно исключить только поле id, поэтому это можно сделать
        # и с помощью exclude.


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class SaveTitleSerializer(serializers.ModelSerializer):
    # TODO: ARTEM
    # Имя сериализатора всегда лучше начинать с имени модели.
    category = SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
    )
    genre = SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')

    def create(self, validated_data):
        # TODO: ARTEM
        # В этом нет необходимости. Мы уже указали, поле genre с атрибутом
        # many=True . Django понимает, что здесь может быть список объектов,
        # а не один.
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genres:
            GenresTitles.objects.create(
                genre=genre, title=title)
        return title

    def to_representation(self, instance):
        return TitleSerializer().to_representation(instance)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)
    # TODO: ARTEM
    # Здесь стоит добавить поле rating, которое мы на лету посчитаем
    # при запросе к нашему view-сету. В таком случае в модели данное поле
    # не потребуется.

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
