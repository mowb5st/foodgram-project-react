from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as __
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from core.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Subscription,
    Tag
)

User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def save(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        favorited = Favorite.objects.filter(user=user, recipe=recipe)
        if not favorited.exists():
            Favorite.objects.create(user=user, recipe=recipe)
            return self.to_representation(recipe)
        raise serializers.ValidationError('Рецепт уже в избранном')

    def destroy(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        favorited = Favorite.objects.filter(user=user, recipe=recipe)
        if favorited.exists:
            favorited.delete()
            return
        raise serializers.ValidationError('Рецепта нет в избранном')


class IngredientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=__("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=__("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=__("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            username = User.objects.get(email=email).username
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)
            if not user:
                msg = __('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = __('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


class Ingredient2RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = Ingredient2RecipeCreateSerializer(many=True)
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def add_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_obj = ingredient['id']
            amount = ingredient['amount']
            relation_obj, created = IngredientRecipe.objects.get_or_create(
                ingredient=ingredient_obj, amount=amount
            )
            if created:
                recipe.ingredients.add(created)
            else:
                recipe.ingredients.add(relation_obj)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.StringRelatedField(source='ingredient')
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserEventSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_card = serializers.SerializerMethodField()

    def get_author(self, obj):
        request = self.context['request']
        serializer = UserEventSerializer(
            obj.author,
            context={'request': request},
        )
        return serializer.data

    def get_ingredients(self, obj):
        request = self.context['request']
        serializer = IngredientSerializer(
            obj.ingredients,
            context={'request': request}
        )
        return serializer.data

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_card(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorite',
            'is_in_shopping_card', 'name', 'image', 'text', 'cooking_time'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def save(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if not shopping_cart.exists():
            ShoppingCart.objects.create(user=user, recipe=recipe)
            return self.to_representation(recipe)
        raise serializers.ValidationError('Рецепт уже в списке покупок')

    def destroy(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if shopping_cart.exists():
            shopping_cart.delete()
            return
        raise serializers.ValidationError('Рецепта нет в списке покупок')


class RecipeSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubPostSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.CharField(default=True)

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        serializer = RecipeSubSerializer(
            instance=queryset,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.id).count()
        return queryset

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def validate_self_subscription(self, user, author):
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться/отписаться на самого себя!')

    def save(self, user, author):
        if not Subscription.objects.filter(user=user, author=author).exists():
            Subscription.objects.create(user=user, author=author)
            return self.to_representation(author)
        raise serializers.ValidationError('Вы уже подписаны на этого автора')

    def destroy(self, user, author):
        subscription = Subscription.objects.filter(user=user, author=author)
        if subscription.exists():
            subscription.delete()
            return
        raise serializers.ValidationError('Вы не подписаны на данного автора')


class UserSubSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes(self, obj):
        queryset = Recipe.objects.filter(author=obj.id)
        serializer = RecipeSubSerializer(
            instance=queryset,
            many=True,
        )
        return serializer.data

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.id).count()
        return queryset

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )
