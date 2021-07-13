from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view, action
from django.core.mail import send_mail

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import UserReadSerializer, TagsSerializer, IngredientsSerializer, RecipesReadSerializer, \
    RecipesCreateSerializer, RecipesListSerializer
from .models import Tags, Ingredients, Favourites, Recipes, Follow, ShoppingCart
from .paginators import VariablePageSizePaginator
from .filters import RecipesFilter

User = get_user_model()


class TagsViewSet(viewsets.ModelViewSet):
    serializer_class = TagsSerializer
    queryset = Tags.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', ]


class IngredientsViewSet(viewsets.ModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    lookup_field = 'id'
    http_method_names = ['get', ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipes.objects.all()
    lookup_field = 'id'
    pagination_class = VariablePageSizePaginator
    http_method_names = ['get', 'post', 'put', 'delete']
    filterset_class = RecipesFilter
    # TODO: добавить permissions

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data

        if request.user:
            for element in data:
                element['author']['is_subscribed'] = Follow.objects.get(
                    user=request.user,
                    author__id=element['author']['id']
                ).exists()

                element['is_favorited'] = Favourites.objects.get(
                    user=request.user,
                    recipe__id=element['id']
                ).exists()

                element['is_in_shopping_cart'] = ShoppingCart.objects.get(
                    user=request.user,
                    recipe__id=element['id']
                ).exists()
        else:
            for element in data:
                element['author']['is_subscribed'] = False
                element['is_favorited'] = False
                element['is_in_shopping_cart'] = False

        return Response(data=data)

    def perform_create(self, serializer):
        recipe = serializer.save()
        tags = Tags.objects.filter(
            id__in=self.request.data.get('tags')
        )
        recipe.tags = tags
        recipe.author = self.request.user
        return recipe.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = RecipesListSerializer(recipe).data
        data['author']['is_subscribed'] = Follow.objects.get(
            user=request.user,
            author__id=data['author']['id']
        ).exists()

        data['is_favorited'] = Favourites.objects.get(
            user=request.user,
            recipe__id=data['id']
        ).exists()

        data['is_in_shopping_cart'] = ShoppingCart.objects.get(
            user=request.user,
            recipe__id=data['id']
        ).exists()
        return Response(data=data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        recipe = self.perform_create(serializer)
        data = RecipesListSerializer(recipe).data
        data['author']['is_subscribed'] = Follow.objects.get(
            user=request.user,
            author__id=data['author']['id']
        ).exists()

        data['is_favorited'] = Favourites.objects.get(
            user=request.user,
            recipe__id=data['id']
        ).exists()

        data['is_in_shopping_cart'] = ShoppingCart.objects.get(
            user=request.user,
            recipe__id=data['id']
        ).exists()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(data)


class FavouriteViewSet(generics.RetrieveDestroyAPIView):
    serializer_class = RecipesReadSerializer
    queryset = Recipes.objects.all()
    http_method_names = ['get', 'delete']
    lookup_field = None
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        recipe = self.get_object()
        if Favourites.objects.get(user=request.user, recipe=recipe).exists():
            data = {
                'errors': 'Рецепт уже в избранном!'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            Favourites.objects.create(user=request.user, recipe=recipe)
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if Favourites.objects.get(user=request.user, recipe=recipe).exists():
            Favourites.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FollowViewSet(generics.RetrieveDestroyAPIView):
    serializer_class = UserReadSerializer
    queryset = User.objects.all()
    http_method_names = ['get', 'delete']
    lookup_field = None
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        author = self.get_object()
        if Follow.objects.get(user=request.user, author=author).exists():
            data = {
                'errors': 'Подписка уже существует!'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            Follow.objects.create(user=request.user, author=author)
            recipes_limit = request.GET.get('recipes_limit')
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            data = serializer.data
            recipes = instance.recipes.order_by('-pub_date')[:recipes_limit]
            recipes_serializer = RecipesReadSerializer(data=recipes, many=True)
            data['recipes'] = recipes_serializer.data
            data['recipes_count'] = recipes.count()
            data['is_subscribed'] = True
            return Response(data=data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        author = self.get_object()
        if Follow.objects.get(user=request.user, author=author).exists():
            Follow.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(generics.RetrieveDestroyAPIView):
    serializer_class = RecipesReadSerializer
    queryset = Recipes.objects.all()
    http_method_names = ['get', 'delete']
    lookup_field = None
    lookup_url_kwarg = 'id'
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        recipe = self.get_object()
        if ShoppingCart.objects.get(user=request.user, recipe=recipe).exists():
            data = {
                'errors': 'Уже в списке покупок!'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        else:
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = self.get_object()
        if ShoppingCart.objects.get(user=request.user, recipe=recipe).exists():
            ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
