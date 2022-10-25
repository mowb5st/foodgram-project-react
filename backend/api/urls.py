from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView
from django.views.decorators.csrf import csrf_exempt

from .views import UserViewSet, RecipeViewSet, SubscriptionViewSet, \
    FavoriteViewSet, LoginViewSet, LogoutViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
                basename='favorites')
router.register(r'recipes', RecipeViewSet, basename='recipe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', LoginViewSet.as_view()),
    path('auth/token/logout/', LogoutViewSet.as_view()),
]
