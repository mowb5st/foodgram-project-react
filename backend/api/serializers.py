from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Recipe, Tag, Ingredient, Follow, Favorite, \
    IngredientRecipe
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as __
from django.contrib.auth import authenticate, get_user_model
from drf_base64.fields import Base64ImageField

User = get_user_model()


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
        # for model = IngredientRecipe ::: fields will be: id, amount, ingredient with int values
        model = IngredientRecipe
        fields = (
            # '__all__'
            'id',
            'name',
            'measurement_unit',
            'amount',
            # 'ingredient'
        )


class Ingredient2RecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorite = serializers.StringRelatedField(
        default='TODO')  # !TODO add is_favorite field
    is_in_shopping_card = serializers.StringRelatedField(
        default='TODO')  # !TODO add is_in_shopping_card field

    def get_ingredients(self, obj):
        request = self.context['request']
        serializer = IngredientSerializer(
            obj.ingredients,
            context={'request': request}
        )
        return serializer.data

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
        # lookup_field = 'id'


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = Ingredient2RecipeCreateSerializer(many=True)
    image = Base64ImageField(use_url=True)

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text',
                  'cooking_time')

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
                # recipe_last = Recipe.objects.get(id=recipe.id).ingredients.add(relation_obj)
                # return recipe_last
                recipe.ingredients.add(relation_obj)

    def create(self, validated_data):
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.add_tags(tags, recipe)
        self.add_ingredients(ingredients, recipe)
        return recipe


class RecipeSubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')

    def save(self, **kwargs):
        user = self.context['request'].user
        recipe = Recipe.objects.get(id=kwargs['recipe'])
        Favorite.objects.create(user=user, recipe=recipe)


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


# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = '__all__'
