from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecipesViewSet, TagsViewSet, IngredientsViewSet, UserViewSet

v1_router = DefaultRouter()
v1_router.register('recipes', RecipesViewSet, basename='recipes')
v1_router.register('tags', TagsViewSet, basename='tags')
v1_router.register('ingredients', IngredientsViewSet, basename='ingredients')
v1_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken'))
]
