"""
Serializers for comments app.
"""
from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'content', 'issue', 'author', 'author_name', 'author_email', 'created_at', 'updated_at')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
