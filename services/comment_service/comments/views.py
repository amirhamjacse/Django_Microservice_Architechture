import requests
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Comments
from .serializers import CommentSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def health(_request):
    return Response({"service": "comment-service", "status": "ok"})


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comments.objects.all().order_by("-created_at")
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset

    def perform_create(self, serializer):
        user_id = getattr(self.request.user, "id", None)
        if not user_id:
            raise PermissionError("Missing authenticated user")

        post_id = serializer.validated_data.get("post_id")

        user_response = requests.get(
            f"{settings.USER_SERVICE_URL}/api/users/{user_id}/",
            timeout=5,
        )
        if user_response.status_code != status.HTTP_200_OK:
            raise ValueError("Author does not exist in user-service")

        post_response = requests.get(
            f"{settings.POST_SERVICE_URL}/api/posts/{post_id}/",
            timeout=5,
        )
        if post_response.status_code != status.HTTP_200_OK:
            raise ValueError("Post does not exist in post-service")

        serializer.save(
            author_id=user_id,
            author_username=user_response.json().get("username", ""),
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except PermissionError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException:
            return Response(
                {"detail": "user-service or post-service unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author_id != getattr(request.user, "id", None):
            return Response(
                {"detail": "You can only modify your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author_id != getattr(request.user, "id", None):
            return Response(
                {"detail": "You can only modify your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author_id != getattr(request.user, "id", None):
            return Response(
                {"detail": "You can only delete your own comments."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)
