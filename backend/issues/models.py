"""
Models for issues app.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class Issue(models.Model):
    """
    Issue model for tracking bugs and tasks.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='issues')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_issues')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['project']),
            models.Index(fields=['reporter']),
            models.Index(fields=['assignee']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """
        Validate status transitions and assignee.
        """
        if self.assignee and not isinstance(self.assignee, User):
            raise ValidationError({'assignee': 'Invalid assignee.'})
