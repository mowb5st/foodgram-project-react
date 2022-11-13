from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenDestroyView, UserViewSet
from rest_framework import status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins

from core.models import Ingredient, Recipe, Tag
from .filters import IngredientFilter, RecipeFilter
from .paginators import CustomPagination
from .permissions import IsAuthenticatedAndOwnerOrAdmin
from .serializers import (FavoriteSerializer, IngredientModelSerializer,
                          LoginSerializer, RecipeCreateSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, SubscriptionEventSerializer,
                          SubscriptionSerializer)

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticatedAndOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def favorite_shopping_cart_function(self, request, serializer_arg, *args,
                                        **kwargs):
        user = request.user
        serializer = serializer_arg(
            data={
                'user': user.id,
                'recipe': self.kwargs.get('id')
            },
            context={
                'request': request,
                'kwargs': kwargs
            }
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            serializer_saved_data = serializer.save()
            return Response(serializer_saved_data,
                            status=status.HTTP_201_CREATED)
        serializer.destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(methods=['GET'],
            detail=False,
            url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated]
            )
    def download_shopping_cart(self, request, *args, **kwargs):
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
        file_text = ([f"• {item} ({value['measurement_unit']}) — "
                      f"{value['amount']}\n"
                      for item, value in shopping_cart.items()])
        response = HttpResponse(file_text, 'Content-Type: text/plain')
        response['Content-Disposition'] = (
            f'attachment; '
            f'filename="{self.request.user.username} shopping cart.txt"'
        )
        return response

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='shopping_cart',
            url_name='shopping_carts',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        return self.favorite_shopping_cart_function(
            request, ShoppingCartSerializer, *args, **kwargs)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='favorite',
            url_name='favorites',
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        return self.favorite_shopping_cart_function(
            request, FavoriteSerializer, *args, **kwargs)


class TagViewSet(mixins.RetrieveModelMixin,
                 mixins.ListModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class SubscriptionViewSet(UserViewSet):

    @action(methods=['GET'],
            detail=False,
            serializer_class=SubscriptionSerializer,
            permission_classes=[IsAuthenticated],
            filter_backends=(DjangoFilterBackend,),
            pagination_class=CustomPagination
            )
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            User.objects.filter(following__user=self.request.user))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            url_path='subscribe',
            url_name='subscribes',
            serializer_class=SubscriptionEventSerializer,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data={'user': self.request.user.id,
                  'author': self.kwargs.get('id')},
            context={
                'request': request,
                'kwargs': kwargs}
        )
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            serializer_saved_data = serializer.save()
            return Response(serializer_saved_data,
                            status=status.HTTP_201_CREATED)
        serializer.destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
