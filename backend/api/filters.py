from django_filters import rest_framework as filters

from .models import Recipe, Ingredient


class RecipesFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.CharFilter(
        field_name='tags__slug',
        lookup_expr='exact'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        ids = list(
            self.request.user.user_favorites.values_list(
                'recipe__id',
                flat=True
            )
        )
        if value:
            return queryset.filter(id__in=ids)
        else:
            return queryset.exclude(id__in=ids)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if not self.request.user.is_authenticated:
            return queryset
        ids = list(
            self.request.user.shop_list.values_list(
                'recipe__id',
                flat=True
            )
        )
        if value:
            return queryset.filter(id__in=ids)
        else:
            return queryset.exclude(id__in=ids)


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        lookup_expr='startswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name', ]
