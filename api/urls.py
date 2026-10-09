from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet, PostViewSet, UserViewSet

router = DefaultRouter()
router.register("posts", PostViewSet, basename="api-post")
router.register("users", UserViewSet, basename="api-user")
router.register("notifications", NotificationViewSet, basename="api-notification")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls")),
]
