from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from reviews.models import Category, Comment, Genre, Review, Title

from .filter import TitleFilter
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          SaveTitleSerializer, TitleSerializer)


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
        # TODO: ALEXEY
        # Здесь будет уместнее использовать get_object_or_404().
        # Нам не потребуется как-то явно обрабатывать ситуации, когда данные,
        # которые запрошены, не окажутся в БД.
        if not title.exists():
            raise NotFound(
                detail=f'Произведения с номером {title_id} не существует'
            )
        review = Review.objects.filter(
            # TODO: ALEXEY
            # Логику валидации необходимо реализовывать в сериализаторе.
            title=title[0], author=self.request.user
        )
        if review.exists():
            raise ValidationError(
                detail='Отзыв на произведение уже существует',
            )
        serializer.save(author=self.request.user, title=title[0])
        # TODO: ALEXEY
        # После того, как мы перейдем на использование get_object_or_404(),
        # то нам не придется лишний раз указывать индексы для работы с объектом


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        new_queryset = Comment.objects.filter(review=review_id)
        return new_queryset

    def perform_create(self, serializer):
        # TODO: ALEXEY
        # Валидация по всех view-функциях должна переехать в сериализатор.
        # Как правило ее располагают именно там и у сериализатора есть
        # специальные методы для валидирования полей.
        title_id = self.kwargs.get('title_id')
        title = Title.objects.filter(pk=title_id)
        # TODO: ALEXEY
        # См. замечания про get_object_or_404().
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
        # TODO: ALEXEY
        # См. замечания про индексы.


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
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
