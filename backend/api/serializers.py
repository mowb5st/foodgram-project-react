from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy
from djoser.serializers import UserCreateSerializer
from drf_base64.fields import Base64ImageField
from rest_framework import serializers

from core.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                         ShoppingCart, Subscription, Tag)

User = get_user_model()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, attrs):
        initial_data = self.initial_data
        user = initial_data.get('user')
        kwargs = initial_data.get('kwargs')
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        favorited = Favorite.objects.filter(user=user, recipe=recipe)
        if initial_data.get('method') == 'POST':
            if favorited.exists():
                raise serializers.ValidationError('Рецепт уже в избранном')
        else:
            if not favorited.exists():
                raise serializers.ValidationError('Рецепта нет в избранном')
        return attrs

    def save(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        Favorite.objects.create(user=user, recipe=recipe)
        return self.to_representation(recipe)

    def destroy(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        Favorite.objects.filter(user=user, recipe=recipe).delete()


class IngredientModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=gettext_lazy("email"),
        write_only=True
    )
    password = serializers.CharField(
        label=gettext_lazy("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=gettext_lazy("Token"),
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
                msg = gettext_lazy(
                    'Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = gettext_lazy('Must include "email" and "password".')
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
    image = Base64ImageField(use_url=False)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, attrs):
        unique_ingredients = []
        ingredients = attrs.get('ingredients')
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id not in unique_ingredients:
                unique_ingredients.append(ingredient_id)
            else:
                raise serializers.ValidationError(
                    f'Нельзя дублировать ингредиент: '
                    f'({ingredient_id})')
        return attrs

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

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        super().update(instance, validated_data)
        instance.tags.set(tags)
        self.add_ingredients(ingredients, instance)
        return instance


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

    def validate(self, attrs):
        initial_data = self.initial_data
        user = initial_data.get('user')
        kwargs = initial_data.get('kwargs')
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if initial_data.get('method') == 'POST':
            if shopping_cart.exists():
                raise serializers.ValidationError(
                    'Рецепт уже в списке покупок')
        else:
            if not shopping_cart.exists():
                raise serializers.ValidationError(
                    'Рецепта нет в списке покупок')
        return attrs

    def save(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        ShoppingCart.objects.create(user=user, recipe=recipe)
        return self.to_representation(recipe)

    def destroy(self, user, **kwargs):
        recipe = Recipe.objects.get(id=kwargs.get('id'))
        ShoppingCart.objects.filter(user=user, recipe=recipe).delete()


class RecipeSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubPostSerializer(serializers.ModelSerializer):
    recipes = RecipeSubSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.CharField(default=True)

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

    def validate(self, attrs):
        # В attr содержится информация только из поля is_subscribed:
        # OrderedDict([('is_subscribed', True)])
        # По этому данные вытаскиваю из self.initial_data
        initial_data = self.initial_data
        user = initial_data.get('user')
        author = initial_data.get('author')
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться/отписаться на самого себя!')

        subscription = Subscription.objects.filter(user=user,
                                                   author=author)
        if initial_data.get('method') == 'POST':
            if subscription.exists():
                raise serializers.ValidationError(
                    'Вы уже подписаны на этого автора')
        else:
            if not subscription.exists():
                raise serializers.ValidationError(
                    'Вы не подписаны на данного автора')
        return attrs

    def save(self, user, author):
        Subscription.objects.create(user=user, author=author)
        return self.to_representation(author)

    def destroy(self, user, author):
        Subscription.objects.filter(user=user, author=author).delete()


class UserSubSerializer(serializers.ModelSerializer):
    recipes = RecipeSubSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def get_recipes_count(self, obj):
        queryset = Recipe.objects.filter(author=obj.id).count()
        return queryset

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )


class UserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }
