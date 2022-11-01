from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, SubscriptionViewSet, \
    LoginViewSet, LogoutViewSet, TagViewSet, \
    IngredientViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
# router.register(r'users/(?P<id>\d+)/subscribe', SubscriptionViewSet, basename='subscribe')
router.register('users', SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', LoginViewSet.as_view()),
    path('auth/token/logout/', LogoutViewSet.as_view()),
]
