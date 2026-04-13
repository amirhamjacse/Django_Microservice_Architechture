from rest_framework import serializers

from .models import Comments


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = [
            "id",
            "post_id",
            "author_id",
            "author_username",
            "body",
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