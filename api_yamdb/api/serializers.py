from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import (Category, Comment, Genre, GenresTitles, Review,
                            Title)


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


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
    # TODO: ARTEM
    # Здесь стоит добавить поле rating, которое мы на лету посчитаем
    # при запросе к нашему view-сету. В таком случае в модели данное поле
    # не потребуется.

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
