from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from core.models import Recipe, Tag, Ingredient, Follow, Favorite
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer, \
    SubscriptionSerializer, UserSubSerializer, FavoriteSerializer, \
    RecipeSubSerializer, LoginSerializer, LogoutSerializer
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.permissions import AllowAny, IsAuthenticated

USERNAME_ME = 'me'


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet
                  ):
    queryset = User.objects.all()
    lookup_field = 'id'
    permission_classes = IsAuthenticated

    def get_object(self):
        if self.kwargs.get('id') == USERNAME_ME:
            return self.request.user
        return super().get_object()

    def get_serializer_class(self):
        if self.kwargs.get('username') == USERNAME_ME:
            return MeUserSerializer
        return UserSerializer


class SubscriptionViewSet(ModelViewSet):
    # queryset = User.objects.filter(is_subscribed=True)
    serializer_class = UserSubSerializer

    def get_queryset(self):
        # f = User.objects.filter(follower=self.request.user)
        # f = User.objects.filter(following=self.request.user)
        # f = self.request.user.following.all()
        # f = self.request.user.follower.all()
        users = Follow.objects.filter(user=self.request.user).values_list('id')
        followings = User.objects.exclude(follower__in=users)
        return followings


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class FavoriteViewSet(ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        recipe_id = self.kwargs.get('recipe_id')
        queryset = Recipe.objects.filter(id=recipe_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

    def perform_create(self, serializer):
        user = self.request.user
        recipe_id = self.kwargs.get('recipe_id')
        serializer.save(user=user, recipe=recipe_id)
        obj = Recipe.objects.get(id=recipe_id)
        serializer = self.get_serializer(obj)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)


class LoginViewSet(ModelViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        # print(request.data['email'])
        user = User.objects.filter(email=request.data['email'])
        token = RefreshToken.for_user(user)
        return Response({'token': token}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer = LoginSerializer
    #
    # def post(self, request, *args, **kwargs):
    #     serializer = LoginSerializer(data=request.data)
    #     try:
    #         serializer.is_valid(raise_exception=True)
    #     except TokenError as e:
    #         raise InvalidToken(e.args[0])
    #     return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


class LogoutView(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer
    # www_authenticate_realm = 'api'
    # def get_authenticate_header(self, request):
    #     return '{0} realm="{1}"'.format(
    #         AUTH_HEADER_TYPES[0],
    #         self.www_authenticate_realm,
    #     )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

