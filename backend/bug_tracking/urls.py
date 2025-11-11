"""
URL configuration for bug_tracking project.
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Routes
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/register/', include('accounts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/issues/', include('issues.urls')),
    path('api/comments/', include('comments.urls')),
]
