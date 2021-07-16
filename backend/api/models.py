from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()


class Ingredients(models.Model):
    name = models.CharField(blank=False, null=False, max_length=200, unique=True)
    measurement_unit = models.CharField(blank=False, null=False, max_length=200)


class Tags(models.Model):
    name = models.CharField(blank=False, null=False, max_length=200)
    colour = models.CharField(blank=False, null=True, max_length=100)
    slug = models.SlugField(validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')], blank=False, null=True)


class Recipes(models.Model):
    author = models.ForeignKey(User, blank=False, null=False, related_name='recipes', on_delete=models.SET_NULL)
    name = models.CharField(blank=False, null=False, max_length=200)
    image = models.ImageField(upload_to='recipes/images/', blank=False, null=False)
    text = models.TextField(blank=False, null=False)
    tags = models.ManyToManyField(Tags, blank=False, null=False, related_name='recipes')
    cooking_time = models.PositiveIntegerField(validators=[MinValueValidator(1)], blank=False, null=False)
    pub_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-pub_date']


class RecipeIngredients(models.Model):
    key = models.BigAutoField(primary_key=True)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='recipe_ingredient', blank=False,
                               null=False)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, related_name='recipe_ingredient',
                                   blank=False, null=False)
    amount = models.IntegerField(blank=False, null=False)


class Favourites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user_favorites', blank=False, null=False)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='favorited_by', blank=False, null=False)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower', blank=False, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following', blank=False, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_user_author')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='shop_list', blank=False, null=False)
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE,
                               related_name='buyer', blank=False, null=False)
