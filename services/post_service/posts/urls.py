from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, health

router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")

urlpatterns = [
    path("health/", health),
    path("api/", include(router.urls)),
]
