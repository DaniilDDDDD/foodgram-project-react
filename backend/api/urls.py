from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipesViewSet, TagsViewSet, IngredientsViewSet, FavouriteViewSet, FollowViewSet, ShoppingCartViewSet

v1_router = DefaultRouter()
v1_router.register('recipes', RecipesViewSet, basename='recipes')
v1_router.register('tags', TagsViewSet, basename='tags')
v1_router.register('ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register(
    r'recipes/(?P<id>\d+)/favourite',
    FavouriteViewSet,
    basename='favourite'
)
v1_router.register(
    r'users/(?P<id>\d+)/subscribe',
    FollowViewSet,
    basename='follow'
)
v1_router.register(
    r'recipes/(?P<id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping'
)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('users/', include('djoser.urls'))
]
