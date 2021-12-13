from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth import get_user_model

User = get_user_model()

User.USERNAME_FIELD = 'email'
User.REQUIRED_FIELDS = ('username', )


class Ingredient(models.Model):
    name = models.CharField(
        blank=False,
        null=False,
        max_length=200,
        unique=True,
        verbose_name='Name'
    )
    measurement_unit = models.CharField(
        blank=False,
        null=False,
        max_length=200,
        verbose_name='Measurement unit'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'


class Tag(models.Model):
    name = models.CharField(
        blank=False,
        null=False,
        max_length=200,
        unique=True,
        verbose_name='Name'
    )
    colour = models.CharField(
        blank=False,
        null=False,
        max_length=100,
        unique=True,
        verbose_name='Colour'
    )
    slug = models.SlugField(
        validators=[RegexValidator(regex='^[-a-zA-Z0-9_]+$')],
        blank=False,
        null=False,
        unique=True,
        verbose_name='Slug'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Author'
    )
    name = models.CharField(
        blank=False,
        null=False,
        max_length=200,
        verbose_name='Name'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        blank=False,
        null=False,
        verbose_name='Image'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Text'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes',
        verbose_name='Tags'
    )
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        blank=False,
        null=False,
        verbose_name='Cooking time'
    )
    pub_date = models.DateTimeField(
        auto_now=True,
        verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

        ordering = ['-pub_date']


class RecipeIngredient(models.Model):
    key = models.BigAutoField(
        primary_key=True,
        verbose_name='id'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        blank=False,
        null=False,
        verbose_name='Recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        blank=False,
        null=False,
        verbose_name='Ingredient'
    )
    amount = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='Ingredient amount'
    )

    class Meta:
        verbose_name = 'Recipe-Ingredient relation'
        verbose_name_plural = 'Recipes-Ingredients relations'


class Favourite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        blank=False,
        null=False,
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        blank=False,
        null=False,
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Adding to favourites'
        verbose_name_plural = 'Addings to favourites'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=False,
        null=False,
        verbose_name='User'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=False,
        null=False,
        verbose_name='Author'
    )

    class Meta:
        verbose_name = 'Adding to subscriptions'
        verbose_name_plural = 'Addings to subscriptions'

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_list',
        blank=False,
        null=False,
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='buyer',
        blank=False,
        null=False,
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Shopping cart element'
        verbose_name_plural = 'Shopping cart elements'
