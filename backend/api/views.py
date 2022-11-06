from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import TokenDestroyView, UserViewSet
from rest_framework import status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins

from core.models import (
    Recipe, Tag, Ingredient, Subscription, Favorite,
    ShoppingCart
)
from .filters import RecipeFilter
from .permissions import IsAuthenticatedOrOwnerOrAdmin
from .serializers import (
    UserSerializer, MeUserSerializer, RecipeSerializer, UserSubSerializer,
    FavoriteSerializer, LoginSerializer, RecipeCreateSerializer, TagSerializer,
    IngredientModelSerializer, SubscriptionSerializer, UserSubPostSerializer,
    ShoppingCartSerializer)

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticatedOrOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == ('list' or 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart',
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response(
                {
                    "detail": "Учетные данные не были предоставлены."
                },
                status=status.HTTP_401_UNAUTHORIZED)
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
            file_text = ([f"• {item} ({value['measurement_unit']}) — "
                          f"{value['amount']}\n"
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

    @action(methods=['POST', 'DELETE'], detail=True,
            url_path='shopping_cart', url_name='shopping_carts',
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        try:
            serializer = ShoppingCartSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user
            if self.request.method == 'POST':
                serializer_data = serializer.save(user=user, **kwargs)
                return Response(serializer_data,
                                status=status.HTTP_201_CREATED)
            # else only one available method DELETE
            serializer.destroy(user=user, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite',
            url_name='favorites', permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        try:
            serializer = FavoriteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = request.user
            if self.request.method == 'POST':
                serializer_data = serializer.save(user=user, **kwargs)

                return Response(serializer_data,
                                status=status.HTTP_201_CREATED)
            # else only one available method DELETE
            serializer.destroy(user=user, **kwargs)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          GenericViewSet):
    serializer_class = UserSubSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        followings = User.objects.filter(following__user=self.request.user)
        return followings

    @action(methods=['GET'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='subscribe',
            url_name='subscribes')
    def subscribe(self, request, *args, **kwargs):
        # try:
        user_id = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=user_id)
        requester = self.request.user
        if user == requester:
            return Response({'errors:': 'Нельзя подписаться на самого себя!'})
        if self.request.method == 'POST':
            serializer = UserSubPostSerializer(user)
            Subscription.objects.create(
                user=self.request.user,
                author=user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        Subscription.objects.get(user=self.request.user,
                                 author=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # except Exception as error:
    #     return Response({'errors': str(error)},
    #                     status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [IsAuthenticated]


class IngredientViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientModelSerializer
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]


class DjoserCustomAndSubscriptionViewSet(UserViewSet):

    @action(methods=['GET'], detail=False,
            serializer_class=UserSubSerializer,
            permission_classes=[IsAuthenticated])
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
            serializer_class=UserSubSerializer,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author_id = self.kwargs.get('id')
        author = get_object_or_404(User, pk=author_id)
        user = self.request.user
        serializer = UserSubPostSerializer(data=request.data)
        serializer.validate_self_subscription(user, author)
        serializer.is_valid(raise_exception=True)
        if self.request.method == 'POST':
            serializer_data = serializer.save(user, author)
            return Response(serializer_data,
                            status=status.HTTP_201_CREATED)
        serializer.destroy(user, author)
        return Response(status=status.HTTP_204_NO_CONTENT)
