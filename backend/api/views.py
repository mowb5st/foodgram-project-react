from django.shortcuts import get_object_or_404
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from users.models import User
from core.models import Recipe, Tag, Ingredient, Follow, Favorite
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer, \
    SubscriptionSerializer, UserSubSerializer, FavoriteSerializer, \
    RecipeSubSerializer
from rest_framework.response import Response

USERNAME_ME = 'me'


class UserViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet
                  ):
    queryset = User.objects.all()
    lookup_field = 'id'

    # serializer_class = UserSerializer

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
    # queryset = Recipe.objects.all()
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        # queryset = get_object_or_404(Recipe, id=self.kwargs.get('recipe_id'))
        # print(queryset)
        queryset = Recipe.objects.filter(id=self.kwargs.get('recipe_id'))
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        recipe = self.kwargs.get('recipe_id')
        obj = Recipe.objects.filter(id=recipe)
        # print(user, ':', recipe)
        # Favorite.objects.create(user=user, recipe__id=recipe)
        serializer.save(user=user, recipe=recipe, instance=obj)
        serializer = RecipeSubSerializer(instance=obj, many=True)
        super(FavoriteViewSet, self).list(self.request)
        # return Response(serializer.data)
