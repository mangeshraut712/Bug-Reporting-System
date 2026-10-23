"""
Views for accounts app.
"""
from dj_rest_auth.views import LoginView, LogoutView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import RegisterSerializer, UserSerializer
from .throttles import LoginRateThrottle, RefreshRateThrottle, RegisterRateThrottle


class RegisterView(APIView):
    """Create a user account."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):
        """Register a new user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'message': 'User registered successfully', 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class ThrottledLoginView(LoginView):
    """Email and password login that returns JWTs and does not open a session."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [LoginRateThrottle]


class SafeLogoutView(LogoutView):
    """Blacklist a refresh token even when the access token has already expired."""

    permission_classes = [AllowAny]
    authentication_classes = []


class PublicTokenRefreshView(TokenRefreshView):
    """Issue a new access token from a refresh token."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [RefreshRateThrottle]


class CurrentUserView(APIView):
    """Return the signed-in user and do not list other accounts."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current user information."""
        return Response(UserSerializer(request.user).data)
