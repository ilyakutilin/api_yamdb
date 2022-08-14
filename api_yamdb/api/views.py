from rest_framework import filters, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from reviews.models import Category, Genre, Title, Comment, Review

from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          CommentSerializer, ReviewSerializer, SaveTitleSerializer)

from django_filters.rest_framework import DjangoFilterBackend


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = Review.objects.filter(title=title_id)
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = Title.objects.filter(pk=title_id)
        if not title.exists():
            raise NotFound(
                detail=f'Произведения с номером {title_id} не существует'
            )
        review = Review.objects.filter(
            title=title[0], author=self.request.user
        )
        if review.exists():
            raise ValidationError(
                detail=f'Отзыв на произведение уже существует',
            )
        serializer.save(author=self.request.user, title=title[0])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        new_queryset = Comment.objects.filter(review=review_id)
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = Title.objects.filter(pk=title_id)
        if not title.exists():
            raise NotFound(
                detail=f'Произведения с номером {title_id} не существует'
            )
        review_id = self.kwargs.get('review_id')
        review = Review.objects.filter(pk=review_id)
        if not review.exists():
            raise NotFound(
                detail=(f'Отзыва с номером {review_id}'
                        f'к произведению {title[0].name} не существует')
            )
        serializer.save(author=self.request.user, review=review[0])


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')

    def get_serializer_class(self): 
        if self.request.method in ['POST', 'PATCH']: 
            return SaveTitleSerializer
        return TitleSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)

    @action(detail=False, methods=['delete',], url_path=r'(?P<slug>[-\w]+)')
    def delete_by_slug(self, request, slug):
        category = Category.objects.filter(slug=slug)
        if not category.exists():
            raise NotFound(
                detail=(f'Категории со слагом - {slug} несуществует')
            )
        category[0].delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)

    @action(detail=False, methods=['delete',], url_path=r'(?P<slug>[-\w]+)')
    def delete_by_slug(self, request, slug):
        genre = Genre.objects.filter(slug=slug)
        if not genre.exists():
            raise NotFound(
                detail=(f'Жанра со слагом - {slug} несуществует')
            )
        genre[0].delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

