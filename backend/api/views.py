from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from users.models import User
from core.models import Recipe, Tag, Ingredient, Follow
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer, \
    SubscriptionSerializer, UserSubSerializer

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
        f = self.request.user.follower.all()
        users = Follow.objects.filter(user=self.request.user).values_list('id')
        followings = User.objects.exclude(follower__in=users)
        print(f, ':', users)
        print(followings)
        return followings


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer



