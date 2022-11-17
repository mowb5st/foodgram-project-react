import django_filters
from core.models import Ingredient, Recipe


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter()
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = django_filters.NumberFilter(method='get_favorite')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value == 1:
                return queryset.filter(favorite_recipe__user=user)
        return queryset.exclude(favorite_recipe__user=user)

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_anonymous:
            if value == 1:
                return queryset.filter(shopping_recipe__user=user)
        return queryset.exclude(shopping_recipe__user=user)


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='get_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def get_name(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
