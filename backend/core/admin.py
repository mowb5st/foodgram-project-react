from django.contrib import admin

from .models import Ingredient, Tag, Recipe, Subscription, Favorite, \
    IngredientRecipe, ShoppingCart


class IngredientAdmin(admin.ModelAdmin):
    pass


class TagAdmin(admin.ModelAdmin):
    pass


class RecipeAdmin(admin.ModelAdmin):
    pass


class FollowAdmin(admin.ModelAdmin):
    pass


class FavoriteAdmin(admin.ModelAdmin):
    pass

class Ingredient2RecipeAdmin(admin.ModelAdmin):
    pass


class ShoppingCartAdmin(admin.ModelAdmin):
    pass


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscription, FollowAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(IngredientRecipe, Ingredient2RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)

