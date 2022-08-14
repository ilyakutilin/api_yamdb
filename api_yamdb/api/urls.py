from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, GenreViewSet, TitleViewSet

router = DefaultRouter()
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewViewSet, 'categories')
router.register('genres', GenreViewSet, basename='genres')


urlpatterns = [
    path('v1/', include('users.urls')),
    path('v1/', include(router.urls)),
]