"""
Models for issues app.
"""
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

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
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['project']),
            models.Index(fields=['reporter']),
            models.Index(fields=['assignee']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(status__in=['open', 'in_progress', 'closed']),
                name='issue_status_valid',
            ),
            models.CheckConstraint(
                condition=models.Q(priority__in=['low', 'medium', 'high', 'critical']),
                name='issue_priority_valid',
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Reject status and priority values outside the supported choices."""
        errors = {}
        valid_status = {choice for choice, _label in self.STATUS_CHOICES}
        valid_priority = {choice for choice, _label in self.PRIORITY_CHOICES}
        if self.status not in valid_status:
            errors['status'] = (
                f'Invalid status. Must be one of: {", ".join(sorted(valid_status))}.'
            )
        if self.priority not in valid_priority:
            errors['priority'] = (
                f'Invalid priority. Must be one of: {", ".join(sorted(valid_priority))}.'
            )
        if errors:
            raise ValidationError(errors)
