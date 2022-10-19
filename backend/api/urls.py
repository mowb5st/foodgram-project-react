from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, RecipeViewSet, SubscriptionViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('users/subscriptions', SubscriptionViewSet,
                basename='subscriptions')
router.register('users', UserViewSet, basename='users')
router.register('recipe', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls))
]
