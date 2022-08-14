from rest_framework import filters, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.pagination import LimitOffsetPagination

from review.models import Category, Genre, Title, Comment, Review

from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import (CategorySerializer, GenreSerializer, TitleSerializer,
                          CommentSerizlizer, ReviewSerializer)

from django_filters.rest_framework import DjangoFilterBackend


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination

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
        serializer.save(author=self.request.user, title=title[0])


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerizlizer
    permission_classes = [IsOwnerOrAdminOrReadOnly, ]
    pagination_class = LimitOffsetPagination

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
        review = Review.objects.filter(review=review_id)
        if not review.exists():
            raise NotFound(
                detail=(f'Отзыва с номером {review_id}'
                        f'к произведению {title[0].name} не существует')
            )
        serializer.save(author=self.request.user, review=review[0])


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
