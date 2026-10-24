"""
Serializers for comments app.
"""
from rest_framework import serializers

from accounts.models import user_display_name
from bug_tracking.validation import MAX_COMMENT_LENGTH

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'issue', 'author', 'author_name', 'author_email',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A comment stays on the issue it was written for.
        if getattr(self, 'instance', None) is not None:
            self.fields['issue'].read_only = True

    def get_author_name(self, obj):
        """Display name of the author, or null when that user was deleted."""
        return user_display_name(obj.author)

    def get_author_email(self, obj):
        """Email of the author, or null when that user was deleted."""
        if obj.author_id is None:
            return None
        return obj.author.email

    def validate_content(self, value):
        """Require comment text and cap its size."""
        content = value.strip()
        if not content:
            raise serializers.ValidationError('Comment content cannot be blank.')
        if len(content) > MAX_COMMENT_LENGTH:
            raise serializers.ValidationError('Comment content is too long.')
        return content
