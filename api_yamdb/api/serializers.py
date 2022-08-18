from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title


class CurrentTitleDefault:
    # TODO: ALEXEY
    # Целый класс для одноразового использования? Не слишком практично.
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
    # TODO: ALEXEY
    # Данное поле можно убрать из сериализатора.

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        validators = [
            # TODO: ALEXEY
            # Сейчас:
            # 1. Создаем дополнительный класс.
            # 2. Дополнительное поле в сериализаторе.
            # 3. Вызов валидатора UniqueTogetherValidator.
            # Но здесь достаточно вызывать validate или validate_<field_name>
            # и проверить, наличие объекта в базе с помощью exists()
            # и бросить ошибку. См. замечание из CommentSerializer
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author')
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
        # TODO: ALEXEY
        # get_object_or_404 уместнее использовать во view-функции.
        # Здесь стоит явно проверить, например, с помощью вызова exists()
        # наличие объекта в базе и тогда уже бросать ошибку
        # serializers.ValidationError.
        # https://www.django-rest-framework.org/api-guide/exceptions/#validationerror
        return data


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSaveSerializer(serializers.ModelSerializer):
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


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')
