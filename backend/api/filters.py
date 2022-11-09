import django_filters
from django_filters import ModelMultipleChoiceFilter

from core.models import Recipe, Tag, Ingredient


# from django_filters.rest_framework import FilterSet, NumberFilter, CharFilter, \
#     BooleanFilter




# class RecipeFilterSet(FilterSet):
#     """Класс фильтрации рецептов."""
#     author = NumberFilter(field_name='author__id')
#     tags = CharFilter(field_name='tags__slug')
#     is_favorited = NumberFilter(method='filter_is_favorited')
#
#     def filter_is_favorited(self, queryset, name, value):
#         if value == 1:
#             return queryset.filter(favorite_recipe__user=self.request.user)
#         elif value == 0:
#             return queryset.exclude(favorite_recipe__user=self.request.user)
#
#     class Meta:
#         model = Recipe
#         fields = ('author', 'tags', 'is_favorite',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.CharFilter()
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name='slug'
    )
    is_favorite = django_filters.NumberFilter(method='get_favorite')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if not user.is_anonymous:
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
    name = django_filters.CharFilter()

    class Meta:
        model = Ingredient
        fields = ('name',)
