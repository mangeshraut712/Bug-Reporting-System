"""
Models for projects app.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    """
    Project model for organizing issues.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return self.name
