from rest_framework import serializers

from .models import Posts


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posts
        fields = [
            "id",
            "title",
            "content",
            "author_id",
            "author_username",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author_id",
            "author_username",
            "created_at",
            "updated_at",
        ]