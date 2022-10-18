from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from users.models import User
from core.models import Recipe, Tag, Ingredient
from .serializers import UserSerializer, MeUserSerializer, RecipeSerializer


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


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer



