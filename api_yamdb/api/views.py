from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from reviews.models import Category, Comment, Genre, Review, Title

from .filter import TitleFilter
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitleSaveSerializer, TitleSerializer)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsOwnerOrAdminOrReadOnly, )

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        new_queryset = Review.objects.filter(title=title_id)
        # TODO: ALEXEY
        # Здесь стоит использовать get_object_or_404(), чтобы функция сразу
        # выбросила 404, а мы не делали другие действия, а только потом
        # выбрасывали.
        # title=title_id -  конструкция рабочая, но не самая лучшая.
        # Изначально Django ожидает, что мы ему дадим объект, а мы даем ID.
        # Оно работает, потому что в базе хранятся именно ID объектов,
        # а не сами объекты. Здесь лучше всегда явно через двойное
        # подчеркивание указывать поле, которое нам необходимо.
        # Пример:
        # title__<имя_поля_из_модели>=<значение>
        # (Поля pk, id как правило всегда присутствуют по умолчанию)
        # В остальных местах в работе рекомендовал бы перейти на такой же
        # способ, где это необходимо. Если мы сравниваем с ID, то значит стоит
        # указать явно, что сравниваем с полем ID через двойной подчеркивание.
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
        # TODO: ALEXEY
        # Здесь стоит использовать `get_object_or_404()
        # Также стоит проверить, что это ревью на верный title_id.
        # Иными словами надо добавить еще одно условие с проверкой на title_id.
        return new_queryset

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    # TODO: ALEXEY
    # Кстати, мы можем отсортировать данные по этому полю, которое создали
    # в annotate. Можно посмотреть в сторону ordering_fields.
    # https://www.django-rest-framework.org/api-guide/filtering/#specifying-which-fields-may-be-ordered-against
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleSaveSerializer


class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    # TODO: ARTEM
    # Сейчас у нас два класса, в которых мы вынуждены дублировать наследников.
    # Давай заведем абстрактный класс и будем наследоваться от него.
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
