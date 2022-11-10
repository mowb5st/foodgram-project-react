import django_filters

from core.models import Recipe, Tag, Ingredient


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
