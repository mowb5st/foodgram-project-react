from django.urls import include, path
from rest_framework import routers

from .views import RecipeViewSet, SubscriptionViewSet, \
    FavoriteViewSet, LoginViewSet, LogoutViewSet, TagViewSet, \
    IngredientViewSet, ShoppingCartViewSet

app_name = 'api'

router = routers.DefaultRouter()
# router.register(r'recipes/(?P<id>\d+)/favorite', FavoriteViewSet,
#                 basename='favorites')
# router.register(r'recipes/(?P<id>\d+)/shopping_cart', ShoppingCartViewSet,
#                 basename='shopping_carts')
# router.register('recipes/download_shopping_cart', ShoppingCartViewSet,
#                 basename='download_shopping_cart')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register(r'users/(?P<id>\d+)/subscribe', SubscriptionViewSet, basename='subscribe')
router.register('users/subscriptions', SubscriptionViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', LoginViewSet.as_view()),
    path('auth/token/logout/', LogoutViewSet.as_view()),
]
