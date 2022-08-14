from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from review.models import Category, Genre, GenresTitles, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        read_only=True,
        slug_field='slug'
    )
    genre = GenreSerializer(many=True)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 
                  'description', 'genre', 'category')

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        category = validated_data.pop('category')
        title = Title.objects.create(**validated_data)

        for genre in genres:
            current_genre, status = Genre.objects.get_or_create(
                **genre)
            GenresTitles.objects.create(
                genre=current_genre, title=title)
                
        Title.objects.create(title=title, **category)
        return title
