from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import action

from django.contrib.auth import get_user_model
from django.http import HttpResponse

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import UserReadSerializer, UserSubscriptionSerializer, TagsSerializer, \
    IngredientsSerializer, RecipesReadSerializer, \
    RecipesCreateSerializer, RecipesListSerializer, UserCreateSerializer
from .models import Tags, Ingredients, Favourites, Recipes, Follow, ShoppingCart
from .paginators import VariablePageSizePaginator
from .filters import RecipesFilter
from .permissions import IsOwnerOrAuthenticatedOrReadOnly

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
    permission_classes = [IsOwnerOrAuthenticatedOrReadOnly, ]

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return RecipesListSerializer
        return RecipesCreateSerializer

    def get_serializer_context(self):
        context = super(RecipesViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        return serializer.save()

    def perform_update(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        serializer = RecipesListSerializer(instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        serializer = RecipesListSerializer(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, ],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        recipes = list(request.user.shop_list.values_list('recipe', flat=True))
        data = {}
        for recipe in recipes:
            recipe_ingredients = list(recipe.recipe_ingredient)
            for recipe_ingredient in recipe_ingredients:
                if recipe_ingredient.ingredient.name in data:
                    data[recipe_ingredient.ingredient.name][0] += recipe_ingredient.amount
                else:
                    data[recipe_ingredient.ingredient.name] = (
                        recipe_ingredient.amount,
                        recipe_ingredient.ingredient.measurement_unit
                    )
        result = ''
        for key in data:
            result += f'{key} ({data[key][1]}) - {data[key][0]}\n'.capitalize()
        response = HttpResponse(result, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="Ingredients list"'
        return response

    @action(methods=['get', 'delete'], detail=True, permission_classes=[IsAuthenticated, ],
            url_path='favourite')
    def favourite(self, request):
        recipe = self.get_object()
        if request.method == 'GET':
            if Favourites.objects.get(user=request.user, recipe=recipe).exists():
                data = {
                    'errors': 'Рецепт уже в избранном!'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                Favourites.objects.create(user=request.user, recipe=recipe)
                serializer = RecipesReadSerializer(recipe)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if Favourites.objects.get(user=request.user, recipe=recipe).exists():
                Favourites.objects.get(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get', 'delete'], detail=True, permission_classes=[IsAuthenticated, ],
            url_path='shopping_cart')
    def shopping_cart(self, request):
        recipe = self.get_object()
        if request.method == 'GET':
            if ShoppingCart.objects.get(user=request.user, recipe=recipe).exists():
                data = {
                    'errors': 'Уже в списке покупок!'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                serializer = RecipesReadSerializer(recipe)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if ShoppingCart.objects.get(user=request.user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = VariablePageSizePaginator
    permission_classes = [IsAuthenticated, ]
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'delete']

    def get_serializer_context(self):
        context = super(UserViewSet, self).get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'GET':
            return UserReadSerializer
        return UserCreateSerializer

    def perform_create(self, serializer):
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data
        data['id'] = instance.id
        return Response(data=data, status=status.HTTP_201_CREATED, headers=headers)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, ],
            url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data)

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated, ],
            url_path='subscriptions')
    def subscriptions(self, request):
        queryset = self.request.user.follower.all().values_list('author', flat=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserSubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(page, many=True)
        return Response(serializer.data)

    @action(methods=['get', 'delete'], detail=True, permission_classes=[IsAuthenticated, ],
            url_path='subscribe')
    def subscribe(self, request):
        author = self.get_object()
        if request.method == 'GET':
            if Follow.objects.get(user=request.user, author=author).exists():
                data = {
                    'errors': 'Подписка уже существует!'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            else:
                Follow.objects.create(user=request.user, author=author)
                serializer = UserSubscriptionSerializer(author)
                data = serializer.data
                return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            if Follow.objects.get(user=request.user, author=author).exists():
                Follow.objects.get(user=request.user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                data = {
                    'errors': 'Вы не подписаны на этого пользователя!'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated, ],
            url_path='set_password')
    def set_password(self, request):
        if not request.data['new_password']:
            return Response(
                data={'new_password': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not request.data['current_password']:
            return Response(
                data={'current_password': 'Обязательное поле.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.data['new_password'] == request.data['current_password']:
            return Response(
                data={'error': "Поле 'new_password' и 'current_password' совпадают"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.check_password(request.data['new_password']):
            request.user.set_password(request.data['new_password'])
            request.user.save()
        return Response(data=request.data, status=status.HTTP_201_CREATED)
