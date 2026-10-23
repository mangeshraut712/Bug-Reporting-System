"""
URL configuration for accounts app.
"""
from django.urls import path

from .views import (
    CurrentUserView,
    PublicTokenRefreshView,
    RegisterView,
    SafeLogoutView,
    ThrottledLoginView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', ThrottledLoginView.as_view(), name='login'),
    path('logout/', SafeLogoutView.as_view(), name='logout'),
    path('token/refresh/', PublicTokenRefreshView.as_view(), name='token-refresh'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
]
