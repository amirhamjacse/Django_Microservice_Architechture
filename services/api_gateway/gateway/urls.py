from django.urls import path
from .views import feed, health

urlpatterns = [
    path("health/", health),
    path("api/feed/", feed),
]
