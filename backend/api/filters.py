from django_filters import rest_framework as filters

from .models import Recipes


class RecipesFilter(filters.FilterSet):

    # TODO: проверить, работает ли это шиза
    def filter_is_favorited(self, queryset, name, value):
        ids = list(self.request.user.user_favorites.values_list('recipe__id', flat=True))
        if value == 1:
            return queryset.filter(id__in=ids)
        elif value == 0:
            return queryset.exclude(id__in=ids)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        ids = list(self.request.user.shop_list.values_list('recipe__id', flat=True))
        if value == 1:
            return queryset.filter(id__in=ids)
        elif value == 0:
            return queryset.exclude(id__in=ids)

    is_favorited = filters.NumberFilter(method=filter_is_favorited)
    is_in_shopping_cart = filters.NumberFilter(method=filter_is_in_shopping_cart)

    class Meta:
        model = Recipes
        fields = ['author__id', 'tags__slug']
