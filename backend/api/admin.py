from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Ingredient, Tag, RecipeIngredient,
    Recipe, Follow, Favourite, ShoppingCart
)

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    empty_value_display = '-пусто-'
    list_filter = ('email', 'username')
    search_fields = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'name', 'image', 'text', 'tags_string',
        'cooking_time', 'pub_date', 'count_in_favourites'
    )
    empty_value_display = '-пусто-'
    list_filter = ('name', 'author', 'tags__slug',)
    search_fields = ('name', 'author__username', 'tags__slug',)

    def count_in_favourites(self, obj):
        return obj.favorited_by.all().count()

    count_in_favourites.short_description = 'times added to favourites'

    def tags_string(self, obj):
        return list(obj.tags.all().values_list('slug', flat=True))

    tags_string.short_description = 'tags'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    empty_value_display = '-пусто-'
    list_filter = ('name',)
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'colour', 'slug')
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('key', 'recipe', 'ingredient', 'amount')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


class FavouritesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    empty_value_display = '-пусто-'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favourite, FavouritesAdmin)
