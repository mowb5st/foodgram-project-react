from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import TokenDestroyView
from rest_framework import status
from rest_framework.authtoken import views
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins

from core.models import Recipe, Tag, Ingredient, Subscription, Favorite, \
    ShoppingCart
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer, \
    UserSubSerializer, FavoriteSerializer, \
    LoginSerializer, \
    RecipeCreateSerializer, TagSerializer, IngredientModelSerializer

User = get_user_model()


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_fields = ('id',)
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.action == ('list' or 'retrieve'):
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(methods=['GET'], detail=False, url_path='download_shopping_cart',
            url_name='download_shopping_cart')
    def download_shopping_cart(self, request, *args, **kwargs):
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

    @action(methods=['POST', 'DELETE'], detail=True,
            url_path='shopping_cart', url_name='shopping_carts')
    def shopping_cart(self, request, *args, **kwargs):
        try:
            if self.request.method == 'POST':
                recipe_id = self.kwargs.get('id')
                recipe = Recipe.objects.get(pk=recipe_id)
                user = User.objects.get(username=self.request.user)
                ShoppingCart.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            # else only one available method DELETE
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            ShoppingCart.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True, url_path='favorite',
            url_name='favorites')
    def favorite(self, request, *args, **kwargs):
        try:
            if self.request.method == 'POST':
                recipe_id = self.kwargs.get('id')
                recipe = Recipe.objects.get(pk=recipe_id)
                user = User.objects.get(username=self.request.user)
                Favorite.objects.create(user=user, recipe=recipe)
                serializer = FavoriteSerializer(recipe)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            # else only one available method DELETE
            recipe_id = self.kwargs.get('id')
            recipe = Recipe.objects.get(pk=recipe_id)
            user = User.objects.get(username=self.request.user)
            Favorite.objects.get(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({'errors': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


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
