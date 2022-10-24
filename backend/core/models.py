from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

CHOICES = {}


class Ingredient(models.Model):
    name = models.CharField('Name', max_length=200)
    measurement_unit = models.CharField("Measurement unit", max_length=20)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Ingredient2Recipe(models.Model):
    # модель рецепта связывается с этой моделью, а эта модель связывается с
    # ингредиетом
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name="Recipe's ingredient")
    amount = models.IntegerField("Amount of ingredients")

    def __str__(self):
        return f'{self.ingredient}, {self.amount}'


class Tag(models.Model):
    name = models.CharField('Name', max_length=50)
    color = models.CharField('HEX color', max_length=8)
    slug = models.SlugField('URL', unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        "Recipe's Title",
        max_length=200)
    image = models.ImageField(
        "Recipe's Image",
        upload_to='media/recipes/'
    )
    text = models.TextField(
        "Recipe's text", max_length=2000)
    ingredients = models.ManyToManyField(
        Ingredient2Recipe,
        # on_delete=models.CASCADE,
        related_name='ingredients',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='tags',
        # on_delete=models.CASCADE
    )
    cooking_time = models.IntegerField('Cooking time')
    pub_date = models.DateTimeField('Publication date', auto_now_add=True)

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        help_text='Пользователь, который подписывается',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='На кого подписался',
        related_name='following',
        help_text='Пользователь, на которого подписываются',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'subsription'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_following')
        ]

    def __str__(self):
        return f'{self.user}, {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorite_user',
        help_text='Пользователь, который подписывается',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='На кого подписался',
        related_name='favorite_recipe',
        help_text='Рецепт, добавляемый в избранное',
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = 'favorites'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]

    def __str__(self):
        return f'{self.user}, {self.recipe}'
