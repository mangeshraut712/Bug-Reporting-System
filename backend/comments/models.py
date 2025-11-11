"""
Models for comments app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    """
    Comment model for issue discussions.
    """
    content = models.TextField()
    issue = models.ForeignKey('issues.Issue', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['issue']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author} on {self.issue}'
