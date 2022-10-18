from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CHOICES = {}


class Ingredient(models.Model):
    title = models.CharField("Ingredient's title", max_length=200)
    amount = models.IntegerField("Amount of ingredients")
    measurement_unit = models.CharField("Units", max_length=20)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField("Tag's title", max_length=50)
    color = models.CharField("Tag's HEX color", max_length=8)
    slug = models.SlugField(
        unique=True,
        verbose_name='URL')

    def __str__(self):
        return self.title


class Recipe(models.Model):
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes'
                               )
    title = models.CharField("Recipe's Title",
                             max_length=200)
    image = models.ImageField("Recipe's Image",
                              upload_to='core/'
                              )
    text = models.TextField("Recipe's text")
    ingredient = models.ManyToManyField(Ingredient,
                                        # on_delete=models.CASCADE,
                                        related_name='ingredients')
    tag = models.ManyToManyField(Tag,
                                 related_name='tags',
                                 # on_delete=models.CASCADE
                                 )

    def __str__(self):
        return self.title

# class IngredientToRecipe(models.Model):
#     recipe = models.ForeignKey(Recipe,
#                                related_name='Recipe of ingredient',
#                                verbose_name='ingredient2recipe_following',
#                                on_delete=models.CASCADE)
#     ingredient = models.ForeignKey(Ingredient,
#                                    related_name='Ingredient',
#                                    verbose_name='ingredient2recipe_follower',
#                                    on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f'{self.recipe}, {self.ingredient}'


# class TagToRecipe(models.Model):
#     recipe = models.ForeignKey(Recipe,
#                                # related_name='Recipe of tag',
#                                verbose_name='tag2recipe_following',
#                                on_delete=models.CASCADE)
#     tag = models.ForeignKey(Tag,
#                             # related_name='Tag of recipe',
#                             verbose_name='tag2recipe_follower',
#                             on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f'{self.recipe}, {self.tag}'
