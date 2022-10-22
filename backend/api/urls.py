from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, \
    TokenRefreshView
from django.views.decorators.csrf import csrf_exempt

from .views import UserViewSet, RecipeViewSet, SubscriptionViewSet, \
    FavoriteViewSet, LoginViewSet, LoginView, LogoutView

app_name = 'api'

router = routers.DefaultRouter()
# router.register('auth/token/login', LoginViewSet, basename='logins')
# router.register('auth/token/logout', LogoutViewSet, basename='logouts')

# router.register('users', include('djoser.urls'), basename='users')
# router.register('users/subscriptions', SubscriptionViewSet,
#                 basename='subscriptions')
# router.register('users', UserViewSet, basename='users')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
                basename='favorites')
router.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', LoginView.as_view(), name='logins'),
    path('auth/token/logout/', csrf_exempt(LogoutView), name='logouts'),
    # path('auth/', include('djoser.urls.jwt')),
]
