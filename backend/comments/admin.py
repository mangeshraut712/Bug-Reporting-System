"""
Admin configuration for comments app.
"""
from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model.
    """
    list_display = ('author', 'issue', 'created_at')
    list_filter = ('created_at', 'issue')
    search_fields = ('content', 'author__email')
    readonly_fields = ('created_at', 'updated_at')
