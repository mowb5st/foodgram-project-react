from rest_framework import serializers
from users.models import User
from core.models import Recipe, Tag, Ingredient, Follow, Favorite
from django.shortcuts import get_object_or_404


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',)


class UserEventSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )


class UserSubSerializer(UserEventSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        # queryset = Recipe.objects.filter(author=obj.username)
        queryset = Recipe.objects.filter(author=obj.id)
        # request = self.context['request']
        serializer = RecipeSubSerializer(
            instance=queryset,
            many=True,
            # context={'request': request}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.id).count()
        # serializer = RecipeSubSerializer(
        #     queryset, many=True
        # )
        return queryset

    class Meta:
        model = User
        # fields = ('email', 'id')
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class MeUserSerializer(UserSerializer):
    pass


class SubscriptionSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()

    def get_author(self, obj):
        request = self.context['request']
        serializer = UserEventSerializer(
            obj.author,
            context={'request': request},
        )
        return serializer.data

    def get_recipes(self, obj):
        request = self.context['request']
        # print(request)
        serializer = RecipeSubSerializer(
            # obj.author,
            context={'request': request},
        )
        return serializer.data

    class Meta:
        model = Follow
        fields = ('author', 'recipes')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = serializers.StringRelatedField(many=True)
    tags = serializers.StringRelatedField(many=True)
    is_favorite = serializers.StringRelatedField(
        default='TODO')  # !TODO add is_favorite field
    is_in_shopping_card = serializers.StringRelatedField(
        default='TODO')  # !TODO add is_in_shopping_card field

    def get_author(self, obj):
        request = self.context['request']
        serializer = UserEventSerializer(
            obj.author,
            context={'request': request},
        )
        return serializer.data

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorite',
                  'is_in_shopping_card', 'name', 'image', 'text',
                  'cooking_time')


class RecipeSubSerializer(serializers.ModelSerializer):
    # id = name = image = cooking_time = serializers.StringRelatedField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time')
        # read_only_fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def save(self, **kwargs):
        ret = []
        request = self.context['request']
        # print(self.serializer_related_field)
        user = request.user
        recipe = Recipe.objects.get(id=kwargs['recipe'])
        # print(user, ':', recipe)
        # obj = Favorite.objects.create(user=user, recipe=recipe)
        queryset = Recipe.objects.filter(id=kwargs['recipe'])
        # request = self.context['request']
        serializer = RecipeSubSerializer(
            instance=queryset,
            many=True,
            context={'request': request}
        )
        ret.append(serializer.data)
        return ret
