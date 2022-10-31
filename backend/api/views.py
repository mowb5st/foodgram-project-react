from datetime import datetime

from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenDestroyView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.authtoken.models import Token
from rest_framework.authtoken import views

from users.models import User
from core.models import Recipe, Tag, Ingredient, Subscription, Favorite, \
    ShoppingCart, IngredientRecipe
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer, \
    SubscriptionSerializer, UserSubSerializer, FavoriteSerializer, \
    RecipeSubSerializer, LoginSerializer, \
    RecipeCreateSerializer, TagSerializer, IngredientModelSerializer, \
    SubscriptionModelSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated
import traceback

from django.http import FileResponse, HttpResponse
from rest_framework import viewsets, renderers
from rest_framework.decorators import action

USERNAME_ME = 'me'


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet
                  ):
    queryset = User.objects.all()
    lookup_field = 'id'

    # permission_classes = IsAuthenticated

    def get_object(self):
        if self.kwargs.get('id') == USERNAME_ME:
            return self.request.user
        return super().get_object()

    def get_serializer_class(self):
        if self.kwargs.get('username') == USERNAME_ME:
            return MeUserSerializer
        return UserSerializer


class SubscriptionViewSet(ModelViewSet):
    serializer_class = UserSubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        followings = User.objects.filter(following__user=self.request.user)
        return followings

    def create(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        user = get_object_or_404(User, pk=user_id)
        sub = Subscription.objects.create(user=self.request.user,
                                          author=user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        user = get_object_or_404(User, pk=user_id)
        Subscription.objects.get(user=self.request.user,
                                 author=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()

    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('id',)
    # lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer
        if self.action == 'create':
            return RecipeCreateSerializer


class FavoriteViewSet(ModelViewSet):
    # queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(views.ObtainAuthToken):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'auth_token': token.key, },
                        status=status.HTTP_201_CREATED)


class LogoutViewSet(TokenDestroyView):
    permission_classes = [IsAuthenticated]


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    lookup_field = 'id'


class ShoppingCartViewSet(ModelViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            shopping_cart = {}
            ingredients = Recipe.objects.filter(
                shopping_recipe__user=request.user
            ).values_list(
                'ingredients__ingredient__name',
                'ingredients__ingredient__measurement_unit'
            ).annotate(amount=Sum('ingredients__amount'))
            for name, measurement_unit, amount in ingredients:
                if name not in shopping_cart:
                    shopping_cart[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
            file_text = ([f"> {item}: {value['amount']}"
                          f"{value['measurement_unit']}\n"
                          for item, value in shopping_cart.items()])
            response = HttpResponse(file_text, 'Content-Type: text/plain')
            response['Content-Disposition'] = (
                f'attachment; '
                f'filename="{self.request.user.username} shopping cart.txt"'
            )
            return response
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = self.get_serializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response({'errors': str(err)},
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)
