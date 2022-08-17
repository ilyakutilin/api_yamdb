from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title

from .filter import TitleFilter
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SaveTitleSerializer, TitleSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly, )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = Review.objects.filter(title=title_id)
        return new_queryset

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly, )

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        new_queryset = Comment.objects.filter(review=review_id)
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    # TODO: ARTEM
    # Стоит добавить возможность подсчета оценки для отзыва. можно сделать
    # проще. После вызова функции all() вызвать метод annotate() совместно с
    # Avg. Таким образом мы сможем подсчитать рейтинг.
    # https://django.fun/docs/django/ru/4.0/ref/models/querysets/#annotate
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    # TODO: ARTEM
    # Не стоит смешивать массивы и списки. Рекомендую определиться с подходом,
    # какой будет использоваться в проекте и придерживаться его.
    # Для неизменяемых последовательностей предпочтительнее будет использовать
    # массив.
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            # TODO: ARTEM
            # В парадигме view-сетов корректнее проверять на self.action.
            # В данном случае это будет: list и retrieve.
            return SaveTitleSerializer
        return TitleSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    # TODO: ARTEM
    # Здесь стоит придерживаться общего подхода работы с view-сетами и
    # реализовать данный класс, как и ему подобные. В данном случае нам
    # не требуется реализовывать @action. А чтобы была возможность указать
    # slug в урл, то стоит посмотреть в сторону поля lookup_field.
    # https://django.fun/docs/django-rest-framework/ru/3.12/api-guide/generic-views/#attributes
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)

    @action(detail=False, methods=['delete'], url_path=r'(?P<slug>[-\w]+)')
    def delete_by_slug(self, request, slug):
        # TODO: ARTEM
        # Все эту работу возьмет на себя джанго.
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

    @action(detail=False, methods=['delete'], url_path=r'(?P<slug>[-\w]+)')
    # TODO: ARTEM
    # См. замечания про lookup_field.
    def delete_by_slug(self, request, slug):
        genre = Genre.objects.filter(slug=slug)
        if not genre.exists():
            raise NotFound(
                detail=(f'Жанра со слагом - {slug} несуществует')
            )
        genre[0].delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
