from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import UserViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [

] + router.urls