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
    ThrottledPasswordResetConfirmView,
    ThrottledPasswordResetView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', ThrottledLoginView.as_view(), name='login'),
    path('logout/', SafeLogoutView.as_view(), name='logout'),
    path('token/refresh/', PublicTokenRefreshView.as_view(), name='token-refresh'),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    # Registered before dj-rest-auth so these throttled views win.
    path('password/reset/', ThrottledPasswordResetView.as_view(), name='password-reset'),
    path(
        'password/reset/confirm/',
        ThrottledPasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
]
