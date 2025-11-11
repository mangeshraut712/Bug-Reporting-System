"""
Admin configuration for issues app.
"""
from django.contrib import admin
from .models import Issue


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """
    Admin interface for Issue model.
    """
    list_display = ('title', 'status', 'priority', 'project', 'reporter', 'assignee', 'created_at')
    list_filter = ('status', 'priority', 'created_at', 'project')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Issue Details', {
            'fields': ('title', 'description', 'status', 'priority')
        }),
        ('Relations', {
            'fields': ('project', 'reporter', 'assignee')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
