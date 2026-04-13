from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, health

router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("health/", health),
    path("api/", include(router.urls)),
]
